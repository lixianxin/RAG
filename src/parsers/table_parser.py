import pandas as pd
from typing import List, Dict


class TableProcessor:
    """表格处理类"""

    def markdown_to_dataframe(self, table_markdown: str) -> pd.DataFrame:
        """
        将markdown表格转化为DataFrame
        Args:
            table_markdown (str): markdown表格字符串
        Returns:
            pd.DataFrame: 转换后的DataFrame
        """
        lines = [
            line.strip() for line in table_markdown.strip().split("\n") if line.strip()
        ]
        if len(lines) < 2:
            return None
        # 解析表头
        headers = [cell.strip() for cell in lines[0].split("|")[1:-1]]
        # 跳过分割线
        data_lines = lines[2:] if len(lines) > 2 else []
        # 解析数据行
        data = []
        for line in data_lines:
            if "|" in line:
                cells = [cell.strip() for cell in line.split("|")[1:-1]]
                if len(cells) == len(headers):
                    data.append(cells)
        return pd.DataFrame(data, columns=headers)

    def dataframe_to_text(self, df: pd.DataFrame) -> str:
        """
        将DataFrame转换为文本描述
        Args:
            df (pd.DataFrame): 输入的DataFrame
        Returns:
            str: 表格的Markdown文本描述
        Args:
            table_markdown (str): markdown表格字符串
        Returns:
            str: 表格的文本描述
        """
        if df.empty:
            return ""
        # 生成表格内容
        parts = ["表格内存"]
        parts.append("|".join(df.columns))
        for _, row in df.iterrows():
            parts.append("|".join(row))
        return "\n".join(parts)

    def table_to_text(self, table_markdown: str) -> str:
        """
        将markdown表格转换为文本描述
        Args:
            table_markdown (str): markdown表格字符串
        Returns:
            str: 表格的文本描述
        """
        df = self.markdown_to_dataframe(table_markdown)
        if df is None:
            return ""

        return self.dataframe_to_text(df)

    def merge_table(self, tables: List[dict]) -> List[dict]:
        """
        合并多个表格
        Args:
            tables (List[dict]): 多个表格的字典列表
        Returns:
            List[dict]: 合并后的表格字典列表
        """
        if len(tables) <= 1:
            return tables
        mergered = [tables[0]]

        for i in range(1, len(tables)):
            curr = tables[i]
            last = mergered[-1]
            # 判断是否需要合并
            should_merge = (
                curr.get("cols") == last.get("cols")
                and curr.get("page") == last.get("page") + 1
            )
            if should_merge:
                last["markdown"] += "\n" + curr["markdown"]
                if "row" in curr and "row" in last:
                    last["rows"] += curr["rows"]
            else:
                mergered.append(curr)
        return mergered

    def extract_key_valule(self, table_text: str) -> Dict[str, str]:
        """
        从表格文本中提取键值对
        Args:
            table_text (str): markdown表格字符串
        Returns:
            Dict[str, str]: 提取的键值对字典
        """
        df = self.markdown_to_dataframe(table_text)
        if df is None or len(df.columns) < 2:
            return {}

        result = {}
        for _, row in df.iterrows():
            key = str(row.iloc[0].strip())
            value = str(row.iloc[1].strip())
            if key:
                result[key] = value
        return result
