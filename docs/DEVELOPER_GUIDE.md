# 👨‍💻 Claude Code Usage Monitor - 开发者指南

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js (用于ccusage CLI)
- Git

### 开发环境设置
```bash
# 克隆项目
git clone https://github.com/zhiyue/ccusage-monitor.git
cd ccusage-monitor

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -r requirements-dev.txt
pip install -e .

# 安装ccusage CLI
npm install -g ccusage
```

## 🏗️ 项目结构详解

### 核心模块设计

#### 1. 数据层 (`core/data.py`)
```python
# 主要功能
- check_ccusage_installed()  # 检查依赖
- run_ccusage()             # 获取使用数据
- run_ccusage_async()       # 异步版本
- get_token_limit()         # 获取计划限制
```

#### 2. 计算层 (`core/calculations.py`)
```python
# 主要功能
- calculate_hourly_burn_rate()  # 计算燃烧率
- get_next_reset_time()         # 计算重置时间
- get_velocity_indicator()      # 速度指示器
```

#### 3. 缓存层 (`core/cache.py`)
```python
# 缓存策略
- TTL缓存机制
- 内存优化
- 线程安全
```

#### 4. 配置层 (`core/config.py`)
```python
# 配置管理
- parse_args()      # CLI参数解析
- 颜色常量定义
- 默认配置值
```

### UI模块设计

#### 标准UI (`ui/display.py`)
- ANSI转义序列
- 进度条渲染
- 缓冲区优化

#### Rich UI (`ui/rich_display.py`)
- Rich库组件
- 布局管理
- 实时更新

## 🔧 开发工作流

### 代码规范
```bash
# 代码格式化
black ccusage_monitor/
isort ccusage_monitor/

# 代码检查
ruff check ccusage_monitor/
mypy ccusage_monitor/

# 运行测试
pytest tests/ -v --cov=ccusage_monitor
```

### Git工作流
```bash
# 创建功能分支
git checkout -b feature/new-feature

# 提交代码
git add .
git commit -m "feat: add new feature"

# 推送分支
git push origin feature/new-feature

# 创建Pull Request
```

### 测试策略
```bash
# 单元测试
pytest tests/test_core_*.py

# 集成测试
pytest tests/test_app_*.py

# 覆盖率报告
pytest --cov=ccusage_monitor --cov-report=html
```

## 🧪 测试指南

### 测试结构
```
tests/
├── test_core_cache.py      # 缓存模块测试
├── test_core_calculations.py  # 计算模块测试
├── test_core_config.py     # 配置模块测试
├── test_core_data.py       # 数据模块测试
├── test_ui_display.py      # UI模块测试
└── test_app_main.py        # 应用层测试
```

### 编写测试
```python
import pytest
from unittest.mock import Mock, patch
from ccusage_monitor.core.data import run_ccusage

def test_run_ccusage_success():
    """测试成功获取数据的情况"""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.stdout = '{"blocks": []}'
        mock_run.return_value.returncode = 0
        
        result = run_ccusage()
        assert result is not None
        assert "blocks" in result

def test_run_ccusage_failure():
    """测试获取数据失败的情况"""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = FileNotFoundError()
        
        result = run_ccusage()
        assert result is None
```

### Mock策略
- 外部CLI调用Mock
- 时间相关函数Mock
- 网络请求Mock
- 文件系统Mock

## 🎨 UI开发指南

### 标准UI开发
```python
# 颜色使用
from ccusage_monitor.core.config import CYAN, RED, YELLOW, RESET

# 进度条创建
def create_progress_bar(percentage, width=50):
    filled = int(width * percentage / 100)
    bar = "█" * filled + "░" * (width - filled)
    return f"[{bar}] {percentage:.1f}%"
```

### Rich UI开发
```python
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import Progress

# 创建布局
layout = Layout()
layout.split_column(
    Layout(name="header", size=3),
    Layout(name="body"),
    Layout(name="footer", size=3)
)
```

## 🔄 数据流开发

### 数据获取流程
```python
async def get_usage_data():
    """异步获取使用数据"""
    try:
        # 检查缓存
        cached = cache.get("ccusage_data", ttl=5)
        if cached:
            return cached
            
        # 调用ccusage
        data = await run_ccusage_async()
        
        # 缓存结果
        cache.set("ccusage_data", data)
        return data
        
    except Exception as e:
        logger.error(f"Failed to get usage data: {e}")
        return None
```

### 计算逻辑开发
```python
def calculate_burn_rate(blocks, current_time):
    """计算token燃烧率"""
    # 获取最近1小时的数据
    recent_blocks = filter_recent_blocks(blocks, current_time, hours=1)
    
    # 计算总消耗和时间跨度
    total_tokens = sum(block.get("totalTokens", 0) for block in recent_blocks)
    time_span = calculate_time_span(recent_blocks)
    
    # 返回每分钟燃烧率
    return total_tokens / time_span if time_span > 0 else 0
```

## 🚀 性能优化

### 缓存优化
```python
class Cache:
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
    
    def get(self, key, ttl=None):
        if key not in self._cache:
            return None
            
        if ttl and self._is_expired(key, ttl):
            self.delete(key)
            return None
            
        return self._cache[key]
    
    def set(self, key, value):
        self._cache[key] = value
        self._timestamps[key] = time.time()
```

### 异步处理
```python
import asyncio

async def async_monitor_loop():
    """异步监控循环"""
    while True:
        try:
            # 异步获取数据
            data = await get_usage_data()
            
            # 处理数据
            processed = process_data(data)
            
            # 更新UI
            await update_ui(processed)
            
            # 等待下次更新
            await asyncio.sleep(3)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Error in monitor loop: {e}")
            await asyncio.sleep(1)
```

## 🔧 调试技巧

### 日志配置
```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### 调试工具
```python
# 使用pdb调试
import pdb; pdb.set_trace()

# 使用rich的inspect
from rich import inspect
inspect(data, methods=True)

# 性能分析
import cProfile
cProfile.run('main()')
```

## 📦 构建和发布

### 本地构建
```bash
# 构建包
python -m build

# 检查包
twine check dist/*

# 本地安装测试
pip install dist/*.whl
```

### 发布流程
```bash
# 测试PyPI发布
twine upload --repository testpypi dist/*

# 正式PyPI发布
twine upload dist/*
```

### 版本管理
```python
# pyproject.toml
[project]
version = "1.0.1"

# 自动版本号
from importlib.metadata import version
__version__ = version("ccusage-monitor")
```

## 🔍 代码审查清单

### 功能检查
- [ ] 功能是否按预期工作
- [ ] 错误处理是否完善
- [ ] 边界条件是否考虑
- [ ] 性能是否可接受

### 代码质量
- [ ] 代码是否符合PEP 8
- [ ] 函数是否有适当的文档
- [ ] 变量命名是否清晰
- [ ] 是否有重复代码

### 测试覆盖
- [ ] 是否有对应的单元测试
- [ ] 测试覆盖率是否足够
- [ ] 是否测试了错误情况
- [ ] 集成测试是否通过

## 🤝 贡献指南

### 提交规范
```
feat: 新功能
fix: 修复bug
docs: 文档更新
style: 代码格式
refactor: 重构
test: 测试相关
chore: 构建/工具相关
```

### Pull Request流程
1. Fork项目
2. 创建功能分支
3. 编写代码和测试
4. 确保所有测试通过
5. 提交Pull Request
6. 代码审查
7. 合并到主分支

---

## 📚 相关资源

- [Python最佳实践](https://docs.python-guide.org/)
- [Rich库文档](https://rich.readthedocs.io/)
- [pytest文档](https://docs.pytest.org/)
- [项目架构文档](ARCHITECTURE.md)

---

*本指南为开发者提供了完整的开发环境设置、代码规范、测试策略和贡献流程。*
