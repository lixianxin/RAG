# RAG 检索增强生成系统

## 1. RAG 概述

**RAG（Retrieval-Augmented Generation，检索增强生成）** 是一种结合了信息检索和文本生成的技术架构。它通过从外部知识库检索相关信息，再利用大语言模型（LLM）生成答案，有效解决了 LLM 知识过时和幻觉问题。

### 1.1 为什么需要 RAG

传统 LLM 存在以下问题：

- **知识截止**：训练数据有截止日期，无法回答最新信息
- **幻觉问题**：模型可能编造看似合理但错误的信息
- **领域知识不足**：对垂直领域知识掌握有限
- **无法访问私有数据**：不能直接查询企业内部文档
- **更新成本高**：重新训练模型代价巨大

RAG 通过引入外部知识库，让模型"看着资料回答"，显著缓解了上述问题。

### 1.2 RAG vs 微调

| 维度 | RAG | 微调 |
|------|-----|------|
| 知识更新 | 即时（更新知识库即可） | 缓慢（需重新训练） |
| 计算成本 | 低（仅推理） | 高（训练成本） |
| 数据隐私 | 知识库可控 | 训练数据可能泄露 |
| 适用场景 | 动态知识、事实问答 | 风格学习、能力提升 |
| 可解释性 | 高（可追溯来源） | 低 |

## 2. RAG 核心架构

RAG 系统通常包含三大核心模块：

### 2.1 索引阶段（Indexing）

将原始文档转化为可检索的向量索引：

```
原始文档 → 文档解析 → 文本分块 → 向量化 → 存入向量数据库
```

**关键步骤：**

1. **文档解析**：支持 PDF、Word、Markdown、HTML 等格式
2. **文本分块（Chunking）**：将长文档切分为合适大小的片段
3. **向量化（Embedding）**：将文本片段转为稠密向量
4. **存储索引**：将向量存入向量数据库（如 Chroma、Faiss、Pinecone）

### 2.2 检索阶段（Retrieval）

根据用户问题检索相关文档片段：

```
用户问题 → 向量化 → 向量相似度搜索 → 返回 Top-K 文档
```

**常用检索方法：**

- **稠密检索**：基于向量相似度（余弦相似度、点积）
- **稀疏检索**：基于关键词（BM25、TF-IDF）
- **混合检索**：结合稠密和稀疏检索优势

### 2.3 生成阶段（Generation）

将检索到的上下文与用户问题一起送入 LLM 生成答案：

```
用户问题 + 检索文档 → Prompt 模板 → LLM → 答案
```

## 3. 文本分块策略

分块质量直接影响检索效果，常用策略：

### 3.1 固定长度分块

按固定字符数切分，简单但可能破坏语义：

```python
def fixed_size_chunk(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks
```

### 3.2 按段落分块

保留段落语义完整性：

```python
def paragraph_chunk(text: str) -> list[str]:
    paragraphs = text.split('\n\n')
    return [p.strip() for p in paragraphs if p.strip()]
```

### 3.3 按句子分块

更细粒度，适合短文本：

```python
import re

def sentence_chunk(text: str, sentences_per_chunk: int = 3) -> list[str]:
    sentences = re.split(r'[。.!?！？]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    chunks = []
    for i in range(0, len(sentences), sentences_per_chunk):
        chunks.append('。'.join(sentences[i:i+sentences_per_chunk]))
    return chunks
```

### 3.4 递归分块

LangChain 的 RecursiveCharacterTextSplitter 采用此策略，按优先级依次尝试不同分隔符：

```
["\n\n", "\n", "。", "，", " ", ""]
```

### 3.5 分块参数选择

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| chunk_size | 300-1000 | 太小信息不全，太大稀释相关度 |
| overlap | 50-200 | 避免边界信息丢失 |
| separator | 优先段落 | 保留语义完整性 |

## 4. 向量化模型

### 4.1 常用 Embedding 模型

| 模型 | 维度 | 特点 |
|------|------|------|
| OpenAI text-embedding-ada-002 | 1536 | 通用性强，效果好 |
| BAAI/bge-large-zh-v1.5 | 1024 | 中文效果好，开源 |
| BAAI/bge-small-zh-v1.5 | 512 | 轻量级，速度快 |
| sentence-transformers/all-MiniLM-L6-v2 | 384 | 多语言，速度快 |
| Cohere embed-multilingual-v3 | 1024 | 多语言商用 |

### 4.2 选型建议

- **中文场景**：优先 BAAI/bge 系列
- **英文场景**：OpenAI 或 all-MiniLM
- **追求效果**：bge-large 或 OpenAI
- **追求速度**：bge-small 或 MiniLM
- **隐私要求**：本地部署 BGE 系列

## 5. 向量数据库对比

| 数据库 | 类型 | 特点 | 适用场景 |
|--------|------|------|----------|
| Chroma | 嵌入式 | 轻量易用 | 开发测试、小规模 |
| FAISS | 库 | 性能高 | 大规模、单机 |
| Pinecone | 云服务 | 全托管 | 生产环境、免运维 |
| Weaviate | 服务器 | 功能丰富 | 混合检索 |
| Milvus | 分布式 | 可扩展 | 大规模生产 |
| Qdrant | 服务器 | Rust实现 | 高性能需求 |

## 6. 高级 RAG 技术

### 6.1 查询改写（Query Rewriting）

将用户原始问题改写为更适合检索的形式：

```python
def rewrite_query(original_query: str, llm) -> str:
    prompt = f"""请将以下用户问题改写为更适合检索的关键词形式：
    
    原问题：{original_query}
    改写后："""
    return llm.generate(prompt)
```

### 6.2 重排序（Re-ranking）

先粗检索 Top-100，再用 Cross-Encoder 精排到 Top-10：

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder('BAAI/bge-reranker-base')
scores = reranker.predict([(query, doc) for doc in candidate_docs])
top_k_docs = [doc for _, doc in sorted(zip(scores, candidate_docs), reverse=True)][:10]
```

### 6.3 多路检索（Hybrid Search）

结合稠密和稀疏检索：

```python
def hybrid_search(query: str, top_k: int = 10):
    # 稠密检索
    dense_results = vector_search(query, top_k=50)
    # 稀疏检索（BM25）
    sparse_results = bm25_search(query, top_k=50)
    # 融合排序（RRF）
    return reciprocal_rank_fusion([dense_results, sparse_results], top_k=top_k)
```

### 6.4 上下文压缩

对检索到的长文档进行压缩摘要：

```python
def compress_context(docs: list[str], query: str, llm) -> str:
    combined = "\n".join(docs)
    prompt = f"""请从以下文档中提取与问题相关的关键信息，去除无关内容：
    
    问题：{query}
    文档：{combined}
    
    关键信息："""
    return llm.generate(prompt)
```

### 6.5 自我反思（Self-RAG）

让模型判断检索结果是否足够，是否需要再次检索：

```
1. 检索文档 → 生成初答
2. 评估答案是否完整
3. 不完整则改写查询再次检索
4. 重复直到满意或达到最大轮次
```

## 7. 评估指标

### 7.1 检索质量

- **Recall@K**：Top-K 中相关文档占比
- **Precision@K**：Top-K 中相关文档比例
- **MRR（Mean Reciprocal Rank）**：第一个相关文档位置的倒数
- **NDCG**：考虑排序的相关性得分

### 7.2 生成质量

- **Faithfulness（忠实度）**：答案是否基于检索文档
- **Answer Relevancy（答案相关性）**：答案是否切题
- **Context Precision（上下文精确率）**：检索上下文是否有用
- **Context Recall（上下文召回率）**：是否检索到所有必要信息

可使用 RAGAS 框架进行自动评估：

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision

result = evaluate(
    dataset,
    metrics=[faithfulness, answer_relevancy, context_precision],
)
```

## 8. 常见问题与优化

### 8.1 检索效果差

**原因：**
- 分块太大或太小
- Embedding 模型不匹配
- 查询与文档表述差异大

**优化：**
- 调整 chunk_size（300-500）
- 换用更适合领域的 Embedding 模型
- 使用查询改写
- 引入重排序

### 8.2 答案有幻觉

**原因：**
- 检索到无关文档
- LLM 忽略上下文
- Prompt 设计不当

**优化：**
- 提高 Top-K 质量
- 明确指示"仅基于上下文回答"
- 添加"如果上下文没有相关信息，请回答'不知道'"

### 8.3 响应慢

**原因：**
- Embedding 计算耗时
- 向量检索慢
- LLM 推理慢

**优化：**
- 缓存 Embedding 结果
- 使用 ANN 索引加速检索
- 启用流式输出
- 缓存常见问题答案

## 9. RAG 工程实践

### 9.1 数据准备

1. **数据清洗**：去除无关字符、统一格式
2. **元数据标注**：添加来源、时间、作者等
3. **质量筛选**：过滤低质量文档
4. **去重**：避免重复内容

### 9.2 索引构建

```python
def build_index(documents: list[dict]):
    for doc in documents:
        # 1. 解析
        parsed = parse_document(doc['path'])
        # 2. 分块
        chunks = chunk_text(parsed.text, chunk_size=500, overlap=50)
        # 3. 向量化
        embeddings = embedding_model.encode(chunks)
        # 4. 存储（带元数据）
        vector_store.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=[{
                'source': doc['path'],
                'title': doc['title'],
                'chunk_id': i
            } for i in range(len(chunks))]
        )
```

### 9.3 监控与维护

- **查询日志**：记录用户问题和检索结果
- **效果监控**：跟踪用户反馈（点赞/点踩）
- **索引更新**：支持增量添加新文档
- **A/B 测试**：对比不同参数效果

## 10. RAG 发展趋势

1. **多模态 RAG**：支持图片、表格、视频检索
2. **GraphRAG**：结合知识图谱，提升推理能力
3. **Agentic RAG**：让 Agent 自主决定检索策略
4. **Long Context**：利用长上下文 LLM 减少检索需求
5. **个性化 RAG**：结合用户画像个性化检索
