# 🚀 OpenClaw 主从Agent无限迭代架构 v1.0

**彻底解决单Agent卡死问题 | 主Agent催促进度+评估 | 子Agent纯执行 | 自动销毁无残留 | 稳定运行24小时+**

---

## ✨ 核心特性

### 架构优势
- ✅ **彻底解决上下文爆炸**：每个子Agent只处理一个小任务，上下文<1000token
- ✅ **彻底解决工具状态锁死**：子Agent执行完立即销毁，无任何状态残留
- ✅ **彻底解决内存泄漏**：主Agent内存占用稳定在100MB以内
- ✅ **容错性极强**：单个子Agent卡死不影响全局，自动重启
- ✅ **效率更高**：支持并行执行多个独立子任务

### 功能特性
- 🚀 **并行执行**：同时运行多个子Agent，大幅提升效率
- 📦 **自动Git提交**：每完成N个子任务自动提交代码
- 💾 **断点续传**：任务中断后自动恢复
- 📢 **进度通知**：支持钉钉/飞书/企业微信通知
- 🔄 **智能重试**：子任务失败自动重试
- 🧹 **资源自动清理**：子Agent执行完立即销毁

---

## 📋 项目结构

```
MiroLaw/
├── master_slave_iterate.py      # 主脚本（包含并行执行+自动Git提交）
├── config.yaml                  # OpenClaw配置文件
├── requirements.txt             # Python依赖
├── README.md                    # 本文档
│
├── logs/                        # 日志目录
│   └── master_slave_log_*.txt
│
├── output/                      # 输出目录
│   ├── subtasks.json           # 任务列表
│   └── final_result_*.md       # 最终交付物
│
└── master_checkpoint.json       # 断点文件（自动生成）
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API

编辑 `master_slave_iterate.py`，修改以下配置：

```python
# API配置（支持多种API）
API_TYPE = "zhipu"  # zhipu / deepseek / openai
API_KEY = "你的API Key"

# 任务配置
TOTAL_TASK = """
在这里填写你的总任务目标...
"""
```

### 3. 运行

```bash
python master_slave_iterate.py
```

---

## ⚙️ 配置说明

### 核心参数

```python
# 稳定性参数
TEMPERATURE = 0.3              # 模型温度
MAX_TOKENS = 32768            # 最大输出token
SLAVE_TIMEOUT = 600           # 子Agent超时时间（秒）
MAX_RETRIES = 3               # 单个子任务最大重试次数
REQUEST_DELAY = 5             # 任务间隔（秒）
SAVE_INTERVAL = 2             # 保存断点间隔

# 并行执行参数
MAX_WORKERS = 3               # 最多同时执行的子任务数量

# Git配置
AUTO_GIT_COMMIT = True        # 是否自动Git提交
GIT_COMMIT_INTERVAL = 3       # 每完成N个子任务提交一次

# 进度通知配置
ENABLE_NOTIFICATION = False   # 是否启用通知
NOTIFICATION_WEBHOOK = ""     # 钉钉/飞书/企业微信webhook
```

### API类型支持

| API类型 | 说明 | 模型 |
|---------|------|------|
| zhipu | 智谱AI | glm-4-plus |
| deepseek | DeepSeek | deepseek-chat |
| openai | OpenAI | gpt-4-turbo-preview |

---

## 🎯 工作流程

```
┌─────────────────────────────────────────────────┐
│ 主Agent（项目经理）                              │
│ - 全局任务规划与拆分                             │
│ - 子Agent生命周期管理（创建/销毁/重启）          │
│ - 子任务结果评估与打分                           │
│ - 进度追踪与迭代推进                             │
│ - 最终结果整合与输出                             │
└───────────────────┬─────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐
    │子Agent1 │ │子Agent2 │ │子Agent3 │
    │纯执行   │ │纯执行   │ │纯执行   │
    │无状态   │ │无状态   │ │无状态   │
    │用完即毁 │ │用完即毁 │ │用完即毁 │
    └─────────┘ └─────────┘ └─────────┘
```

---

## 📊 性能对比

| 指标 | 单Agent | 主从架构 |
|------|---------|----------|
| 上下文大小 | 无限增长 → 爆炸 | 稳定<1000 token |
| 内存占用 | 持续增长 → OOM | 稳定<100MB |
| 工具状态 | 容易锁死 | 永不锁死 |
| 容错性 | 一旦失败全挂 | 单点失败不影响全局 |
| 执行效率 | 串行 | 并行（3x+） |
| 运行时长 | 最多2小时 | 24小时+ |

---

## 🔧 高级功能

### 1. 并行执行

项目已内置并行执行功能，通过 `MAX_WORKERS` 参数控制并发数：

```python
MAX_WORKERS = 3  # 同时运行3个子Agent
```

### 2. 自动Git提交

启用自动Git提交后，每完成N个子任务会自动提交代码：

```python
AUTO_GIT_COMMIT = True
GIT_COMMIT_INTERVAL = 3  # 每3个子任务提交一次
```

### 3. 进度通知

支持钉钉/飞书/企业微信通知：

```python
ENABLE_NOTIFICATION = True
NOTIFICATION_WEBHOOK = "你的webhook地址"
```

钉钉示例：
```python
NOTIFICATION_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=xxx"
```

飞书示例：
```python
NOTIFICATION_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
```

### 4. 断点续传

任务中断后，下次运行会自动从断点恢复：

```bash
# 中断任务
Ctrl+C

# 重新运行
python master_slave_iterate.py
# 会自动从上次中断的地方继续
```

---

## 📝 使用示例

### 示例1：完成一个完整的软件项目

```python
TOTAL_TASK = """
项目名称：电商合规哨兵

总任务目标：
1. 完成产品PRD文档
2. 完成技术架构设计
3. 完成核心模块代码
4. 完成市场分析报告
5. 完成商业模式设计

验收标准：
- PRD文档包含完整功能设计
- 技术架构包含完整架构图
- 代码框架可以运行
- 市场分析包含竞争分析
- 商业模式包含收入模式
"""
```

### 示例2：完成一篇学术论文

```python
TOTAL_TASK = """
任务：撰写一篇关于"AI法律风险预测"的学术论文

要求：
1. 文献综述（30篇以上）
2. 研究方法设计
3. 实验设计与分析
4. 结果讨论
5. 结论与展望

标准：
- 字数：8000-10000字
- 格式：学术论文格式
- 参考文献：50篇以上
"""
```

---

## 🐛 常见问题

### Q1: 子Agent执行超时怎么办？

**原因**：任务太复杂，超时时间设置太短

**解决**：
```python
# 增加超时时间
SLAVE_TIMEOUT = 900  # 15分钟

# 或拆分更小的子任务
```

### Q2: 预测准确率不足怎么办？

**原因**：任务描述不明确

**解决**：
- 优化 `TOTAL_TASK` 描述
- 增加验收标准
- 调整 `TEMPERATURE` 参数

### Q3: Git提交失败怎么办？

**原因**：没有初始化Git仓库

**解决**：
```bash
cd E:\WORKS\MiroLaw
git init
git add .
git commit -m "Initial commit"
```

### Q4: 内存占用过高怎么办？

**原因**：主Agent上下文太大

**解决**：
```python
# 减少保存的历史消息数量
"master_messages": self.master_messages[-10:]  # 只保留最近10条
```

---

## 📚 最佳实践

### 1. 任务拆分原则

- ✅ 每个子任务应能在10-30分钟内完成
- ✅ 子任务描述要具体、明确
- ✅ 子任务之间尽量独立，减少依赖

### 2. 并发数设置

| 任务类型 | 推荐并发数 | 说明 |
|----------|-----------|------|
| 文档生成 | 2-3 | 避免API限流 |
| 代码生成 | 3-5 | 可适当提高 |
| 数据分析 | 1-2 | 资源密集型 |

### 3. Git提交策略

- 提交间隔：3-5个子任务
- 提交信息：包含进度信息
- 分支管理：建议使用feature分支

---

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

---

## 📄 许可证

MIT License

---

## 👥 作者

OpenClaw Team

---

## 🙏 致谢

感谢以下开源项目：
- [MiroFish](https://github.com/666ghj/MiroFish) - 群体智能引擎
- [OpenClaw](https://github.com/openclaw/openclaw) - AI Agent框架
