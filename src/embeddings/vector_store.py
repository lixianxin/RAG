from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class Document:
    """文档对象"""

    id: str  # 文档ID
    content: str  # 文档内容
    metadata: Dict[str, Any]  # 元数据
    embedding: Optional[List[float]] = None  # 向量（可选）


@dataclass
class SearchResult:
    """检索结果"""

    document: Document  # 文档
    score: float  # 相似度分数
    metadata: Dict[str, Any]  # 额外元数据


class BaseVectorStore(ABC):
    """基础向量存储类"""

    @abstractmethod
    def add_documents(
        self, documents: List[Document], embeddings: List[List[float]]
    ) -> List[str]:
        """
        添加文档到存储
        :param documents: 文档列表
        :param embeddings: 对应的向量列表
        :return: 文档ID列表
        """

    @abstractmethod
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        filter: Dict[str, Any] = None,
    ) -> List[SearchResult]:
        """
        搜索向量存储
        :param query_embedding: 查询向量
        :param top_k: 返回的文档数量
        :param filter: 过滤条件
        :return: 检索结果列表
        """

    @abstractmethod
    def get_collection_stats(self) -> Dict[str, Any]:
        """获取 获取当前向量数据库中的集合统计信息
        :return: 统计信息字典
        """
        pass

    @abstractmethod
    def clear(self) -> bool:
        """
        清除向量存储
        :return: 是否成功
        """
        pass
