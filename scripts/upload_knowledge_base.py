"""
批量上传知识库文档到 RAG 系统

用法:
    python scripts/upload_knowledge_base.py                    # 交互模式
    python scripts/upload_knowledge_base.py --collection mykb  # 指定集合
    python scripts/upload_knowledge_base.py --yes              # 跳过确认
"""

import argparse
import os
import sys
from pathlib import Path
import time

import requests

# 后端地址
BACKEND_URL = "http://127.0.0.1:8000"
UPLOAD_API = f"{BACKEND_URL}/api/document/upload"

# 知识库目录
KB_DIR = Path(__file__).parent.parent / "knowledge_base"

# 默认集合名
DEFAULT_COLLECTION = "default"


def upload_file(file_path: Path, collection_name: str) -> dict:
    """上传单个文件到后端"""
    file_name = file_path.name
    print(f"\n[上传] {file_name} -> 集合 '{collection_name}'")

    with open(file_path, "rb") as f:
        files = {"file": (file_name, f, "application/octet-stream")}
        data = {"collection_name": collection_name}

        try:
            start = time.time()
            resp = requests.post(UPLOAD_API, files=files, data=data, timeout=300)
            elapsed = time.time() - start

            if resp.status_code == 200:
                result = resp.json()
                status = []
                if result.get("stored"):
                    status.append(f"已入库 {result.get('doc_count', 0)} 块")
                if result.get("duplicate"):
                    status.append("重复跳过")
                print(f"  [成功] {' | '.join(status)} (耗时 {elapsed:.1f}s)")
                return result
            else:
                print(f"  [失败] HTTP {resp.status_code}: {resp.text}")
                return {}
        except requests.exceptions.ConnectionError:
            print(f"  [错误] 无法连接后端 {BACKEND_URL}，请确认后端已启动")
            sys.exit(1)
        except Exception as e:
            print(f"  [错误] {e}")
            return {}


def main():
    parser = argparse.ArgumentParser(description="批量上传知识库文档")
    parser.add_argument("--collection", "-c", default=DEFAULT_COLLECTION,
                        help=f"集合名（默认: {DEFAULT_COLLECTION}）")
    parser.add_argument("--yes", "-y", action="store_true",
                        help="跳过确认，直接上传")
    args = parser.parse_args()
    collection = args.collection

    # 1. 检查后端是否在线
    print(f"检查后端: {BACKEND_URL}")
    try:
        r = requests.get(f"{BACKEND_URL}/api/health", timeout=5)
        if r.status_code == 200:
            print("  [OK] 后端在线")
        else:
            print(f"  [警告] 后端响应异常: {r.status_code}")
    except Exception:
        print(f"  [错误] 后端未启动，请先运行: uv run python src/api/main.py")
        sys.exit(1)

    # 2. 收集知识库文件
    if not KB_DIR.exists():
        print(f"  [错误] 知识库目录不存在: {KB_DIR}")
        sys.exit(1)

    supported_exts = {".md", ".markdown", ".pdf", ".docx", ".html", ".htm"}
    files = [
        f for f in KB_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in supported_exts
    ]

    if not files:
        print(f"  [警告] 知识库目录无支持的文件: {KB_DIR}")
        sys.exit(0)

    print(f"\n待上传文件 ({len(files)} 个):")
    for f in files:
        size_kb = f.stat().st_size / 1024
        print(f"  - {f.name} ({size_kb:.1f} KB)")

    # 3. 选择集合
    if not args.yes:
        print(f"\n默认集合: '{DEFAULT_COLLECTION}'")
        custom = input("输入自定义集合名（回车使用默认）: ").strip()
        collection = custom or DEFAULT_COLLECTION

    # 4. 开始上传
    print(f"\n{'='*50}")
    print(f"开始上传到集合 '{collection}'")
    print('='*50)

    success_count = 0
    for f in files:
        result = upload_file(f, collection)
        if result.get("success"):
            success_count += 1

    # 5. 汇总
    print(f"\n{'='*50}")
    print(f"上传完成: {success_count}/{len(files)} 成功")
    print(f"集合名: '{collection}'")
    print(f"\n现在可以在前端 http://localhost:3000 使用集合 '{collection}' 进行问答")
    print('='*50)


if __name__ == "__main__":
    main()
