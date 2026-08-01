from functools import lru_cache
import os
import threading

from fastapi import HTTPException

from src.database.document_store import DocumentStore
from src.retrieval.search_service import SearchService, CachedSearchService
from src.embeddings.local_embedding import LocalEmbedding
from src.api.config import settings
from src.llm.llm import LLM

# 缓存实例，避免每次请求重复创建
_embedding_model = None
_embedding_lock = threading.Lock()
_llm_cache: dict[str, LLM] = {}
_llm_lock = threading.Lock()
_store_cache: dict[str, DocumentStore] = {}
_store_lock = threading.Lock()


def get_embedding_model():
    """获取embedding模型实例（单例，线程安全）"""
    global _embedding_model
    if _embedding_model is None:
        with _embedding_lock:
            if _embedding_model is None:  # double-check
                model = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5")
                device = os.getenv("EMBEDDING_DEVICE", "cpu")
                _embedding_model = LocalEmbedding(model_name=model, device=device)
    return _embedding_model


def get_search_service(collection_name: str):
    """获取检索服务实例（按 collection_name 缓存）"""
    if collection_name not in _store_cache:
        with _store_lock:
            if collection_name not in _store_cache:  # double-check
                embedding_model = get_embedding_model()
                store = DocumentStore(
                    embedding_model=embedding_model,
                    collection_name=collection_name,
                )
                _store_cache[collection_name] = store

    store = _store_cache[collection_name]
    search_service = SearchService(document_store=store)

    # 缓存检索
    enable_cache = os.getenv("ENABLE_SEARCH_CACHE", "")
    if enable_cache and enable_cache.lower() in ("1", "true", "yes"):
        # CachedSearchService 内部自带缓存，直接包装即可
        if not hasattr(store, "_cached_service"):
            store._cached_service = CachedSearchService(search_service=search_service)
        return store._cached_service

    return search_service


def get_llm(model: str):
    """获取LLM实例（按 model 缓存，避免重复创建 OpenAI client）"""
    if model not in settings.LLM_PROVIDERS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持:{model}模型，目前支持的模型有:{list(settings.LLM_PROVIDERS.keys())}",
        )

    if model not in _llm_cache:
        with _llm_lock:
            if model not in _llm_cache:  # double-check
                config = settings.LLM_PROVIDERS.get(model)
                _llm_cache[model] = LLM(
                    model=config.get("default_model"),
                    api_key=config.get("api_key"),
                    base_url=config.get("base_url"),
                )

    return _llm_cache[model]


def preload():
    """启动时预加载模型（在后台线程中执行，不阻塞启动）"""
    import logging

    logger = logging.getLogger("uvicorn")

    def _preload():
        try:
            logger.info("[预加载] 正在加载 Embedding 模型...")
            get_embedding_model()
            logger.info("[预加载] Embedding 模型加载完成")
        except Exception as e:
            logger.warning(f"[预加载] Embedding 模型加载失败: {e}")

        try:
            logger.info("[预加载] 正在初始化 LLM 客户端...")
            default_model = settings.DEFAULT_MODEL
            get_llm(default_model)
            logger.info(f"[预加载] LLM 客户端初始化完成 ({default_model})")
        except Exception as e:
            logger.warning(f"[预加载] LLM 客户端初始化失败: {e}")

    thread = threading.Thread(target=_preload, daemon=True)
    thread.start()
