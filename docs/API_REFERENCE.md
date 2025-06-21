# 📚 Claude Code Usage Monitor - API参考文档

## 🔍 概述

本文档提供了Claude Code Usage Monitor所有公共API的详细参考，包括函数签名、参数说明、返回值和使用示例。

## 📦 核心模块 (core)

### 🗃️ data.py

#### `check_ccusage_installed() -> bool`
检查ccusage CLI工具是否已安装。

**返回值:**
- `bool`: 如果ccusage已安装返回True，否则返回False

**示例:**
```python
from ccusage_monitor.core.data import check_ccusage_installed

if check_ccusage_installed():
    print("ccusage is ready!")
else:
    print("Please install ccusage first")
```

#### `run_ccusage() -> Optional[CcusageData]`
执行ccusage命令获取token使用数据。

**返回值:**
- `Optional[CcusageData]`: 成功时返回使用数据，失败时返回None

**示例:**
```python
from ccusage_monitor.core.data import run_ccusage

data = run_ccusage()
if data:
    print(f"Found {len(data['blocks'])} blocks")
```

#### `run_ccusage_async() -> Optional[CcusageData]`
异步版本的ccusage数据获取函数。

**返回值:**
- `Optional[CcusageData]`: 异步返回使用数据

**示例:**
```python
import asyncio
from ccusage_monitor.core.data import run_ccusage_async

async def main():
    data = await run_ccusage_async()
    if data:
        print("Data received asynchronously")

asyncio.run(main())
```

#### `get_token_limit(plan: str, blocks: Optional[List[CcusageBlock]] = None) -> int`
根据计划类型获取token限制。

**参数:**
- `plan`: 计划类型 ("pro", "max5", "max20", "custom_max")
- `blocks`: 可选的历史数据块列表

**返回值:**
- `int`: token限制数量

**示例:**
```python
from ccusage_monitor.core.data import get_token_limit

# 获取Pro计划限制
pro_limit = get_token_limit("pro")  # 返回 7000

# 获取自定义最大限制
custom_limit = get_token_limit("custom_max", blocks)
```

### 🧮 calculations.py

#### `calculate_hourly_burn_rate(blocks: List[CcusageBlock], current_time: datetime) -> float`
计算每小时token燃烧率。

**参数:**
- `blocks`: ccusage数据块列表
- `current_time`: 当前时间

**返回值:**
- `float`: 每分钟token消耗率

**示例:**
```python
from datetime import datetime
from ccusage_monitor.core.calculations import calculate_hourly_burn_rate

burn_rate = calculate_hourly_burn_rate(blocks, datetime.now())
print(f"Current burn rate: {burn_rate:.1f} tokens/min")
```

#### `get_next_reset_time(current_time: datetime, custom_reset_hour: Optional[int] = None, timezone_str: str = "Europe/Warsaw") -> datetime`
计算下次token重置时间。

**参数:**
- `current_time`: 当前时间
- `custom_reset_hour`: 自定义重置小时 (0-23)
- `timezone_str`: 时区字符串

**返回值:**
- `datetime`: 下次重置时间

**示例:**
```python
from datetime import datetime
from ccusage_monitor.core.calculations import get_next_reset_time

reset_time = get_next_reset_time(
    datetime.now(),
    custom_reset_hour=9,
    timezone_str="US/Eastern"
)
print(f"Next reset: {reset_time}")
```

#### `get_velocity_indicator(burn_rate: float) -> str`
根据燃烧率获取速度指示器。

**参数:**
- `burn_rate`: 燃烧率 (tokens/min)

**返回值:**
- `str`: 速度指示器字符串

**示例:**
```python
from ccusage_monitor.core.calculations import get_velocity_indicator

indicator = get_velocity_indicator(15.5)
print(f"Speed: {indicator}")  # 可能输出: "🔥 HIGH"
```

### ⚙️ config.py

#### `parse_args() -> CLIArgs`
解析命令行参数。

**返回值:**
- `CLIArgs`: 包含所有配置选项的对象

**示例:**
```python
from ccusage_monitor.core.config import parse_args

args = parse_args()
print(f"Plan: {args.plan}")
print(f"Rich mode: {args.rich}")
print(f"Timezone: {args.timezone}")
```

### 💾 cache.py

#### `cache.get(key: str, ttl: Optional[int] = None) -> Any`
从缓存获取数据。

**参数:**
- `key`: 缓存键
- `ttl`: 生存时间（秒）

**返回值:**
- `Any`: 缓存的数据，如果不存在或过期返回None

**示例:**
```python
from ccusage_monitor.core.cache import cache

# 获取缓存数据
data = cache.get("ccusage_data", ttl=5)
if data:
    print("Using cached data")
```

#### `cache.set(key: str, value: Any) -> None`
设置缓存数据。

**参数:**
- `key`: 缓存键
- `value`: 要缓存的数据

**示例:**
```python
from ccusage_monitor.core.cache import cache

# 设置缓存
cache.set("user_config", {"plan": "pro", "timezone": "UTC"})
```

## 🎨 UI模块 (ui)

### 🖥️ display.py

#### `clear_screen() -> None`
清空终端屏幕。

**示例:**
```python
from ccusage_monitor.ui.display import clear_screen

clear_screen()
```

#### `hide_cursor() -> None`
隐藏终端光标。

#### `show_cursor() -> None`
显示终端光标。

#### `create_token_progress_bar(percentage: float, width: int = 50) -> str`
创建token使用进度条。

**参数:**
- `percentage`: 使用百分比 (0-100)
- `width`: 进度条宽度

**返回值:**
- `str`: 格式化的进度条字符串

**示例:**
```python
from ccusage_monitor.ui.display import create_token_progress_bar

bar = create_token_progress_bar(75.5, width=40)
print(bar)  # [████████████████████████████████░░░░░░░░] 75.5%
```

#### `create_time_progress_bar(elapsed_minutes: float, total_minutes: float, width: int = 50) -> str`
创建时间进度条。

**参数:**
- `elapsed_minutes`: 已过去的分钟数
- `total_minutes`: 总分钟数
- `width`: 进度条宽度

**返回值:**
- `str`: 格式化的时间进度条

### 🌈 rich_display.py

#### `create_rich_display() -> RichDisplay`
创建Rich显示组件。

**返回值:**
- `RichDisplay`: Rich显示对象

**示例:**
```python
from ccusage_monitor.ui.rich_display import create_rich_display

display = create_rich_display()
display.update_display(data)
```

## 📱 应用模块 (app)

### 🚀 main.py

#### `main() -> None`
标准UI模式的主入口函数。

**示例:**
```python
from ccusage_monitor.app.main import main

# 启动标准UI监控
main()
```

### ✨ main_rich.py

#### `main_with_args(args: CLIArgs) -> None`
使用指定参数启动Rich UI模式。

**参数:**
- `args`: CLI参数对象

**示例:**
```python
from ccusage_monitor.app.main_rich import main_with_args
from ccusage_monitor.core.config import parse_args

args = parse_args()
args.rich = True
main_with_args(args)
```

#### `format_time(minutes: float) -> str`
格式化时间显示。

**参数:**
- `minutes`: 分钟数

**返回值:**
- `str`: 格式化的时间字符串

**示例:**
```python
from ccusage_monitor.app.main_rich import format_time

time_str = format_time(125.5)
print(time_str)  # "2h 5m"
```

## 🔧 类型定义 (protocols.py)

### CcusageBlock
```python
class CcusageBlock(TypedDict, total=False):
    isActive: bool
    totalTokens: int
    startTime: str
    isGap: bool
    actualEndTime: str
```

### CcusageData
```python
class CcusageData(TypedDict):
    blocks: List[CcusageBlock]
```

### CLIArgs
```python
class CLIArgs:
    plan: str = "pro"
    reset_hour: Optional[int] = None
    timezone: str = "Europe/Warsaw"
    performance: bool = False
    rich: bool = False
    refresh: int = 3
```

## 🎯 使用示例

### 基本监控循环
```python
from ccusage_monitor.core import data, calculations, config
from ccusage_monitor.ui import display
from datetime import datetime
import time

def simple_monitor():
    """简单的监控示例"""
    args = config.parse_args()
    
    if not data.check_ccusage_installed():
        print("ccusage not installed!")
        return
    
    token_limit = data.get_token_limit(args.plan)
    
    while True:
        # 获取数据
        ccusage_data = data.run_ccusage()
        if not ccusage_data:
            continue
            
        # 查找活跃会话
        active_block = None
        for block in ccusage_data["blocks"]:
            if block.get("isActive", False):
                active_block = block
                break
                
        if not active_block:
            continue
            
        # 计算指标
        tokens_used = active_block.get("totalTokens", 0)
        usage_pct = (tokens_used / token_limit) * 100
        
        burn_rate = calculations.calculate_hourly_burn_rate(
            ccusage_data["blocks"], 
            datetime.now()
        )
        
        # 显示信息
        print(f"Tokens: {tokens_used}/{token_limit} ({usage_pct:.1f}%)")
        print(f"Burn rate: {burn_rate:.1f} tokens/min")
        
        time.sleep(3)

if __name__ == "__main__":
    simple_monitor()
```

### 自定义UI组件
```python
from ccusage_monitor.ui.display import create_token_progress_bar
from ccusage_monitor.core.config import CYAN, RESET

def custom_display(tokens_used, token_limit):
    """自定义显示组件"""
    usage_pct = (tokens_used / token_limit) * 100
    
    # 创建进度条
    progress_bar = create_token_progress_bar(usage_pct)
    
    # 自定义格式
    print(f"{CYAN}Token Usage:{RESET}")
    print(f"  {progress_bar}")
    print(f"  {tokens_used:,} / {token_limit:,} tokens")
    
    # 状态指示
    if usage_pct > 90:
        print("  ⚠️  WARNING: High usage!")
    elif usage_pct > 75:
        print("  ⚡ Moderate usage")
    else:
        print("  ✅ Normal usage")
```

---

## 📚 相关文档

- [项目架构](ARCHITECTURE.md)
- [开发者指南](DEVELOPER_GUIDE.md)
- [使用说明](USAGE.md)
- [配置选项](CONFIG.md)

---

*本API参考文档提供了所有公共接口的详细说明，帮助开发者集成和扩展功能。*
