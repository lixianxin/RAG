# 机器学习基础

## 1. 机器学习概述

机器学习（Machine Learning, ML）是人工智能的一个分支，通过算法让计算机从数据中学习规律，并对新数据做出预测或决策，而无需明确编程。

### 1.1 学习范式

| 类型 | 说明 | 典型算法 |
|------|------|----------|
| 监督学习 | 有标签数据 | 线性回归、SVM、神经网络 |
| 无监督学习 | 无标签数据 | K-Means、PCA、自编码器 |
| 半监督学习 | 少量标签 + 大量无标签 | 标签传播 |
| 强化学习 | 通过奖励学习 | Q-Learning、PPO |

### 1.2 基本术语

- **特征（Feature）**：输入变量 $x$
- **标签（Label）**：预测目标 $y$
- **样本（Sample）**：一条数据 $(x, y)$
- **数据集（Dataset）**：样本集合
- **模型（Model）**：学习到的映射 $f: x \to y$
- **损失函数（Loss）**：衡量预测与真实差异
- **训练（Training）**：通过数据调整参数
- **推理（Inference）**：用训练好的模型预测

## 2. 监督学习

### 2.1 线性回归

预测连续值，模型形式：

$$\hat{y} = w_1 x_1 + w_2 x_2 + \cdots + w_n x_n + b$$

损失函数（MSE）：

$$L = \frac{1}{N}\sum_{i=1}^{N}(y_i - \hat{y}_i)^2$$

```python
import numpy as np
from sklearn.linear_model import LinearRegression

# 生成数据
X = np.random.rand(100, 1) * 10
y = 2 * X + 1 + np.random.randn(100, 1)

# 训练
model = LinearRegression()
model.fit(X, y)
print(f"w={model.coef_}, b={model.intercept_}")
```

### 2.2 逻辑回归

二分类任务，输出概率：

$$p = \sigma(w^T x + b) = \frac{1}{1 + e^{-(w^T x + b)}}$$

```python
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification

X, y = make_classification(n_samples=1000, n_features=10)
model = LogisticRegression()
model.fit(X, y)
print(f"准确率: {model.score(X, y):.4f}")
```

### 2.3 决策树

基于特征进行递归划分：

```python
from sklearn.tree import DecisionTreeClassifier

model = DecisionTreeClassifier(max_depth=5)
model.fit(X_train, y_train)
```

**优点**：可解释性强、无需特征缩放
**缺点**：容易过拟合

### 2.4 随机森林

集成多个决策树：

```python
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42
)
model.fit(X_train, y_train)
```

### 2.5 支持向量机

寻找最大间隔超平面：

```python
from sklearn.svm import SVC

model = SVC(kernel='rbf', C=1.0)
model.fit(X_train, y_train)
```

常用核函数：
- **线性核**：$K(x, y) = x^T y$
- **多项式核**：$K(x, y) = (x^T y + r)^d$
- **RBF 核**：$K(x, y) = e^{-\gamma \|x-y\|^2}$

## 3. 无监督学习

### 3.1 K-Means 聚类

```python
from sklearn.cluster import KMeans

kmeans = KMeans(n_clusters=3, random_state=42)
labels = kmeans.fit_predict(X)

# 选择 K：肘部法则
inertias = []
for k in range(1, 11):
    km = KMeans(n_clusters=k).fit(X)
    inertias.append(km.inertia_)
```

### 3.2 PCA 降维

```python
from sklearn.decomposition import PCA

pca = PCA(n_components=2)
X_reduced = pca.fit_transform(X)
print(f"方差解释率: {pca.explained_variance_ratio_}")
```

### 3.3 DBSCAN

基于密度的聚类，可发现任意形状簇：

```python
from sklearn.cluster import DBSCAN

dbscan = DBSCAN(eps=0.5, min_samples=5)
labels = dbscan.fit_predict(X)
```

## 4. 神经网络

### 4.1 基本结构

```
输入层 → 隐藏层（多个）→ 输出层
```

每层计算：

$$a^{(l)} = \sigma(W^{(l)} a^{(l-1)} + b^{(l)})$$

### 4.2 激活函数

| 函数 | 公式 | 适用场景 |
|------|------|----------|
| Sigmoid | $\frac{1}{1+e^{-x}}$ | 二分类输出 |
| Tanh | $\frac{e^x - e^{-x}}{e^x + e^{-x}}$ | 隐藏层 |
| ReLU | $\max(0, x)$ | 隐藏层（默认） |
| Leaky ReLU | $\max(0.01x, x)$ | 解决 ReLU 死亡 |
| Softmax | $\frac{e^{x_i}}{\sum e^{x_j}}$ | 多分类输出 |

### 4.3 反向传播

通过链式法则计算梯度：

$$\frac{\partial L}{\partial W^{(l)}} = \frac{\partial L}{\partial a^{(l)}} \cdot \frac{\partial a^{(l)}}{\partial z^{(l)}} \cdot \frac{\partial z^{(l)}}{\partial W^{(l)}}$$

### 4.4 优化器

- **SGD**：基础随机梯度下降
- **Momentum**：加速收敛
- **Adam**：自适应学习率（最常用）
- **AdamW**：Adam + 权重衰减

```python
import torch.optim as optim

optimizer = optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
```

## 5. 模型评估

### 5.1 数据集划分

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
```

### 5.2 交叉验证

```python
from sklearn.model_selection import cross_val_score

scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
print(f"准确率: {scores.mean():.4f} ± {scores.std():.4f}")
```

### 5.3 分类指标

```python
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)

y_pred = model.predict(X_test)
print(f"准确率: {accuracy_score(y_test, y_pred):.4f}")
print(f"精确率: {precision_score(y_test, y_pred, average='weighted'):.4f}")
print(f"召回率: {recall_score(y_test, y_pred, average='weighted'):.4f}")
print(f"F1:    {f1_score(y_test, y_pred, average='weighted'):.4f}")
print(classification_report(y_test, y_pred))
```

**指标定义：**
- **准确率（Accuracy）**：$\frac{TP + TN}{Total}$
- **精确率（Precision）**：$\frac{TP}{TP + FP}$
- **召回率（Recall）**：$\frac{TP}{TP + FN}$
- **F1**：$\frac{2 \cdot P \cdot R}{P + R}$

### 5.4 回归指标

```python
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

print(f"MSE:  {mean_squared_error(y_test, y_pred):.4f}")
print(f"RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.4f}")
print(f"MAE:  {mean_absolute_error(y_test, y_pred):.4f}")
print(f"R²:   {r2_score(y_test, y_pred):.4f}")
```

## 6. 过拟合与欠拟合

### 6.1 识别

| 现象 | 训练误差 | 测试误差 | 原因 |
|------|----------|----------|------|
| 欠拟合 | 高 | 高 | 模型太简单 |
| 过拟合 | 低 | 高 | 模型太复杂 |
| 理想 | 低 | 低 | 平衡 |

### 6.2 解决过拟合

1. **增加数据**：最有效的方法
2. **正则化**：L1/L2 正则
3. **Dropout**：神经网络中随机丢弃神经元
4. **早停**：验证误差上升时停止训练
5. **简化模型**：减少层数、参数
6. **数据增强**：扩充训练数据

```python
# L2 正则
from sklearn.linear_model import Ridge
model = Ridge(alpha=1.0)

# Dropout
import torch.nn as nn
class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(100, 50),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(50, 10),
        )
```

## 7. 深度学习框架

### 7.1 PyTorch

```python
import torch
import torch.nn as nn
import torch.optim as optim

class MLP(nn.Module):
    def __init__(self, in_dim, hidden_dim, out_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, out_dim),
        )
    
    def forward(self, x):
        return self.net(x)

model = MLP(784, 128, 10)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=1e-3)

# 训练循环
for epoch in range(10):
    for X_batch, y_batch in train_loader:
        optimizer.zero_grad()
        output = model(X_batch)
        loss = criterion(output, y_batch)
        loss.backward()
        optimizer.step()
```

### 7.2 TensorFlow/Keras

```python
import tensorflow as tf
from tensorflow import keras

model = keras.Sequential([
    keras.layers.Dense(128, activation='relu', input_shape=(784,)),
    keras.layers.Dropout(0.5),
    keras.layers.Dense(10, activation='softmax'),
])

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy'],
)

model.fit(X_train, y_train, epochs=10, batch_size=32, validation_split=0.2)
```

## 8. 自然语言处理

### 8.1 文本预处理

```python
import re
import jieba

def preprocess(text: str) -> list[str]:
    # 去除特殊字符
    text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', ' ', text)
    # 英文小写
    text = text.lower()
    # 中文分词
    words = jieba.lcut(text)
    # 去停用词
    stopwords = {'的', '了', '是', '在'}
    words = [w for w in words if w not in stopwords and len(w) > 1]
    return words
```

### 8.2 词向量

| 方法 | 特点 |
|------|------|
| Word2Vec | 静态词向量，CBOW/Skip-gram |
| GloVe | 基于共现矩阵 |
| BERT | 动态上下文向量 |
| Sentence-BERT | 句向量 |

### 8.3 Transformer 架构

核心是 Self-Attention：

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

## 9. 实践建议

1. **从简单模型开始**：先跑通基线
2. **数据质量第一**：垃圾进垃圾出
3. **特征工程重要**：好的特征胜过复杂模型
4. **监控验证集**：及时发现过拟合
5. **集成学习**：结合多个模型提升效果
6. **可复现性**：固定随机种子、记录实验
