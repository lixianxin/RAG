from typing import List
import re

class TextCleaner():
    def __init__(self,custom_patterns:List[str]=None):
        '''
        Args:
            custom_patterns (list[str]): 自定义的正则模板
        '''
        # 常见的无意义模式
        self.patterns_to_remove = [
            r'^\s*\d+\s*$',        # 单独的页码
            r'^\s*[-=_]+\s*$',      # 分隔线
            r'^\s*第\s*\d+\s*页\s*$',   # 中文页码标记
            r'^\s*Page\s*\d+\s*$',    # 英文页码
            r'^\s*\d+\s*/\s*\d+\s*$',   # 页码格式：1/10
        ]

        #添加自定义模式
        if custom_patterns:
            self.patterns_to_remove.extend(custom_patterns)
        
    def clean(self,text:str) -> str:
        '''
        Args:
            text (str): 待处理的文本
        Returns:
            str: 处理后的文本
        '''
        lines=text.split('\n')
        cleaded_lines=[]

        for line in lines:
            if not line.strip():  # 跳过空白行
                continue
            #检查是否含有无意义模式
            is_noise=any(re.search(pattern,line) for pattern in self.patterns_to_remove)

            #如果不含有无意义模式，则添加到结果中
            if not is_noise:
                cleaded_lines.append(line)
        return '\n'.join(cleaded_lines)

    def normalize_whitespace(self,text:str) -> str:
        '''
        规范化文本中的空白字符
        -  合并多个空格
        -  合并多个换行
        -  去除行首行尾的空白字符
        Args:
            text (str): 待处理的文本
        Returns:
            str: 处理后的文本
        '''
        #去除多余的空格
        text=re.sub(r'\s+', ' ', text)
        #合并多个换行符
        text=re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        return text.strip()

    def remove_exstract_chars(self, text: str,chars: str=None) -> str:
        '''
        移除多余的特殊字符
        Args:
            text (str): 待处理的文本
            chars (str, optional): 需要移除的特殊字符. Defaults to None.
        return (str): 处理后的文本
        '''
        if chars is None: 
            chars = '\u200b\u200c\u200d\ufeff' # 零宽字符等
        return re.translate(text, str.maketrans('', '', chars))
    
    def full_clean(self, text: str) -> str:
        '''
        执行完整清理clean
        Args:
            text (str): 待处理的文本
        return (str): 处理后的文本
        '''
        text=self.clean(text)
        text=self.normalize_whitespace(text)
        text=self.remove_exstract_chars(text)
        return text