# Python 编程基础

## 1. Python 语言简介

Python 是一种高级、解释型、通用型编程语言，由 Guido van Rossum 于 1989 年圣诞节期间开发，1991 年正式发布。Python 强调代码可读性和简洁语法，特别适合快速开发。

### 1.1 主要特点

- **简洁易读**：使用缩进而非大括号表示代码块
- **解释型语言**：无需编译，可直接运行
- **动态类型**：变量类型在运行时确定
- **跨平台**：支持 Windows、Linux、macOS
- **丰富的标准库**：内置大量模块
- **面向对象**：支持面向过程和面向对象编程

## 2. 基本语法

### 2.1 变量与数据类型

Python 有以下基本数据类型：

```python
# 数字
integer_num = 42              # int
float_num = 3.14159           # float
complex_num = 1 + 2j          # complex

# 字符串
name = "Python"
multiline = """多行
字符串"""

# 布尔值
is_true = True
is_false = False

# 空值
nothing = None
```

### 2.2 容器类型

Python 提供四种内置容器类型：

1. **列表（List）**：有序、可变
```python
fruits = ['apple', 'banana', 'cherry']
fruits.append('date')
fruits[0] = 'apricot'
```

2. **元组（Tuple）**：有序、不可变
```python
point = (10, 20)
x, y = point  # 解包
```

3. **字典（Dict）**：键值对
```python
person = {'name': 'Alice', 'age': 30}
person['email'] = 'alice@example.com'
```

4. **集合（Set）**：无序、不重复
```python
unique_nums = {1, 2, 3, 3}  # 实际为 {1, 2, 3}
```

## 3. 控制流

### 3.1 条件语句

```python
score = 85

if score >= 90:
    grade = 'A'
elif score >= 80:
    grade = 'B'
elif score >= 70:
    grade = 'C'
else:
    grade = 'F'
```

### 3.2 循环

```python
# for 循环
for i in range(5):
    print(i)

# while 循环
count = 0
while count < 5:
    print(count)
    count += 1

# 列表推导式
squares = [x**2 for x in range(10)]
even_squares = [x**2 for x in range(10) if x % 2 == 0]
```

## 4. 函数

### 4.1 函数定义

```python
def greet(name: str, greeting: str = "Hello") -> str:
    """带类型注解的函数"""
    return f"{greeting}, {name}!"

# 调用
print(greet("Alice"))           # Hello, Alice!
print(greet("Bob", greeting="Hi"))  # Hi, Bob!
```

### 4.2 Lambda 函数

```python
# 匿名函数
square = lambda x: x ** 2
print(square(5))  # 25

# 常用于排序
students = [('Alice', 85), ('Bob', 92), ('Charlie', 78)]
students.sort(key=lambda x: x[1], reverse=True)
```

### 4.3 装饰器

装饰器是修改函数行为的强大工具：

```python
def timing_decorator(func):
    import time
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 执行耗时: {end - start:.4f}秒")
        return result
    return wrapper

@timing_decorator
def slow_function():
    import time
    time.sleep(1)
    print("完成")
```

## 5. 面向对象编程

### 5.1 类与对象

```python
class Animal:
    """基类"""
    
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age
    
    def speak(self) -> str:
        raise NotImplementedError("子类必须实现此方法")
    
    def __str__(self):
        return f"{self.name} ({self.age}岁)"


class Dog(Animal):
    """子类"""
    
    def __init__(self, name: str, age: int, breed: str):
        super().__init__(name, age)
        self.breed = breed
    
    def speak(self) -> str:
        return f"{self.name}说: 汪汪！"


# 使用
dog = Dog("旺财", 3, "金毛")
print(dog.speak())  # 旺财说: 汪汪！
```

### 5.2 魔术方法

```python
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)
    
    def __repr__(self):
        return f"Vector({self.x}, {self.y})"
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

v1 = Vector(1, 2)
v2 = Vector(3, 4)
print(v1 + v2)  # Vector(4, 6)
```

## 6. 异常处理

```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"除零错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")
else:
    print(f"结果: {result}")
finally:
    print("无论是否异常都会执行")
```

## 7. 异步编程

Python 3.5+ 引入了 async/await 语法：

```python
import asyncio

async def fetch_data(url: str) -> str:
    print(f"开始请求: {url}")
    await asyncio.sleep(1)  # 模拟网络请求
    return f"来自{url}的数据"

async def main():
    # 并发执行多个任务
    tasks = [
        fetch_data("https://api1.example.com"),
        fetch_data("https://api2.example.com"),
        fetch_data("https://api3.example.com"),
    ]
    results = await asyncio.gather(*tasks)
    for r in results:
        print(r)

asyncio.run(main())
```

## 8. 包管理

### 8.1 pip

```bash
# 安装包
pip install requests

# 安装指定版本
pip install requests==2.28.0

# 升级包
pip install --upgrade requests

# 卸载包
pip uninstall requests

# 列出已安装的包
pip list
```

### 8.2 虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活（Windows）
venv\Scripts\activate

# 激活（Linux/macOS）
source venv/bin/activate

# 退出
deactivate
```

## 9. 常用标准库

| 库名 | 用途 |
|------|------|
| `os` | 操作系统接口 |
| `sys` | 系统相关参数 |
| `json` | JSON 编解码 |
| `re` | 正则表达式 |
| `datetime` | 日期时间处理 |
| `collections` | 高级容器 |
| `itertools` | 迭代器工具 |
| `functools` | 函数工具 |
| `pathlib` | 路径处理 |
| `logging` | 日志记录 |

## 10. Python 之禅

Python 的设计哲学可以通过 `import this` 查看：

```
优美胜于丑陋
明了胜于晦涩
简洁胜于复杂
复杂胜于难懂
扁平胜于嵌套
稀疏胜于密集
可读性很重要
```
