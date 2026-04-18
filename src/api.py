"""
FastAPI接口模块

本模块提供RESTful API接口，供前端和其他系统调用。
支持WebSocket实时推送和主动预警功能。
"""

from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import logging
from datetime import datetime
from pathlib import Path
import asyncio

# 导入核心模块
from .predictor import RiskPredictor
from .fine_predictor import FinePredictor
from .knowledge_graph import LegalKnowledgeGraph
from .suggestion_generator import SuggestionGenerator
from .law_database import LawDatabase, get_law_database
from .alert_system import get_alert_manager, get_proactive_monitor, Alert, AlertLevel
from .prediction_history import get_prediction_history, PredictionRecord
from .cache import get_global_cache, cache_prediction, get_cached_prediction
from .rate_limiter import get_rate_limiter
from .health_check import get_health_checker
from .task_queue import get_task_queue, TaskStatus

# 创建FastAPI应用
app = FastAPI(
    title="电商合规哨兵 API",
    description="电商平台合规风险预测与应对建议系统 - 支持实时预警",
    version="0.4.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
FRONTEND_DIR = Path(__file__).parent.parent / "frontend" / "public"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

logger = logging.getLogger(__name__)

# 初始化核心模块
_knowledge_graph = None
_risk_predictor = None
_fine_predictor = None
_suggestion_generator = None


def get_knowledge_graph():
    global _knowledge_graph
    if _knowledge_graph is None:
        _knowledge_graph = LegalKnowledgeGraph(
            uri="memory://localhost",
            user="default",
            password="default"
        )
    return _knowledge_graph


def get_risk_predictor():
    global _risk_predictor
    if _risk_predictor is None:
        _risk_predictor = RiskPredictor(config={})
    return _risk_predictor


def get_fine_predictor():
    global _fine_predictor
    if _fine_predictor is None:
        _fine_predictor = FinePredictor(knowledge_graph=get_knowledge_graph())
    return _fine_predictor


def get_suggestion_generator():
    global _suggestion_generator
    if _suggestion_generator is None:
        _suggestion_generator = SuggestionGenerator(llm_client=None)
    return _suggestion_generator


# ==================== 数据模型 ====================

class PredictRequest(BaseModel):
    """风险预测请求模型"""
    platform_data: Dict = Field(..., description="平台运营数据")
    risk_types: Optional[List[str]] = Field(None, description="风险类型列表")
    horizon: int = Field(30, ge=1, le=365, description="预测时间范围（天）")

    class Config:
        json_schema_extra = {
            "example": {
                "platform_data": {
                    "product_info": {"name": "产品A", "category": "电子产品", "description": "世界最好的产品"},
                    "sales_data": [{"date": "2024-01-01", "amount": 10000}],
                    "marketing_content": [{"text": "全球首创技术"}]
                },
                "risk_types": ["虚假宣传", "价格欺诈"],
                "horizon": 30
            }
        }


class PredictResponse(BaseModel):
    """风险预测响应模型"""
    risk_assessments: List[Dict] = Field(..., description="风险评估结果列表")
    overall_risk_score: float = Field(..., description="综合风险评分")
    prediction_horizon: int = Field(..., description="预测时间范围")
    timestamp: str = Field(..., description="预测时间戳")
    recommendation: str = Field(..., description="整体建议")


class FinePredictRequest(BaseModel):
    """罚款预测请求模型"""
    risk_type: str = Field(..., description="风险类型")
    platform_data: Dict = Field(..., description="平台运营数据")
    simulation_result: Dict = Field(..., description="风险预测结果")

    class Config:
        json_schema_extra = {
            "example": {
                "risk_type": "虚假宣传",
                "platform_data": {
                    "company_size": "中型",
                    "annual_revenue": 10000000,
                    "violation_history": []
                },
                "simulation_result": {
                    "probability": 0.75,
                    "risk_level": "高"
                }
            }
        }


class FinePredictResponse(BaseModel):
    """罚款预测响应模型"""
    fine_range: Dict = Field(..., description="罚款金额范围")
    confidence: float = Field(..., description="预测置信度")
    legal_basis: List[Dict] = Field(..., description="法律依据列表")
    historical_cases: List[Dict] = Field(..., description="相似历史案例")
    factors: Dict = Field(..., description="影响因素分析")
    timestamp: str = Field(..., description="预测时间戳")


class KnowledgeGraphSearchRequest(BaseModel):
    """知识图谱搜索请求模型"""
    query: str = Field(..., description="搜索关键词")
    search_type: str = Field("all", description="搜索类型: case/article/risk_type/all")
    limit: int = Field(10, ge=1, le=100, description="返回结果数量限制")


class KnowledgeGraphSearchResponse(BaseModel):
    """知识图谱搜索响应模型"""
    results: List[Dict] = Field(..., description="搜索结果列表")
    total: int = Field(..., description="总结果数量")
    query: str = Field(..., description="搜索关键词")


class SuggestionRequest(BaseModel):
    """建议生成请求模型"""
    risk_type: str = Field(..., description="风险类型")
    simulation_result: Dict = Field(..., description="风险预测结果")
    similar_cases: Optional[List[Dict]] = Field(None, description="相似案例列表")


class SuggestionResponse(BaseModel):
    """建议生成响应模型"""
    immediate_actions: List[Dict] = Field(..., description="立即行动建议")
    long_term_measures: List[Dict] = Field(..., description="长期措施建议")
    compliance_checklist: List[str] = Field(..., description="合规检查清单")
    risk_mitigation_strategies: List[str] = Field(..., description="风险缓解策略")
    reference_cases: List[Dict] = Field(..., description="参考案例")
    estimated_cost: Dict = Field(..., description="预估成本")
    timeline: Dict = Field(..., description="时间线")


# ==================== API路由 ====================

@app.get("/", tags=["Root"])
async def root():
    """根路径"""
    return {
        "name": "电商合规哨兵 API",
        "version": "0.2.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "predict": "/predict",
            "fine_predict": "/fine_predict",
            "knowledge_graph": "/knowledge_graph/search",
            "suggestions": "/suggestions",
            "risk_types": "/risk_types"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """健康检查"""
    checker = get_health_checker()
    return checker.check_all()


@app.get("/health/metrics", tags=["Health"])
async def health_metrics():
    """系统监控指标"""
    checker = get_health_checker()
    return checker.get_system_metrics()


@app.get("/health/live", tags=["Health"])
async def health_live():
    """存活检查（Kubernetes liveness probe）"""
    return {"status": "alive"}


@app.get("/health/ready", tags=["Health"])
async def health_ready():
    """就绪检查（Kubernetes readiness probe）"""
    checker = get_health_checker()
    result = checker.check_all()
    if result["status"] == "healthy":
        return {"status": "ready"}
    raise HTTPException(status_code=503, detail="Service not ready")


@app.post("/predict", response_model=PredictResponse, tags=["Risk Prediction"])
async def predict_risk(request: PredictRequest):
    """风险预测接口"""
    try:
        # 尝试从缓存获取
        cached_result = get_cached_prediction(request.platform_data)
        if cached_result:
            logger.info("Returning cached prediction result")
            return PredictResponse(**cached_result)

        predictor = get_risk_predictor()
        result = predictor.predict(
            platform_data=request.platform_data,
            risk_types=request.risk_types,
            horizon=request.horizon
        )

        # 缓存结果
        cache_prediction(request.platform_data, result, ttl=600)

        # 保存预测历史
        history = get_prediction_history()
        record = PredictionRecord(
            prediction_result=result,
            alerts_triggered=0,
            metadata={"horizon": request.horizon}
        )
        history.save_record(record)

        return PredictResponse(**result)
    except Exception as e:
        logger.error(f"Risk prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/fine_predict", response_model=FinePredictResponse, tags=["Fine Prediction"])
async def predict_fine(request: FinePredictRequest):
    """罚款预测接口"""
    try:
        predictor = get_fine_predictor()
        result = predictor.predict_fine(
            risk_type=request.risk_type,
            platform_data=request.platform_data,
            simulation_result=request.simulation_result
        )
        return FinePredictResponse(**result)
    except Exception as e:
        logger.error(f"Fine prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/knowledge_graph/search", response_model=KnowledgeGraphSearchResponse, tags=["Knowledge Graph"])
async def search_knowledge_graph(
    query: str = Query(..., description="搜索关键词"),
    search_type: str = Query("all", description="搜索类型"),
    limit: int = Query(10, ge=1, le=100, description="返回结果数量限制"),
):
    """知识图谱查询接口"""
    try:
        kg = get_knowledge_graph()
        results = []

        if search_type in ["case", "all"]:
            cases = kg.get_all_cases()
            for case in cases:
                if query.lower() in case.get("title", "").lower() or \
                   query.lower() in case.get("risk_type", "").lower():
                    results.append({
                        "type": "case",
                        "data": case
                    })

        if search_type in ["article", "all"]:
            for risk_type, articles in kg._legal_store.items():
                if query.lower() in risk_type.lower():
                    for article in articles:
                        results.append({
                            "type": "legal_article",
                            "risk_type": risk_type,
                            "data": article
                        })

        return KnowledgeGraphSearchResponse(
            results=results[:limit],
            total=len(results),
            query=query
        )
    except Exception as e:
        logger.error(f"Knowledge graph search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/knowledge_graph/cases", tags=["Knowledge Graph"])
async def get_all_cases():
    """获取所有案例"""
    kg = get_knowledge_graph()
    cases = kg.get_all_cases()
    return {"cases": cases, "total": len(cases)}


@app.get("/knowledge_graph/statistics", tags=["Knowledge Graph"])
async def get_statistics():
    """获取统计数据"""
    kg = get_knowledge_graph()
    stats = kg.get_risk_type_statistics()
    return {"statistics": stats}


@app.post("/suggestions", response_model=SuggestionResponse, tags=["Suggestions"])
async def generate_suggestions(request: SuggestionRequest):
    """应对建议生成接口"""
    try:
        generator = get_suggestion_generator()

        # 如果没有提供相似案例，从知识图谱获取
        similar_cases = request.similar_cases
        if not similar_cases:
            kg = get_knowledge_graph()
            similar_cases = kg.query_similar_cases(request.risk_type)

        result = generator.generate_suggestions(
            risk_type=request.risk_type,
            simulation_result=request.simulation_result,
            similar_cases=similar_cases
        )

        return SuggestionResponse(**result)
    except Exception as e:
        logger.error(f"Suggestion generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/risk_types", tags=["Reference"])
async def get_risk_types():
    """获取支持的风险类型列表"""
    risk_types = [
        {"name": "虚假宣传", "description": "产品宣传内容与实际不符"},
        {"name": "价格欺诈", "description": "虚构原价、虚假优惠等价格违法行为"},
        {"name": "产品质量问题", "description": "销售不符合标准的产品"},
        {"name": "知识产权侵权", "description": "侵犯他人商标、专利、著作权"},
        {"name": "个人信息泄露", "description": "违规收集、使用或泄露用户信息"},
        {"name": "不正当竞争", "description": "虚假评价、恶意竞争等行为"},
        {"name": "广告违法", "description": "违反广告法规定的广告行为"},
    ]
    return {"risk_types": risk_types}


# ==================== 法律数据库API ====================

@app.get("/laws/search", tags=["Laws"])
async def search_laws(
    query: str = Query(..., description="搜索关键词"),
    limit: int = Query(10, ge=1, le=100, description="返回结果数量限制")
):
    """搜索法律条文"""
    db = get_law_database()
    results = db.search_articles(query, limit)
    return {"results": results, "total": len(results), "query": query}


@app.get("/laws/by_risk_type/{risk_type}", tags=["Laws"])
async def get_laws_by_risk_type(risk_type: str):
    """根据风险类型获取相关法律条文"""
    db = get_law_database()
    articles = db.get_articles_by_risk_type(risk_type)
    return {"articles": articles, "total": len(articles), "risk_type": risk_type}


@app.get("/laws/statistics", tags=["Laws"])
async def get_law_statistics():
    """获取法律数据库统计信息"""
    db = get_law_database()
    return db.get_statistics()


# ==================== 多智能体API ====================

@app.post("/multi_agent/predict", tags=["Multi-Agent"])
async def multi_agent_predict(request: PredictRequest):
    """多智能体协作预测"""
    try:
        from .multi_agent import get_multi_agent_system

        system = get_multi_agent_system()
        result = system.predict(request.platform_data)

        return {
            "success": True,
            "data": result,
            "agent_status": system.get_agent_status()
        }
    except Exception as e:
        logger.error(f"Multi-agent prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/multi_agent/status", tags=["Multi-Agent"])
async def get_multi_agent_status():
    """获取多智能体系统状态"""
    try:
        from .multi_agent import get_multi_agent_system

        system = get_multi_agent_system()
        return {
            "status": "running",
            "agents": system.get_agent_status()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ==================== 报告导出API ====================

@app.post("/export/pdf", tags=["Export"])
async def export_pdf(request: Dict):
    """导出PDF报告"""
    try:
        # 简化实现：返回报告数据
        return {
            "success": True,
            "message": "PDF导出功能需要安装reportlab库",
            "data": request
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/export/json", tags=["Export"])
async def export_json(request: Dict):
    """导出JSON报告"""
    from datetime import datetime
    import json

    report = {
        "report_type": "电商合规风险预测报告",
        "generated_at": datetime.now().isoformat(),
        "data": request,
        "version": "0.4.0"
    }

    return report


# ==================== WebSocket实时推送 ====================

@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """预警WebSocket连接"""
    await websocket.accept()

    alert_manager = get_alert_manager()
    await alert_manager.ws_manager.connect(websocket)

    try:
        # 订阅预警主题
        await alert_manager.ws_manager.subscribe(websocket, "alerts")

        # 发送欢迎消息
        await websocket.send_json({
            "type": "connected",
            "message": "已连接到预警系统",
            "timestamp": datetime.now().isoformat()
        })

        # 保持连接，接收客户端消息
        while True:
            data = await websocket.receive_json()

            # 处理订阅请求
            if data.get("action") == "subscribe":
                topic = data.get("topic", "alerts")
                await alert_manager.ws_manager.subscribe(websocket, topic)
                await websocket.send_json({
                    "type": "subscribed",
                    "topic": topic
                })

            # 处理心跳
            elif data.get("action") == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        await alert_manager.ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await alert_manager.ws_manager.disconnect(websocket)


@app.get("/ws/stats", tags=["WebSocket"])
async def get_websocket_stats():
    """获取WebSocket连接统计"""
    alert_manager = get_alert_manager()
    return alert_manager.ws_manager.get_stats()


# ==================== 预警系统API ====================

@app.get("/alerts", tags=["Alerts"])
async def get_alerts(status: Optional[str] = None, limit: int = 50):
    """获取预警列表"""
    alert_manager = get_alert_manager()

    if status == "active":
        alerts = alert_manager.get_active_alerts()
    else:
        alerts = [
            {
                "alert_id": a.alert_id,
                "title": a.title,
                "message": a.message,
                "level": a.level.value,
                "status": a.status.value,
                "risk_type": a.risk_type,
                "probability": a.probability,
                "created_at": a.created_at
            }
            for a in alert_manager.alerts.values()
        ]

    return {"alerts": alerts[:limit], "total": len(alerts)}


@app.get("/alerts/stats", tags=["Alerts"])
async def get_alert_stats():
    """获取预警统计"""
    alert_manager = get_alert_manager()
    return alert_manager.get_alert_stats()


@app.post("/alerts/{alert_id}/acknowledge", tags=["Alerts"])
async def acknowledge_alert(alert_id: str):
    """确认预警"""
    alert_manager = get_alert_manager()
    success = alert_manager.acknowledge_alert(alert_id)

    if success:
        return {"success": True, "message": "预警已确认"}
    raise HTTPException(status_code=404, detail="预警不存在")


@app.post("/alerts/{alert_id}/resolve", tags=["Alerts"])
async def resolve_alert(alert_id: str):
    """解决预警"""
    alert_manager = get_alert_manager()
    success = alert_manager.resolve_alert(alert_id)

    if success:
        return {"success": True, "message": "预警已解决"}
    raise HTTPException(status_code=404, detail="预警不存在")


@app.get("/alerts/rules", tags=["Alerts"])
async def get_alert_rules():
    """获取预警规则"""
    alert_manager = get_alert_manager()
    return {"rules": alert_manager.rule_engine.get_rules()}


# ==================== 主动监控API ====================

@app.get("/monitor/status", tags=["Monitor"])
async def get_monitor_status():
    """获取主动监控状态"""
    monitor = get_proactive_monitor()
    return monitor.get_status()


@app.post("/monitor/items", tags=["Monitor"])
async def add_monitored_item(request: Dict):
    """添加监控项"""
    monitor = get_proactive_monitor()
    item_id = request.get("item_id", f"item_{datetime.now().timestamp()}")

    monitor.add_monitored_item(item_id, request)

    return {
        "success": True,
        "item_id": item_id,
        "message": "监控项已添加"
    }


@app.delete("/monitor/items/{item_id}", tags=["Monitor"])
async def remove_monitored_item(item_id: str):
    """移除监控项"""
    monitor = get_proactive_monitor()
    monitor.remove_monitored_item(item_id)

    return {"success": True, "message": "监控项已移除"}


@app.post("/monitor/start", tags=["Monitor"])
async def start_monitor():
    """启动主动监控"""
    monitor = get_proactive_monitor()
    await monitor.start()

    return {"success": True, "message": "主动监控已启动"}


@app.post("/monitor/stop", tags=["Monitor"])
async def stop_monitor():
    """停止主动监控"""
    monitor = get_proactive_monitor()
    await monitor.stop()

    return {"success": True, "message": "主动监控已停止"}


# ==================== 缓存管理API ====================

@app.get("/cache/stats", tags=["Cache"])
async def get_cache_stats():
    """获取缓存统计"""
    cache = get_global_cache()
    return cache.get_stats()


@app.delete("/cache/clear", tags=["Cache"])
async def clear_cache():
    """清空缓存"""
    cache = get_global_cache()
    cache.clear()
    return {"success": True, "message": "缓存已清空"}


# ==================== 限流管理API ====================

@app.get("/rate_limiter/stats", tags=["RateLimiter"])
async def get_rate_limiter_stats():
    """获取限流统计"""
    limiter = get_rate_limiter()
    return limiter.get_stats()


# ==================== 批量预测API ====================

class BatchPredictRequest(BaseModel):
    """批量预测请求模型"""
    items: List[Dict] = Field(..., description="批量预测数据列表")
    horizon: int = Field(30, ge=1, le=365, description="预测时间范围（天）")


class BatchPredictResponse(BaseModel):
    """批量预测响应模型"""
    results: List[Dict] = Field(..., description="预测结果列表")
    total: int = Field(..., description="总数量")
    success_count: int = Field(..., description="成功数量")
    failed_count: int = Field(..., description="失败数量")


@app.post("/predict/batch", response_model=BatchPredictResponse, tags=["Batch Prediction"])
async def batch_predict_risk(request: BatchPredictRequest):
    """批量风险预测接口"""
    predictor = get_risk_predictor()
    results = []
    success_count = 0
    failed_count = 0

    for item in request.items:
        try:
            result = predictor.predict(
                platform_data=item.get("platform_data", {}),
                risk_types=item.get("risk_types"),
                horizon=request.horizon
            )
            results.append({
                "success": True,
                "data": result,
                "item_id": item.get("id")
            })
            success_count += 1
        except Exception as e:
            results.append({
                "success": False,
                "error": str(e),
                "item_id": item.get("id")
            })
            failed_count += 1

    return BatchPredictResponse(
        results=results,
        total=len(request.items),
        success_count=success_count,
        failed_count=failed_count
    )


# ==================== 预测历史API ====================

@app.get("/history/records", tags=["History"])
async def get_prediction_records(limit: int = Query(50, ge=1, le=200)):
    """获取预测历史记录"""
    history = get_prediction_history()
    records = history.get_recent_records(limit)
    return {
        "records": [r.to_dict() for r in records],
        "total": len(records)
    }


@app.get("/history/statistics", tags=["History"])
async def get_history_statistics():
    """获取预测历史统计"""
    history = get_prediction_history()
    return history.get_statistics()


@app.get("/history/trend", tags=["History"])
async def get_history_trend(days: int = Query(7, ge=1, le=30)):
    """获取预测趋势数据"""
    history = get_prediction_history()
    return history.get_trend_data(days)


@app.get("/history/records/{record_id}", tags=["History"])
async def get_prediction_record(record_id: str):
    """获取单条预测记录"""
    history = get_prediction_history()
    record = history.get_record(record_id)

    if record:
        return record.to_dict()
    raise HTTPException(status_code=404, detail="记录不存在")


@app.delete("/history/records/{record_id}", tags=["History"])
async def delete_prediction_record(record_id: str):
    """删除预测记录"""
    history = get_prediction_history()
    success = history.delete_record(record_id)

    if success:
        return {"success": True, "message": "记录已删除"}
    raise HTTPException(status_code=404, detail="记录不存在")


# ==================== 实时预测API ====================

@app.post("/predict/realtime", tags=["Realtime"])
async def predict_realtime(request: PredictRequest):
    """实时预测并触发预警"""
    predictor = get_risk_predictor()

    # 执行预测
    result = predictor.predict(
        platform_data=request.platform_data,
        risk_types=request.risk_types,
        horizon=request.horizon
    )

    # 处理预警
    alert_manager = get_alert_manager()
    await alert_manager.process_risk_result(result)

    # 获取触发的预警
    active_alerts = alert_manager.get_active_alerts()

    return {
        "prediction": result,
        "alerts_triggered": len(active_alerts),
        "alerts": active_alerts[:5]
    }


# ==================== 任务队列API ====================

@app.post("/tasks/submit", tags=["Tasks"])
async def submit_task(request: Dict):
    """提交异步任务"""
    task_type = request.get("type", "predict")
    data = request.get("data", {})

    queue = get_task_queue()

    async def run_prediction():
        predictor = get_risk_predictor()
        return predictor.predict(platform_data=data)

    task_id = await queue.submit(
        name=f"async_{task_type}",
        func=run_prediction
    )

    return {
        "task_id": task_id,
        "status": "submitted",
        "message": "任务已提交"
    }


@app.get("/tasks/{task_id}", tags=["Tasks"])
async def get_task_status(task_id: str):
    """获取任务状态"""
    queue = get_task_queue()
    task = queue.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return {
        "task_id": task.task_id,
        "name": task.name,
        "status": task.status.value,
        "result": task.result,
        "error": task.error,
        "progress": task.progress,
        "created_at": task.created_at,
        "started_at": task.started_at,
        "completed_at": task.completed_at
    }


@app.get("/tasks", tags=["Tasks"])
async def list_tasks(status: Optional[str] = None, limit: int = 50):
    """获取任务列表"""
    queue = get_task_queue()

    task_status = None
    if status:
        task_status = TaskStatus(status)

    tasks = queue.get_all_tasks(status=task_status)

    return {
        "tasks": [
            {
                "task_id": t.task_id,
                "name": t.name,
                "status": t.status.value,
                "progress": t.progress,
                "created_at": t.created_at
            }
            for t in tasks[:limit]
        ],
        "total": len(tasks)
    }


@app.delete("/tasks/{task_id}", tags=["Tasks"])
async def cancel_task(task_id: str):
    """取消任务"""
    queue = get_task_queue()
    success = queue.cancel_task(task_id)

    if success:
        return {"success": True, "message": "任务已取消"}
    raise HTTPException(status_code=400, detail="无法取消任务")


@app.get("/tasks/stats", tags=["Tasks"])
async def get_task_stats():
    """获取任务统计"""
    queue = get_task_queue()
    return queue.get_stats()


# ==================== 前端页面 ====================

@app.get("/", tags=["Frontend"])
async def index():
    """前端首页"""
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {
        "name": "电商合规哨兵 API",
        "version": "0.3.0",
        "status": "running",
        "docs": "/docs",
        "frontend": "/static/index.html"
    }


# ==================== 启动配置 ====================

def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    logger.info("FastAPI application created")
    return app


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
