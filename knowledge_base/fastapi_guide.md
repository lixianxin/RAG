# FastAPI 开发指南

## 1. FastAPI 简介

FastAPI 是一个现代、快速（高性能）的 Python Web 框架，基于标准 Python 类型提示构建。由 Sebastián Ramírez 于 2018 年创建。

### 1.1 核心特点

- **快速**：与 NodeJS、Go 性能相当
- **快速编码**：开发速度提升约 200%-300%
- **更少 Bug**：减少约 40% 人为错误
- **直观**：编辑器支持好，自动补全完善
- **简易**：易于使用和学习
- **简短**：代码重复最少
- **健壮**：生产就绪代码
- **基于标准**：完全兼容 OpenAPI、JSON Schema

### 1.2 技术栈

- **Starlette**：ASGI 框架，负责 Web 部分
- **Pydantic**：数据验证，负责数据部分
- **Uvicorn**：ASGI 服务器

## 2. 安装与第一个应用

### 2.1 安装

```bash
pip install fastapi uvicorn[standard]
```

### 2.2 Hello World

```python
from fastapi import FastAPI

app = FastAPI(title="我的API", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
```

### 2.3 启动

```bash
# 开发模式（热重载）
uvicorn main:app --reload --port 8000

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

访问 http://localhost:8000/docs 即可看到自动生成的 Swagger 文档。

## 3. 路径参数

### 3.1 基本用法

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}
```

### 3.2 类型转换与验证

FastAPI 自动进行类型转换和验证：

```python
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    # 如果传入非整数，自动返回 422 错误
    return {"item_id": item_id}
```

### 3.3 路径顺序

更具体的路径应放在前面：

```python
# 正确：先具体的，再通用的
@app.get("/users/me")
async def read_user_me():
    return {"user": "current user"}

@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}
```

## 4. 查询参数

### 4.1 基本查询参数

```python
@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

# 请求：/items/?skip=0&limit=20
```

### 4.2 可选参数

```python
from typing import Optional

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}
```

### 4.3 bool 类型转换

```python
@app.get("/items/")
async def read_items(feature: bool = False):
    return {"feature": feature}

# 以下都被转换为 True: true, 1, yes, on
```

## 5. 请求体

### 5.1 使用 Pydantic 模型

```python
from pydantic import BaseModel
from typing import Optional

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

@app.post("/items/")
async def create_item(item: Item):
    return item
```

### 5.2 嵌套模型

```python
class Image(BaseModel):
    url: str
    name: str

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    images: list[Image] = []

@app.post("/items/")
async def create_item(item: Item):
    return item
```

### 5.3 字段验证

```python
from pydantic import BaseModel, Field

class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    price: float = Field(..., gt=0, description="价格必须大于0")
    tags: list[str] = Field(default=[], max_items=10)
```

## 6. 依赖注入

FastAPI 提供强大的依赖注入系统：

### 6.1 基本依赖

```python
from fastapi import Depends

def common_parameters(q: Optional[str] = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/items/")
async def read_items(commons: dict = Depends(common_parameters)):
    return commons
```

### 6.2 类作为依赖

```python
class CommonQueryParams:
    def __init__(self, q: Optional[str] = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit

@app.get("/items/")
async def read_items(commons: CommonQueryParams = Depends()):
    return {"q": commons.q, "skip": commons.skip, "limit": commons.limit}
```

### 6.3 全局依赖

```python
app = FastAPI(dependencies=[Depends(verify_token)])

# 或针对路由
@app.get("/users/", dependencies=[Depends(verify_admin)])
async def read_users():
    return [...]
```

### 6.4 Yield 依赖

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/items/")
async def read_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

## 7. 安全与认证

### 7.1 OAuth2 密码模式

```python
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username = payload.get("sub")
    return username

@app.get("/users/me")
async def read_users_me(current_user: str = Depends(get_current_user)):
    return {"user": current_user}
```

## 8. 中间件

### 8.1 自定义中间件

```python
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### 8.2 CORS 中间件

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 允许的源
    allow_credentials=True,        # 允许携带 Cookie
    allow_methods=["*"],           # 允许的方法
    allow_headers=["*"],           # 允许的请求头
)
```

## 9. 异步与后台任务

### 9.1 异步路由

```python
import httpx

@app.get("/external/")
async def read_external():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
    return response.json()
```

### 9.2 后台任务

```python
from fastapi import BackgroundTasks

def write_log(message: str):
    with open("log.txt", "a") as f:
        f.write(message + "\n")

@app.post("/send-notification/")
async def send_notification(background_tasks: BackgroundTasks):
    background_tasks.add_task(write_log, "通知已发送")
    return {"message": "通知已加入队列"}
```

### 9.3 定时任务（依赖 APScheduler）

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job("interval", minutes=10)
async def cleanup_task():
    # 定期清理任务
    pass

@app.on_event("startup")
async def startup_event():
    scheduler.start()
```

## 10. 流式响应

### 10.1 StreamingResponse

```python
from fastapi.responses import StreamingResponse
import asyncio

async def generate():
    for i in range(10):
        yield f"data: 消息 {i}\n\n".encode()
        await asyncio.sleep(0.5)

@app.get("/stream")
async def stream():
    return StreamingResponse(generate(), media_type="text/event-stream")
```

### 10.2 LLM 流式输出

```python
@app.post("/chat/stream")
async def chat_stream(query: str):
    async def generate():
        async for chunk in llm.stream(query):
            yield chunk.encode()
    return StreamingResponse(generate(), media_type="text/plain")
```

## 11. 文件上传

### 11.1 单文件上传

```python
from fastapi import UploadFile, File

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    return {
        "filename": file.filename,
        "size": len(contents),
        "content_type": file.content_type,
    }
```

### 11.2 多文件上传

```python
@app.post("/uploads/")
async def upload_files(files: list[UploadFile] = File(...)):
    results = []
    for file in files:
        contents = await file.read()
        results.append({
            "filename": file.filename,
            "size": len(contents),
        })
    return results
```

### 11.3 大文件分块上传

```python
@app.post("/upload-large/")
async def upload_large(file: UploadFile = File(...)):
    save_path = f"./uploads/{file.filename}"
    with open(save_path, "wb") as f:
        while True:
            chunk = await file.read(1024 * 1024)  # 1MB chunks
            if not chunk:
                break
            f.write(chunk)
    return {"filename": file.filename}
```

## 12. 数据库集成

### 12.1 SQLAlchemy 集成

```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    email = Column(String, unique=True)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/")
def create_user(name: str, email: str, db: Session = Depends(get_db)):
    user = User(name=name, email=email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
```

## 13. 异常处理

### 13.1 自定义异常

```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id not in items:
        raise HTTPException(status_code=404, detail="Item not found")
    return items[item_id]
```

### 13.2 自定义异常处理器

```python
from fastapi import Request
from fastapi.responses import JSONResponse

class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name

@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={"message": f"Oops, {exc.name} did it again."},
    )
```

## 14. 测试

### 14.1 使用 TestClient

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_read_item():
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json() == {"item_id": 1}

def test_create_item():
    response = client.post(
        "/items/",
        json={"name": "Test", "price": 9.99},
    )
    assert response.status_code == 200
```

### 14.2 测试依赖覆盖

```python
def get_test_db():
    return TestSession()

app.dependency_overrides[get_db] = get_test_db

def test_read_users():
    response = client.get("/users/")
    assert response.status_code == 200

app.dependency_overrides = {}
```

## 15. 部署

### 15.1 Gunicorn + Uvicorn

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 15.2 Docker 部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 15.3 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 16. 最佳实践

1. **使用类型提示**：充分发挥 FastAPI 优势
2. **分层架构**：路由、服务、数据层分离
3. **配置管理**：使用环境变量和 Pydantic Settings
4. **异步优先**：IO 密集型操作用 async
5. **依赖注入**：复用逻辑，便于测试
6. **文档完善**：利用 docstring 和 response_model
7. **错误处理**：统一异常处理中间件
8. **性能监控**：集成日志和指标
