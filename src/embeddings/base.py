from typing import List
from abc import ABC, abstractmethod


class BaseEmbedding(ABC):
    """
    嵌入抽象类
    """

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """
        嵌入单个文本
        :param text: 要嵌入的文本
        :return: 嵌入后的向量
        """
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        嵌入多个文本
        :param texts: 要嵌入的文本列表
        :return: 嵌入后的向量列表
        """
        pass
    
    @abstractmethod
    def get_embedding_dim(self) -> int:
        """
        获取嵌入维度
        :return: 嵌入维度
        """
        pass

    @abstractmethod
    def get_embedding_name(self) -> str:
        """
        获取嵌入名称
        :return: 嵌入名称
        """
        pass