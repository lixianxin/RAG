from typing import List
import os
from pathlib import Path

from sentence_transformers import SentenceTransformer

from src.embeddings.base import BaseEmbedding


class LocalEmbedding(BaseEmbedding):
    def __init__(self, model_name: str, device: str = "cpu"):
        """
        初始化本地向量化模型

        :param model_name: 模型名称或路径
        :param device: 计算设备（如 "cuda" 或 "cpu"）
        """
        self.model_name = model_name
        self.device = device

        # 获取缓存目录
        cache_folder = os.getenv("EMBEDDING_CACHE_DIR", "./models/cache")
        Path(cache_folder).mkdir(parents=True, exist_ok=True)

        # 加载模型，CUDA不可用时自动降级到CPU
        try:
            self.model = SentenceTransformer(
                model_name,
                cache_folder=cache_folder,
                device=device,
            )
        except (AssertionError, Exception):
            if device != "cpu":
                self.device = "cpu"
                self.model = SentenceTransformer(
                    model_name,
                    cache_folder=cache_folder,
                    device="cpu",
                )
            else:
                raise

    def embed_text(self, text: str) -> List[float]:
        """
        对单条文本进行向量化

        :param text: 输入文本
        :return: 向量化后的文本向量
        """
        return self.model.encode(text, convert_to_tensor=True).tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        对批量文本进行向量化

        :param texts: 输入文本列表
        :return: 向量化后的文本向量列表
        """
        return self.model.encode(texts, convert_to_tensor=True).tolist()

    def get_embedding_name(self) -> str:
        return self.model_name

    def get_embedding_dim(self) -> int:
        return self.model.get_sentence_embedding_dimension()
