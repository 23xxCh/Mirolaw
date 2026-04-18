"""
应对建议生成模块

本模块负责基于风险预测结果和历史案例，生成针对性的合规应对建议。
"""

from typing import Dict, List, Optional
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)


# 风险类型对应的建议模板
RISK_SUGGESTIONS = {
    "虚假宣传": {
        "immediate_actions": [
            {"action": "立即下架涉嫌虚假宣传的商品", "priority": "高", "estimated_time": "1天", "responsible_party": "运营部"},
            {"action": "审查所有营销文案，删除绝对化用语", "priority": "高", "estimated_time": "2-3天", "responsible_party": "市场部"},
            {"action": "修改产品描述，确保内容真实准确", "priority": "高", "estimated_time": "1-2天", "responsible_party": "产品部"},
            {"action": "保留修改记录作为整改证据", "priority": "中", "estimated_time": "1天", "responsible_party": "法务部"}
        ],
        "checklist": [
            "产品功效是否有科学依据支持",
            "是否使用了'最'、'第一'等绝对化用语",
            "宣传图片是否经过PS过度处理",
            "用户评价是否真实有效",
            "价格对比是否真实存在"
        ],
        "mitigation_strategies": [
            "建立营销内容三级审核机制",
            "定期开展广告法合规培训",
            "引入第三方内容审核服务",
            "建立用户投诉快速响应机制"
        ]
    },
    "价格欺诈": {
        "immediate_actions": [
            {"action": "停止虚假促销活动", "priority": "高", "estimated_time": "立即", "responsible_party": "运营部"},
            {"action": "核实并修正商品原价标注", "priority": "高", "estimated_time": "1-2天", "responsible_party": "产品部"},
            {"action": "清理虚假折扣信息", "priority": "高", "estimated_time": "1天", "responsible_party": "市场部"}
        ],
        "checklist": [
            "原价是否真实存在过",
            "折扣计算是否准确",
            "限时促销是否真实限时",
            "价格对比是否合理"
        ],
        "mitigation_strategies": [
            "建立价格审核机制",
            "保留历史价格记录",
            "规范促销活动流程",
            "定期价格合规自查"
        ]
    },
    "知识产权侵权": {
        "immediate_actions": [
            {"action": "立即下架涉嫌侵权商品", "priority": "高", "estimated_time": "立即", "responsible_party": "运营部"},
            {"action": "核实商品授权证明文件", "priority": "高", "estimated_time": "1-2天", "responsible_party": "采购部"},
            {"action": "联系权利人确认授权状态", "priority": "高", "estimated_time": "2-3天", "responsible_party": "法务部"}
        ],
        "checklist": [
            "是否有品牌授权证明",
            "商品来源是否正规",
            "商标使用是否合规",
            "专利是否侵权"
        ],
        "mitigation_strategies": [
            "建立供应商资质审核机制",
            "要求提供授权证明文件",
            "定期检查商品知识产权状态",
            "建立侵权投诉处理流程"
        ]
    },
    "产品质量问题": {
        "immediate_actions": [
            {"action": "暂停销售问题产品", "priority": "高", "estimated_time": "立即", "responsible_party": "运营部"},
            {"action": "召回已售出的问题产品", "priority": "高", "estimated_time": "3-5天", "responsible_party": "客服部"},
            {"action": "联系质检部门进行检测", "priority": "高", "estimated_time": "5-7天", "responsible_party": "质量部"}
        ],
        "checklist": [
            "产品是否有质检报告",
            "是否符合国家/行业标准",
            "是否有3C认证等必要认证",
            "产品标识是否完整"
        ],
        "mitigation_strategies": [
            "建立供应商质量审核机制",
            "定期抽检产品质量",
            "建立产品质量追溯体系",
            "完善产品召回机制"
        ]
    },
    "个人信息泄露": {
        "immediate_actions": [
            {"action": "排查数据收集流程合规性", "priority": "高", "estimated_time": "2-3天", "responsible_party": "技术部"},
            {"action": "检查隐私政策是否完整披露", "priority": "高", "estimated_time": "1-2天", "responsible_party": "法务部"},
            {"action": "加强数据访问权限控制", "priority": "高", "estimated_time": "3-5天", "responsible_party": "技术部"}
        ],
        "checklist": [
            "是否获得用户明确授权",
            "隐私政策是否完整",
            "数据存储是否安全",
            "是否有数据泄露风险"
        ],
        "mitigation_strategies": [
            "定期进行安全评估",
            "加强员工数据安全培训",
            "建立数据泄露应急预案",
            "引入第三方安全审计"
        ]
    },
    "不正当竞争": {
        "immediate_actions": [
            {"action": "停止刷单刷评行为", "priority": "高", "estimated_time": "立即", "responsible_party": "运营部"},
            {"action": "清理虚假评价数据", "priority": "高", "estimated_time": "1-2天", "responsible_party": "技术部"},
            {"action": "停止好评返现活动", "priority": "高", "estimated_time": "立即", "responsible_party": "市场部"}
        ],
        "checklist": [
            "用户评价是否真实",
            "交易数据是否真实",
            "是否存在刷单行为",
            "是否有恶意竞争行为"
        ],
        "mitigation_strategies": [
            "建立真实评价激励机制",
            "加强平台规则合规",
            "定期数据合规审计",
            "建立竞争合规制度"
        ]
    },
    "广告违法": {
        "immediate_actions": [
            {"action": "下架违法广告内容", "priority": "高", "estimated_time": "立即", "responsible_party": "运营部"},
            {"action": "审查广告内容合规性", "priority": "高", "estimated_time": "2-3天", "responsible_party": "法务部"},
            {"action": "修改违法广告内容", "priority": "高", "estimated_time": "1-2天", "responsible_party": "设计部"}
        ],
        "checklist": [
            "广告内容是否符合广告法",
            "是否使用禁用词汇",
            "医疗广告是否合规",
            "特殊商品广告是否审批"
        ],
        "mitigation_strategies": [
            "建立广告内容审核机制",
            "定期广告法合规培训",
            "引入专业法务审核",
            "建立广告档案管理"
        ]
    }
}


class SuggestionGenerator:
    """
    应对建议生成器

    支持LLM和规则引擎两种模式生成合规应对建议。
    支持DeepSeek、OpenAI等LLM提供商。
    """

    def __init__(self, llm_client=None) -> None:
        """初始化建议生成器"""
        self.llm_client = llm_client
        self.use_llm = False

        # 检查是否启用LLM
        if os.getenv("ENABLE_LLM", "false").lower() == "true":
            # 如果没有提供client，尝试创建DeepSeek client
            if llm_client is None:
                self.llm_client = self._create_deepseek_client()
            if self.llm_client is not None:
                self.use_llm = True

        logger.info(f"SuggestionGenerator initialized (LLM mode: {self.use_llm})")

    def _create_deepseek_client(self):
        """创建DeepSeek API客户端"""
        try:
            from openai import OpenAI

            api_key = os.getenv("DEEPSEEK_API_KEY")
            base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

            if api_key:
                client = OpenAI(
                    api_key=api_key,
                    base_url=base_url
                )
                logger.info(f"DeepSeek client created with base_url: {base_url}")
                return client
        except Exception as e:
            logger.error(f"Failed to create DeepSeek client: {e}")

        return None

    def generate_suggestions(
        self,
        risk_type: str,
        simulation_result: Dict,
        similar_cases: List
    ) -> Dict:
        """生成应对建议"""
        if self.use_llm:
            suggestions = self._generate_with_llm(risk_type, simulation_result, similar_cases)
        else:
            suggestions = self._generate_with_rules(risk_type, simulation_result, similar_cases)

        logger.info(f"Generated suggestions for risk type: {risk_type}")
        return suggestions

    def _generate_with_rules(
        self,
        risk_type: str,
        simulation_result: Dict,
        similar_cases: List
    ) -> Dict:
        """使用规则引擎生成建议"""
        template = RISK_SUGGESTIONS.get(risk_type, RISK_SUGGESTIONS["虚假宣传"])

        # 根据风险等级调整建议
        risk_level = simulation_result.get("risk_level", "中")
        probability = simulation_result.get("probability", 0.5)

        immediate_actions = self._adjust_actions_by_risk(
            template["immediate_actions"],
            risk_level
        )

        suggestions = {
            "immediate_actions": immediate_actions,
            "long_term_measures": self._generate_long_term_measures(risk_type),
            "compliance_checklist": template["checklist"],
            "risk_mitigation_strategies": template["mitigation_strategies"],
            "reference_cases": self._summarize_reference_cases(similar_cases),
            "estimated_cost": self._estimate_cost(probability, risk_type),
            "timeline": {
                "immediate": "1-3天",
                "short_term": "1-2周",
                "long_term": "1-3个月"
            },
            "generated_at": datetime.now().isoformat(),
            "generation_method": "rule-based"
        }

        return suggestions

    def _generate_with_llm(
        self,
        risk_type: str,
        simulation_result: Dict,
        similar_cases: List
    ) -> Dict:
        """使用LLM生成建议"""
        prompt = self._build_prompt(risk_type, simulation_result, similar_cases)

        try:
            # 获取模型名称
            model = os.getenv("LLM_MODEL", "deepseek-chat")

            # 调用LLM
            response = self.llm_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )

            llm_suggestions = self._parse_llm_response(response.choices[0].message.content)
            llm_suggestions["generation_method"] = "llm"
            llm_suggestions["generated_at"] = datetime.now().isoformat()
            llm_suggestions["model"] = model

            return llm_suggestions

        except Exception as e:
            logger.error(f"LLM generation failed: {e}, falling back to rules")
            return self._generate_with_rules(risk_type, simulation_result, similar_cases)

    def _adjust_actions_by_risk(self, actions: List, risk_level: str) -> List:
        """根据风险等级调整行动建议"""
        adjusted = []
        for action in actions:
            adjusted_action = action.copy()
            if risk_level == "高":
                adjusted_action["priority"] = "高"
            elif risk_level == "低":
                if action["priority"] == "高":
                    adjusted_action["priority"] = "中"
            adjusted.append(adjusted_action)
        return adjusted

    def _generate_long_term_measures(self, risk_type: str) -> List:
        """生成长期措施建议"""
        measures = [
            {
                "measure": "建立内容审核机制",
                "implementation_steps": [
                    "制定审核标准和流程",
                    "培训审核人员",
                    "建立审核系统",
                    "定期审核效果评估"
                ],
                "expected_outcome": "降低违规风险80%",
                "timeline": "1-2个月"
            },
            {
                "measure": "开展合规培训",
                "implementation_steps": [
                    "制定培训计划",
                    "组织定期培训",
                    "考核培训效果",
                    "更新培训内容"
                ],
                "expected_outcome": "提升员工合规意识",
                "timeline": "持续进行"
            },
            {
                "measure": "建立合规监控体系",
                "implementation_steps": [
                    "部署监控工具",
                    "设置预警阈值",
                    "建立响应机制",
                    "定期评估优化"
                ],
                "expected_outcome": "实时发现合规风险",
                "timeline": "2-3个月"
            }
        ]
        return measures

    def _estimate_cost(self, probability: float, risk_type: str) -> Dict:
        """预估整改成本"""
        # 基础成本范围
        base_costs = {
            "虚假宣传": (5000, 50000),
            "价格欺诈": (3000, 30000),
            "知识产权侵权": (10000, 100000),
            "产品质量问题": (20000, 200000),
            "个人信息泄露": (50000, 500000),
            "不正当竞争": (10000, 100000),
            "广告违法": (5000, 50000)
        }

        min_cost, max_cost = base_costs.get(risk_type, (5000, 50000))

        # 根据概率调整
        adjusted_min = round(min_cost * (0.5 + probability * 0.5), 2)
        adjusted_max = round(max_cost * (0.5 + probability * 0.5), 2)

        return {
            "min": adjusted_min,
            "max": adjusted_max,
            "currency": "CNY",
            "note": "预估整改成本，不含潜在罚款"
        }

    def _summarize_reference_cases(self, cases: List) -> List:
        """总结参考案例"""
        summaries = []
        for case in cases[:3]:
            summary = {
                "case_id": case.get("case_id"),
                "title": case.get("title", "未知案例"),
                "fine_amount": case.get("fine_amount", 0),
                "company_size": case.get("company_size", "未知"),
                "key_lesson": self._extract_key_lesson(case)
            }
            summaries.append(summary)
        return summaries

    def _extract_key_lesson(self, case: Dict) -> str:
        """提取案例关键教训"""
        risk_type = case.get("risk_type", "")
        fine_amount = case.get("fine_amount", 0)

        if fine_amount > 500000:
            return f"高额罚款案例，需高度重视{risk_type}风险"
        elif fine_amount > 200000:
            return f"中等罚款案例，应加强{risk_type}合规"
        else:
            return f"一般案例，注意{risk_type}合规要求"

    def _build_prompt(self, risk_type: str, simulation_result: Dict, similar_cases: List) -> str:
        """构建LLM提示词"""
        prompt = f"""
你是一位资深的电商合规专家。请基于以下信息，为电商平台提供针对性的合规应对建议。

风险类型: {risk_type}

风险预测结果:
- 发生概率: {simulation_result.get('probability', 0):.2%}
- 风险等级: {simulation_result.get('risk_level', '未知')}
- 置信度: {simulation_result.get('confidence', 0):.2%}

相似历史案例:
{self._format_cases_for_prompt(similar_cases)}

请提供以下方面的建议（JSON格式）:
1. immediate_actions: 立即行动建议列表
2. long_term_measures: 长期措施建议
3. compliance_checklist: 合规检查清单
4. risk_mitigation_strategies: 风险缓解策略

要求:
- 建议具体可执行
- 考虑成本效益
- 参考历史案例
- 符合法律法规
"""
        return prompt

    def _format_cases_for_prompt(self, cases: List) -> str:
        """格式化案例用于提示词"""
        if not cases:
            return "暂无相似案例"

        formatted = []
        for i, case in enumerate(cases[:5], 1):
            formatted.append(
                f"{i}. {case.get('title', '未知案例')} "
                f"- 罚款: {case.get('fine_amount', 0)}元"
            )
        return "\n".join(formatted)

    def _parse_llm_response(self, response: str) -> Dict:
        """解析LLM响应"""
        import json
        try:
            return json.loads(response)
        except:
            return {
                "immediate_actions": [],
                "long_term_measures": [],
                "compliance_checklist": [],
                "risk_mitigation_strategies": [],
                "raw_response": response
            }

    def refine_suggestions(
        self,
        suggestions: Dict,
        feedback: str
    ) -> Dict:
        """根据反馈优化建议"""
        if self.use_llm:
            # 使用LLM优化
            prompt = f"请根据以下反馈优化合规建议:\n原建议: {suggestions}\n反馈: {feedback}"
            try:
                response = self.llm_client.chat.completions.create(
                    model=os.getenv("LLM_MODEL", "gpt-3.5-turbo"),
                    messages=[{"role": "user", "content": prompt}]
                )
                return self._parse_llm_response(response.choices[0].message.content)
            except Exception as e:
                logger.error(f"LLM refinement failed: {e}")

        logger.info("Refining suggestions based on feedback")
        return suggestions
