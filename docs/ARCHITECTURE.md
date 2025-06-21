# 🏗️ Claude Code Usage Monitor - 项目架构文档

## 📋 项目概述

Claude Code Usage Monitor 是一个实时监控 Claude AI token 使用情况的终端工具。该项目采用模块化设计，支持多种 Claude 计划类型，提供美观的终端界面和智能预测功能。

## 🎯 核心功能

- **实时监控** - 每3秒更新token使用情况
- **多计划支持** - Pro (7K)、Max5 (35K)、Max20 (140K)、自定义计划
- **智能预测** - 基于燃烧率预测token耗尽时间
- **自动检测** - Pro计划超限时自动切换到custom_max
- **双UI模式** - 标准终端UI和Rich美化UI
- **缓存优化** - 减少重复API调用，提升性能
- **时区支持** - 支持自定义时区和重置时间

## 🏗️ 项目架构

### 目录结构
```
ccusage_monitor/
├── app/                    # 应用层
│   ├── main.py            # 标准UI主应用
│   └── main_rich.py       # Rich UI主应用
├── core/                   # 核心业务逻辑层
│   ├── cache.py           # 数据缓存
│   ├── calculations.py    # 计算逻辑
│   ├── config.py          # 配置管理
│   └── data.py            # 数据获取
├── ui/                     # 用户界面层
│   ├── display.py         # 标准显示
│   └── rich_display.py    # Rich显示
├── protocols.py           # 类型定义
├── main.py               # 入口点
└── __main__.py           # 模块执行入口
```

### 架构层次

#### 1. 应用层 (Application Layer)
- **职责**: 主应用逻辑和用户交互流程
- **模块**:
  - `app/main.py` - 标准UI模式的主循环
  - `app/main_rich.py` - Rich UI模式的主循环

#### 2. 核心层 (Core Layer)
- **职责**: 核心业务逻辑和数据处理
- **模块**:
  - `core/data.py` - ccusage CLI交互和数据获取
  - `core/calculations.py` - 燃烧率计算和时间预测
  - `core/config.py` - 配置管理和CLI参数解析
  - `core/cache.py` - 数据缓存和性能优化

#### 3. UI层 (User Interface Layer)
- **职责**: 用户界面渲染和显示逻辑
- **模块**:
  - `ui/display.py` - 标准终端显示组件
  - `ui/rich_display.py` - Rich库美化显示组件

#### 4. 协议层 (Protocol Layer)
- **职责**: 类型定义和接口规范
- **模块**:
  - `protocols.py` - TypedDict和Protocol定义

## 🔄 数据流程

### 主要数据流
1. **初始化阶段**
   ```
   用户启动 → 检查依赖 → 解析参数 → 选择UI模式 → 初始化组件
   ```

2. **监控循环**
   ```
   调用ccusage → 解析数据 → 计算指标 → 更新显示 → 等待刷新
   ```

3. **数据处理流程**
   ```
   原始JSON → 活跃会话 → Token统计 → 燃烧率计算 → 时间预测 → 警告生成
   ```

### 关键算法

#### 燃烧率计算
```python
def calculate_hourly_burn_rate(blocks, current_time):
    # 获取最近1小时内的所有会话
    # 计算总token消耗和时间跨度
    # 返回 tokens/minute 的燃烧率
```

#### 时间预测
```python
def predict_depletion_time(tokens_left, burn_rate):
    # 基于当前燃烧率预测token耗尽时间
    # 考虑重置时间和使用模式
```

## 🎨 UI设计

### 标准UI模式
- 使用ANSI转义序列实现彩色输出
- 进度条和实时统计显示
- 优化的缓冲区减少闪烁

### Rich UI模式
- 使用Rich库提供美观界面
- 实时更新的布局组件
- 更好的视觉效果和用户体验

## 🚀 性能优化

### 缓存策略
- **ccusage数据缓存** - 5秒TTL，减少CLI调用
- **配置缓存** - 会话级缓存，避免重复计算
- **显示缓存** - 内容变化检测，减少重绘

### 异步支持
- 提供异步版本的数据获取函数
- 非阻塞的用户界面更新
- 超时控制和错误处理

## 🔧 配置系统

### 命令行参数
```bash
ccusage-monitor [OPTIONS]
  --plan {pro,max5,max20,custom_max}  # Claude计划类型
  --timezone TIMEZONE                 # 时区设置
  --reset-hour HOUR                   # 自定义重置时间
  --rich                              # 启用Rich UI
  --refresh SECONDS                   # 刷新间隔
```

### 计划配置
- **Pro**: 7,000 tokens
- **Max5**: 35,000 tokens  
- **Max20**: 140,000 tokens
- **Custom Max**: 自动检测历史最高值

## 🛡️ 错误处理

### 依赖检查
- 检查ccusage CLI工具安装状态
- 提供详细的安装指导
- 优雅的错误退出

### 数据验证
- JSON解析错误处理
- 网络超时处理
- 数据完整性验证

### 用户体验
- 清晰的错误消息
- 恢复建议
- 优雅的程序退出

## 🧪 测试策略

### 单元测试
- 核心计算逻辑测试
- 数据处理函数测试
- UI组件独立测试

### 集成测试
- 端到端流程测试
- 外部依赖模拟
- 错误场景测试

### 性能测试
- 内存使用监控
- 响应时间测试
- 并发处理能力

## 📦 部署和分发

### PyPI包
- 使用hatchling构建系统
- 自动化版本管理
- 依赖声明和兼容性

### 安装方式
```bash
# PyPI安装
pip install ccusage-monitor

# 直接运行
uvx ccusage-monitor

# 开发安装
pip install -e .
```

## 🔮 未来规划

### 功能扩展
- [ ] Web界面支持
- [ ] 历史数据分析
- [ ] 多用户支持
- [ ] API接口提供

### 性能优化
- [ ] 更智能的缓存策略
- [ ] 异步UI更新
- [ ] 内存使用优化

### 用户体验
- [ ] 配置文件支持
- [ ] 主题自定义
- [ ] 通知系统集成

---

## 📚 相关文档

- [安装指南](INSTALL.md)
- [使用说明](USAGE.md)
- [配置选项](CONFIG.md)
- [故障排除](../TROUBLESHOOTING.md)
- [贡献指南](../CONTRIBUTING.md)

---

*本文档描述了Claude Code Usage Monitor的完整架构设计，为开发者提供深入理解项目结构的参考。*
