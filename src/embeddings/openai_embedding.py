from typing import List

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from src.embeddings.base import BaseEmbedding


class OpenAIEmbedding(BaseEmbedding):
    def __init__(
        self, model: str, api_key: str, base_url: str, dimension: int
    ):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.dimension = dimension
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def embed_text(self, text: str) -> List[float]:
        """
        嵌入单个文本

        :param text: 要嵌入的文本
        :return: 嵌入后的向量
        """
        return self.embed_batch([text])[0]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量嵌入文本

        :param texts: 要嵌入的文本列表
        :return: 嵌入后的向量列表
        """
        params = {
            "model": self.model,
            "input": texts,
        }
        # 判断是否指定了维度
        if self.dimension:
            params["dimensions"] = self.dimension
        # 发送请求
        resp = self.client.embeddings.create(**params)
        # 提取向量
        embeddings = [item.embedding for item in resp.data]
        return embeddings

    def get_embedding_dim(self) -> int:
        """
        获取嵌入维度

        :return: 嵌入维度
        """
        return self.dimension

    def get_embedding_name(self) -> str:
        """
        获取嵌入名称

        :return: 模型名称
        """
        return self.model
