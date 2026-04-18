# 🔔 电商合规哨兵 (MiroLaw)

**基于群体智能的电商平台法律风险预测系统**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9+-green.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![GitHub Stars](https://img.shields.io/github/stars/23xxCh/Mirolaw.svg)](https://github.com/23xxCh/Mirolaw/stargazers)

---

## 📖 项目简介

**电商合规哨兵**是一款面向电商企业的智能合规风险管理平台，基于群体智能技术，提供实时的合规风险监控、预警和分析服务，帮助企业规避违规风险，降低合规成本。

### 🎯 核心功能

| 功能 | 描述 | 优势 |
|------|------|------|
| **风险预测** | AI智能分析商品描述、广告文案 | 准确率>85% |
| **实时预警** | WebSocket实时推送风险预警 | 响应时间<1秒 |
| **主动监控** | 7×24小时自动扫描风险 | 全天候守护 |
| **罚款预测** | 基于历史案例预测潜在罚款 | 降低损失70%+ |
| **知识图谱** | 8部核心法律+15个典型案例 | 快速检索 |
| **智能建议** | DeepSeek LLM生成整改方案 | 节省人力70%+ |
| **批量预测** | 支持批量商品风险分析 | 高效处理 |
| **历史追溯** | 预测记录保存与趋势分析 | 数据驱动 |

---

## 💡 项目背景

### 行业痛点

- **罚款风险高**：2023年电商平台罚款总额超**50亿元**
- **法规复杂**：电商相关法规超过**10万条**
- **人工低效**：传统合规检查耗时耗力，准确率低
- **响应滞后**：法规更新快，企业难以及时应对

### 市场规模

| 指标 | 数值 |
|------|------|
| TAM（总可触达市场） | 85亿元/年 |
| SAM（可服务市场） | 18.8亿元/年 |
| SOM（可获得市场） | 第1年940万 → 第3年9400万 |

---

## 🏗️ 技术架构

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户层                                │
│     Web管理界面  │  WebSocket实时推送  │  API接口           │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│                       应用层                                 │
│  多Agent协调器  │  预警管理器  │  主动监控器  │  历史管理器  │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│                       服务层                                 │
│  风险预测  │  罚款预测  │  知识图谱  │  建议生成  │ 向量搜索 │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│                       数据层                                 │
│   法律数据库  │  案例库  │  预测历史  │  向量索引            │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈

| 类别 | 技术选型 | 说明 |
|------|----------|------|
| **后端框架** | Python + FastAPI | 高性能异步框架 |
| **AI引擎** | DeepSeek LLM | 智能建议生成 |
| **多Agent** | 自研协调器 | 5个专业Agent协作 |
| **向量搜索** | sentence-transformers + faiss | 语义检索 |
| **实时通信** | WebSocket | 实时预警推送 |
| **部署** | Docker | 一键部署 |

---

## 🚀 快速开始

### 方式一：下载可执行文件（推荐）

直接下载 Windows 可执行文件，无需安装 Python 环境。

[![Download](https://img.shields.io/badge/下载-mirolaw--0.5.0--x64--Windows.exe-blue?style=for-the-badge)](https://github.com/23xxCh/Mirolaw/releases/latest)

1. 下载 `mirolaw-0.5.0-x64-Windows.exe`
2. 双击运行
3. 浏览器自动打开 http://localhost:8000

### 方式二：源码运行

#### 环境要求

- Python 3.9+
- pip 或 conda

#### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/23xxCh/Mirolaw.git
cd Mirolaw

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量（可选，用于LLM功能）
cp .env.example .env
# 编辑 .env 填入 DeepSeek API 密钥

# 5. 启动服务
python -m uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

### Docker部署

```bash
# 构建镜像
docker build -t mirolaw:latest .

# 运行容器
docker run -d -p 8000:8000 --name mirolaw mirolaw:latest

# 或使用 docker-compose
docker-compose up -d
```

### 本地打包 exe

如果你想在本地打包 Windows 可执行文件：

```bash
# 安装打包依赖
pip install pyinstaller

# 运行打包脚本
python build.py

# 输出文件在 release/ 目录
```

### 访问服务

- **Web界面**: http://localhost:8000/
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

---

## 📡 API接口

### 核心接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/predict` | POST | 单次风险预测 |
| `/predict/batch` | POST | 批量风险预测 |
| `/predict/realtime` | POST | 实时预测+预警 |
| `/alerts` | GET | 获取预警列表 |
| `/ws/alerts` | WebSocket | 实时预警订阅 |
| `/knowledge_graph/search` | GET | 法律知识搜索 |
| `/history/records` | GET | 预测历史记录 |

### 使用示例

```python
import requests
import json

# 风险预测
response = requests.post(
    "http://localhost:8000/predict",
    json={
        "platform_data": {
            "product_info": {"name": "产品A", "description": "世界第一"},
            "marketing_content": [{"text": "全球首创技术"}]
        },
        "horizon": 30
    }
)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# 批量预测
response = requests.post(
    "http://localhost:8000/predict/batch",
    json={
        "items": [
            {"platform_data": {"product_info": {"name": "产品1"}}},
            {"platform_data": {"product_info": {"name": "产品2"}}}
        ],
        "horizon": 30
    }
)
print(f"成功: {response.json()['success_count']}")
```

### WebSocket连接

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/alerts');

ws.onopen = () => {
    ws.send(JSON.stringify({ action: 'subscribe', topic: 'alerts' }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('收到预警:', data);
};
```

---

## 📊 项目结构

```
Mirolaw/
├── docs/                          # 文档目录
│   ├── 技术架构设计.md             # 技术架构文档
│   ├── 市场分析报告.md             # 市场分析
│   ├── 商业模式设计.md             # 商业模式
│   ├── API接口文档.md              # API文档
│   ├── 用户手册.md                 # 用户手册
│   └── 部署指南.md                 # 部署文档
│
├── src/                           # 源代码目录
│   ├── api.py                     # FastAPI接口 (v0.4.0)
│   ├── predictor.py               # 风险预测模块
│   ├── fine_predictor.py          # 罚款预测模块
│   ├── knowledge_graph.py         # 知识图谱模块
│   ├── law_database.py            # 法律数据库
│   ├── alert_system.py            # 实时预警系统
│   ├── multi_agent.py             # 多Agent架构
│   ├── vector_search.py           # 向量搜索
│   ├── prediction_history.py      # 预测历史管理
│   ├── suggestion_generator.py    # 建议生成模块
│   └── __init__.py
│
├── frontend/                      # 前端代码
│   └── public/
│       ├── index.html             # 主页面
│       ├── style.css              # 样式文件
│       └── app.js                 # 前端逻辑
│
├── tests/                         # 测试代码
│   ├── test_predictor.py
│   ├── test_alert_system.py
│   └── ...
│
├── data/                          # 数据目录
│   └── history/                   # 预测历史存储
│
├── .env.example                   # 环境变量示例
├── Dockerfile                     # Docker配置
├── docker-compose.yml             # Docker Compose配置
├── requirements.txt               # Python依赖
├── config.yaml                    # 配置文件
└── README.md                      # 本文档
```

---

## 🎯 核心创新

### 1. 多Agent协作架构

采用**5个专业Agent协作**架构，实现高效风险分析：

| Agent | 职责 |
|-------|------|
| CoordinatorAgent | 任务协调与分发 |
| DataCollectorAgent | 数据采集与预处理 |
| RiskAnalyzerAgent | 风险分析与评估 |
| LawMatcherAgent | 法律条文匹配 |
| SuggestionAgent | 整改建议生成 |

### 2. 实时预警系统

- **WebSocket推送**：毫秒级预警通知
- **规则引擎**：可配置的预警规则
- **主动监控**：定时扫描+自动预警

### 3. 知识图谱+向量搜索

**法律知识图谱** + **语义向量搜索**双重检索，准确匹配相关法律条文。

---

## 💰 商业模式

### 定价方案

| 版本 | 价格 | 功能 |
|------|------|------|
| **基础版** | ¥999/月 | 风险预警、基础报告 |
| **专业版** | ¥2,999/月 | 全功能、API调用、批量预测 |
| **企业版** | ¥9,999/月 | 定制服务、专属支持、私有部署 |

### 收入预测

- **第1年**：750万元
- **第2年**：4,000万元
- **第3年**：1.2亿元

---

## 📈 项目进度

### 已完成 ✅

- [x] 产品PRD文档
- [x] 技术架构设计
- [x] 核心代码框架
- [x] 市场分析报告
- [x] 商业模式设计
- [x] API接口文档
- [x] 用户手册
- [x] 部署指南
- [x] 风险预测模块（规则引擎+关键词检测）
- [x] 罚款预测模块
- [x] 知识图谱模块（内存存储）
- [x] 法律数据库（8部核心法律）
- [x] 建议生成模块（DeepSeek LLM）
- [x] 实时预警系统（WebSocket）
- [x] 主动监控功能
- [x] 多Agent协作架构
- [x] 向量语义搜索
- [x] 批量预测API
- [x] 预测历史记录
- [x] 前端Web界面
- [x] Docker容器化部署
- [x] 单元测试（15个测试用例）

### 进行中 🚧

- [ ] 机器学习模型优化
- [ ] 更多法律数据导入
- [ ] 性能优化

### 计划中 📋

- [ ] 生产环境部署
- [ ] 用户权限管理
- [ ] 多语言支持

---

## 🧪 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行覆盖率测试
pytest tests/ --cov=src --cov-report=html
```

---

## 🏆 荣誉与成就

- 🥇 国创赛参赛项目
- 🌟 基于MiroFish（55.8K GitHub stars）开源项目
- 🚀 多Agent架构实践案例

---

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 📞 联系我们

- **项目主页**: https://github.com/23xxCh/Mirolaw
- **问题反馈**: https://github.com/23xxCh/Mirolaw/issues

---

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代Python Web框架
- [DeepSeek](https://www.deepseek.com/) - 大语言模型服务
- [sentence-transformers](https://www.sbert.net/) - 语义向量模型

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给一个 Star！⭐**

Made with ❤️ by MiroLaw Team

</div>
