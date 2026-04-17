# 电商合规哨兵 API 接口文档

## 1. 概述

### 1.1 API简介

电商合规哨兵API是一套专为电商平台设计的合规风险预测与管理服务接口。通过智能化的风险识别算法，该API帮助商家和平台运营者及时发现潜在的法律风险，预测可能的罚款金额，并提供针对性的应对建议。系统整合了知识图谱技术，能够快速检索相关法规案例，为决策提供数据支持。

### 1.2 基础URL

```
生产环境: https://api.miro-law.com
测试环境: https://api-test.miro-law.com
```

### 1.3 认证方式

API采用Bearer Token认证方式。所有请求需在请求头中携带有效的访问令牌。

**获取令牌**：
```
POST /auth/token
Content-Type: application/json

{
  "client_id": "your_client_id",
  "client_secret": "your_client_secret"
}
```

**响应示例**：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 7200
}
```

---

## 2. 公共参数

### 2.1 请求头

所有API请求必须包含以下请求头：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| Authorization | String | 是 | Bearer {access_token} |
| Content-Type | String | 是 | application/json |
| X-Request-ID | String | 否 | 请求唯一标识，用于问题追踪 |
| X-API-Version | String | 否 | API版本号，默认v1 |

### 2.2 响应格式

所有接口统一返回JSON格式数据，包含以下标准字段：

```json
{
  "code": 200,
  "message": "success",
  "data": { },
  "timestamp": 1703123456,
  "request_id": "req_abc123xyz"
}
```

**响应字段说明**：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| code | Integer | 业务状态码，200表示成功 |
| message | String | 响应消息 |
| data | Object | 业务数据对象 |
| timestamp | Long | 服务器时间戳（秒） |
| request_id | String | 请求追踪ID |

### 2.3 错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| 200 | 成功 | - |
| 400 | 请求参数错误 | 检查请求参数格式和必填项 |
| 401 | 认证失败 | 检查Token是否有效或已过期 |
| 403 | 权限不足 | 联系管理员开通相应权限 |
| 404 | 资源不存在 | 检查请求路径和资源ID |
| 429 | 请求频率超限 | 降低请求频率或申请提升配额 |
| 500 | 服务器内部错误 | 联系技术支持并提供request_id |
| 503 | 服务暂时不可用 | 稍后重试 |

---

## 3. 风险预测接口

### 3.1 POST /api/v1/predict

预测电商行为或商品的合规风险等级。

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| product_name | String | 是 | 商品名称 |
| category | String | 是 | 商品分类（如：食品、保健品、医疗器械） |
| description | String | 否 | 商品描述文本 |
| keywords | Array | 否 | 商品关键词列表 |
| platform | String | 否 | 电商平台（如：淘宝、京东、拼多多） |
| region | String | 否 | 销售区域（如：中国大陆、港澳台、海外） |

**请求示例**：
```json
{
  "product_name": "XX品牌瘦身胶囊",
  "category": "保健品",
  "description": "纯天然植物提取，快速瘦身不反弹",
  "keywords": ["减肥", "瘦身", "排毒"],
  "platform": "淘宝",
  "region": "中国大陆"
}
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "risk_level": "high",
    "risk_score": 85,
    "risk_categories": [
      {
        "category": "广告法违规",
        "score": 90,
        "reason": "使用"快速瘦身"等绝对化用语"
      },
      {
        "category": "食品安全风险",
        "score": 80,
        "reason": "保健品宣传治疗功效"
      }
    ],
    "recommendations": [
      "修改广告文案，避免使用绝对化用语",
      "补充保健品备案证明",
      "明确标注"保健食品不能替代药物"提示"
    ]
  },
  "timestamp": 1703123456,
  "request_id": "req_predict_001"
}
```

**错误处理**：
- 缺少必填参数返回400错误
- 商品分类不支持返回400错误并提示支持的分类列表
- 服务超时返回503错误，建议重试

---

## 4. 罚款预测接口

### 4.1 POST /api/v1/fine_predict

基于违规情形预测可能的行政处罚罚款金额范围。

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| violation_type | String | 是 | 违规类型（如：虚假宣传、价格欺诈、无证经营） |
| severity | String | 是 | 违规严重程度（minor/moderate/severe） |
| sales_amount | Number | 否 | 涉案销售金额（元） |
| profit_amount | Number | 否 | 违法所得金额（元） |
| violation_count | Integer | 否 | 历史违规次数 |
| region | String | 否 | 违规发生地（省份或城市） |
| mitigating_factors | Array | 否 | 从轻处罚情节 |

**请求示例**：
```json
{
  "violation_type": "虚假宣传",
  "severity": "moderate",
  "sales_amount": 150000,
  "profit_amount": 30000,
  "violation_count": 0,
  "region": "广东省",
  "mitigating_factors": ["主动下架", "配合调查"]
}
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "fine_range": {
      "min": 50000,
      "max": 200000,
      "recommended": 85000
    },
    "legal_basis": [
      {
        "law": "《中华人民共和国广告法》第五十五条",
        "clause": "违反本法规定，发布虚假广告的，由工商行政管理部门责令停止发布广告..."
      }
    ],
    "calculation_factors": {
      "base_fine": 50000,
      "sales_multiplier": 1.5,
      "profit_multiplier": 0.3,
      "mitigation_discount": 0.2
    },
    "similar_cases": [
      {
        "case_id": "case_2023_001",
        "violation": "虚假宣传",
        "fine_amount": 80000,
        "similarity": 0.85
      }
    ]
  },
  "timestamp": 1703123456,
  "request_id": "req_fine_001"
}
```

---

## 5. 知识图谱接口

### 5.1 GET /api/v1/knowledge_graph/search

搜索知识图谱中的法规、案例、处罚信息。

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| query | String | 是 | 搜索关键词 |
| type | String | 否 | 资源类型（law/case/regulation） |
| limit | Integer | 否 | 返回结果数量，默认10，最大50 |
| offset | Integer | 否 | 分页偏移量，默认0 |

**请求示例**：
```
GET /api/v1/knowledge_graph/search?query=虚假宣传&type=case&limit=5
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 128,
    "results": [
      {
        "id": "kg_case_001",
        "title": "某电商公司虚假宣传处罚案",
        "type": "case",
        "summary": "该公司在商品详情页宣传"100%纯天然"，实际含有化学添加剂...",
        "fine_amount": 120000,
        "decision_date": "2023-08-15",
        "authority": "某市市场监督管理局"
      }
    ]
  }
}
```

### 5.2 POST /api/v1/knowledge_graph/cases

查询知识图谱中的关联案例网络。

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| entity_name | String | 是 | 实体名称（公司名/品牌名/商品名） |
| entity_type | String | 否 | 实体类型（company/brand/product） |
| depth | Integer | 否 | 关联深度，默认2，最大3 |

**请求示例**：
```json
{
  "entity_name": "XX科技有限公司",
  "entity_type": "company",
  "depth": 2
}
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "nodes": [
      {"id": "company_001", "name": "XX科技有限公司", "type": "company"},
      {"id": "case_001", "name": "虚假宣传案", "type": "case"},
      {"id": "law_001", "name": "广告法", "type": "law"}
    ],
    "edges": [
      {"source": "company_001", "target": "case_001", "relation": "涉案"},
      {"source": "case_001", "target": "law_001", "relation": "适用法律"}
    ]
  }
}
```

---

## 6. 应对建议接口

### 6.1 POST /api/v1/suggestions

基于风险分析结果生成合规应对建议。

**请求参数**：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| risk_id | String | 是 | 风险预测结果ID |
| context | Object | 否 | 补充上下文信息 |
| priority | String | 否 | 建议优先级（urgent/normal/low） |

**请求示例**：
```json
{
  "risk_id": "risk_20231215_001",
  "context": {
    "deadline": "2023-12-20",
    "budget": 50000
  },
  "priority": "urgent"
}
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "suggestions": [
      {
        "priority": 1,
        "action": "立即下架问题商品",
        "reason": "避免违规范围扩大",
        "deadline": "24小时内",
        "difficulty": "low"
      },
      {
        "priority": 2,
        "action": "修改商品详情页文案",
        "reason": "消除广告法违规内容",
        "deadline": "3个工作日",
        "difficulty": "medium",
        "guidelines": [
          "删除"最"、"第一"等绝对化用语",
          "补充资质证明文件链接",
          "添加免责声明"
        ]
      },
      {
        "priority": 3,
        "action": "建立合规审核流程",
        "reason": "预防后续违规",
        "deadline": "建议1个月内",
        "difficulty": "high"
      }
    ],
    "estimated_cost": {
      "time": "5-7个工作日",
      "money": "5000-15000元"
    },
    "reference_cases": ["case_001", "case_002"]
  }
}
```

---

## 7. 其他接口

### 7.1 GET /api/v1/risk_types

获取系统支持的风险类型列表。

**请求示例**：
```
GET /api/v1/risk_types
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "risk_types": [
      {
        "type": "ad_law",
        "name": "广告法违规",
        "sub_types": ["虚假宣传", "绝对化用语", "未审批广告"]
      },
      {
        "type": "food_safety",
        "name": "食品安全风险",
        "sub_types": ["标签不规范", "无证经营", "过期食品"]
      },
      {
        "type": "consumer_protection",
        "name": "消费者权益保护",
        "sub_types": ["价格欺诈", "虚假促销", "退换货纠纷"]
      }
    ]
  }
}
```

### 7.2 GET /api/v1/health

健康检查接口，用于监控服务状态。

**请求示例**：
```
GET /api/v1/health
```

**响应示例**：
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "status": "healthy",
    "services": {
      "api": "up",
      "database": "up",
      "cache": "up",
      "ml_engine": "up"
    },
    "version": "1.2.3",
    "uptime": 864000
  }
}
```

---

## 附录

### A. 请求频率限制

| 用户等级 | 每分钟请求数 | 每日请求数 |
|----------|--------------|------------|
| 免费版 | 10 | 1000 |
| 专业版 | 60 | 10000 |
| 企业版 | 300 | 100000 |

### B. 版本更新日志

- v1.0.0 (2023-01-01): 初始版本发布
- v1.1.0 (2023-06-01): 新增知识图谱接口
- v1.2.0 (2023-12-01): 优化风险预测算法，提升准确率

### C. 技术支持

- 邮箱：support@miro-law.com
- 工作时间：周一至周五 9:00-18:00
- 在线文档：https://docs.miro-law.com

---

**文档版本**：v1.0  
**最后更新**：2024年1月
