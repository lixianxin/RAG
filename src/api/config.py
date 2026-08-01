import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """API配置类"""

    # 文件上传配置
    MAX_FILE_SIZE = 1024 * 1024 * 50  # 50MB
    ALLOWED_EXTENSIONS = [".pdf", ".html", ".md", ".docx"]
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./data/uploads")

    # LLM配置
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "zhipu")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKEN = int(os.getenv("LLM_MAX_TOKEN", "2000"))

    # 检索配置
    SEARCH_TOP_K = int(os.getenv("SEARCH_TOP_K", "5"))

    # LLM提供商配置
    LLM_PROVIDERS = {
        "dashscope": {
            "default_model": os.getenv("DASHSCOPE_MODEL", "qwen-max"),
            "api_key": os.getenv("DASHSCOPE_API_KEY", ""),
            "base_url": os.getenv(
                "DASHSCOPE_BASE_URL",
                "https://dashscope.aliyuncs.com/compatible-mode/v1",
            ),
        },
        "zhipu": {
            "default_model": os.getenv("ZHIPU_MODEL", "glm-4-flash"),
            "api_key": os.getenv("ZHIPU_API_KEY", ""),
            "base_url": os.getenv(
                "ZHIPU_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"
            ),
        },
    }


# 全局配置对象
settings = Settings()
