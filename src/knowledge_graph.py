"""
法律知识图谱模块

本模块负责构建和管理法律知识图谱，包括法律条文、案例、
风险类型的关联关系存储和查询。
"""

from typing import Dict, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


# 预置示例数据
SAMPLE_CASES = [
    {
        "case_id": "CASE2024001",
        "title": "某电商虚假宣传案",
        "risk_type": "虚假宣传",
        "fine_amount": 500000,
        "company_name": "某科技有限公司",
        "company_size": "中型",
        "decision_date": "2024-01-15",
        "legal_articles": ["广告法第4条", "广告法第28条"],
        "summary": "该公司在电商平台销售产品时，宣称产品具有'世界第一'功效，构成虚假宣传"
    },
    {
        "case_id": "CASE2024002",
        "title": "某平台价格欺诈案",
        "risk_type": "价格欺诈",
        "fine_amount": 300000,
        "company_name": "某贸易有限公司",
        "company_size": "小型",
        "decision_date": "2024-02-20",
        "legal_articles": ["价格法第14条"],
        "summary": "虚构原价进行虚假优惠促销，欺骗消费者"
    },
    {
        "case_id": "CASE2024003",
        "title": "某品牌知识产权侵权案",
        "risk_type": "知识产权侵权",
        "fine_amount": 800000,
        "company_name": "某电子商务公司",
        "company_size": "中型",
        "decision_date": "2024-03-10",
        "legal_articles": ["商标法第57条"],
        "summary": "销售侵犯注册商标专用权的商品"
    },
    {
        "case_id": "CASE2024004",
        "title": "某商家虚假宣传保健品案",
        "risk_type": "虚假宣传",
        "fine_amount": 200000,
        "company_name": "某健康科技公司",
        "company_size": "小型",
        "decision_date": "2024-01-25",
        "legal_articles": ["广告法第4条", "食品安全法第73条"],
        "summary": "保健品宣传治疗功效，误导消费者"
    },
    {
        "case_id": "CASE2024005",
        "title": "某平台虚构交易案",
        "risk_type": "不正当竞争",
        "fine_amount": 450000,
        "company_name": "某网络科技公司",
        "company_size": "中型",
        "decision_date": "2024-02-15",
        "legal_articles": ["反不正当竞争法第8条"],
        "summary": "通过刷单刷评虚构交易数据"
    },
    {
        "case_id": "CASE2024006",
        "title": "某商家价格欺诈案",
        "risk_type": "价格欺诈",
        "fine_amount": 150000,
        "company_name": "某商贸有限公司",
        "company_size": "小型",
        "decision_date": "2024-03-05",
        "legal_articles": ["价格法第14条"],
        "summary": "先涨价后降价，虚假促销"
    },
    {
        "case_id": "CASE2024007",
        "title": "某店铺销售假冒商品案",
        "risk_type": "知识产权侵权",
        "fine_amount": 600000,
        "company_name": "某服饰公司",
        "company_size": "小型",
        "decision_date": "2024-02-28",
        "legal_articles": ["商标法第57条", "消费者权益保护法第56条"],
        "summary": "销售假冒知名品牌服装"
    },
    # 新增案例
    {
        "case_id": "CASE2024008",
        "title": "某电商平台用户信息泄露案",
        "risk_type": "个人信息泄露",
        "fine_amount": 1000000,
        "company_name": "某互联网科技公司",
        "company_size": "大型",
        "decision_date": "2024-03-20",
        "legal_articles": ["个人信息保护法第66条"],
        "summary": "违规收集用户个人信息并出售给第三方，涉及用户数据500万条"
    },
    {
        "case_id": "CASE2024009",
        "title": "某食品电商销售三无产品案",
        "risk_type": "产品质量问题",
        "fine_amount": 350000,
        "company_name": "某食品贸易公司",
        "company_size": "小型",
        "decision_date": "2024-01-30",
        "legal_articles": ["产品质量法第49条", "食品安全法第124条"],
        "summary": "销售无生产日期、无质量合格证、无生产厂家的三无食品"
    },
    {
        "case_id": "CASE2024010",
        "title": "某医美平台违法广告案",
        "risk_type": "广告违法",
        "fine_amount": 800000,
        "company_name": "某医疗美容平台",
        "company_size": "中型",
        "decision_date": "2024-02-10",
        "legal_articles": ["广告法第17条", "医疗广告管理办法"],
        "summary": "发布未经审查的医疗美容广告，使用患者形象作证明"
    },
    {
        "case_id": "CASE2024011",
        "title": "某直播电商虚假宣传案",
        "risk_type": "虚假宣传",
        "fine_amount": 1200000,
        "company_name": "某直播带货公司",
        "company_size": "大型",
        "decision_date": "2024-03-15",
        "legal_articles": ["广告法第4条", "电子商务法第17条"],
        "summary": "主播虚假宣传产品功效，虚构原价，夸大产品效果"
    },
    {
        "case_id": "CASE2024012",
        "title": "某跨境电商售假案",
        "risk_type": "知识产权侵权",
        "fine_amount": 2000000,
        "company_name": "某跨境电商平台",
        "company_size": "大型",
        "decision_date": "2024-03-25",
        "legal_articles": ["商标法第57条", "电子商务法第38条"],
        "summary": "平台明知商家销售假冒国际品牌商品未采取措施"
    },
    {
        "case_id": "CASE2024013",
        "title": "某母婴电商虚假促销案",
        "risk_type": "价格欺诈",
        "fine_amount": 250000,
        "company_name": "某母婴用品公司",
        "company_size": "小型",
        "decision_date": "2024-01-18",
        "legal_articles": ["价格法第14条"],
        "summary": "虚构原价进行虚假打折促销，实际价格高于日常售价"
    },
    {
        "case_id": "CASE2024014",
        "title": "某社交电商刷单案",
        "risk_type": "不正当竞争",
        "fine_amount": 600000,
        "company_name": "某社交电商平台",
        "company_size": "中型",
        "decision_date": "2024-02-25",
        "legal_articles": ["反不正当竞争法第8条", "电子商务法第17条"],
        "summary": "组织刷单刷评，虚构交易数据和用户评价"
    },
    {
        "case_id": "CASE2024015",
        "title": "某数码电商产品质量案",
        "risk_type": "产品质量问题",
        "fine_amount": 500000,
        "company_name": "某数码科技公司",
        "company_size": "中型",
        "decision_date": "2024-03-08",
        "legal_articles": ["产品质量法第49条", "消费者权益保护法第56条"],
        "summary": "销售未经3C认证的电子产品，存在安全隐患"
    },
]

SAMPLE_LEGAL_BASIS = {
    "虚假宣传": [
        {
            "article_id": "第4条",
            "law_name": "中华人民共和国广告法",
            "article_content": "广告不得含有虚假或者引人误解的内容，不得欺骗、误导消费者。",
            "penalty_clause": "违反本法规定，由市场监督管理部门责令停止发布广告，处以罚款。",
            "applicability": "适用于所有商业广告宣传行为"
        },
        {
            "article_id": "第28条",
            "law_name": "中华人民共和国广告法",
            "article_content": "广告以虚假或者引人误解的内容欺骗、误导消费者的，构成虚假广告。",
            "penalty_clause": "由市场监督管理部门责令停止发布广告，处广告费用3倍以上5倍以下罚款。",
            "applicability": "适用于商品性能、功能等虚假宣传"
        }
    ],
    "价格欺诈": [
        {
            "article_id": "第14条",
            "law_name": "中华人民共和国价格法",
            "article_content": "经营者不得有下列不正当价格行为：（四）利用虚假的或者使人误解的价格手段，诱骗消费者或者其他经营者与其进行交易。",
            "penalty_clause": "责令改正，没收违法所得，可以并处违法所得5倍以下罚款。",
            "applicability": "适用于虚构原价、虚假优惠等行为"
        }
    ],
    "知识产权侵权": [
        {
            "article_id": "第57条",
            "law_name": "中华人民共和国商标法",
            "article_content": "有下列行为之一的，均属侵犯注册商标专用权：（三）销售侵犯注册商标专用权的商品的。",
            "penalty_clause": "责令立即停止侵权行为，没收、销毁侵权商品，处以罚款。",
            "applicability": "适用于销售假冒商品行为"
        }
    ],
    "不正当竞争": [
        {
            "article_id": "第8条",
            "law_name": "中华人民共和国反不正当竞争法",
            "article_content": "经营者不得对其商品的性能、功能、质量、销售状况、用户评价、曾获荣誉等作虚假或者引人误解的商业宣传，欺骗、误导消费者。",
            "penalty_clause": "由监督检查部门责令停止违法行为，处二十万元以上一百万元以下罚款。",
            "applicability": "适用于刷单刷评、虚假交易等行为"
        }
    ],
    "产品质量问题": [
        {
            "article_id": "第49条",
            "law_name": "中华人民共和国产品质量法",
            "article_content": "生产、销售不符合保障人体健康和人身、财产安全的国家标准、行业标准的产品的。",
            "penalty_clause": "责令停止生产、销售，没收违法生产、销售的产品，并处货值金额等值以上三倍以下罚款。",
            "applicability": "适用于产品质量不达标行为"
        }
    ],
    "个人信息泄露": [
        {
            "article_id": "第66条",
            "law_name": "中华人民共和国个人信息保护法",
            "article_content": "违反本法规定处理个人信息，或者处理个人信息未履行本法规定的个人信息保护义务的。",
            "penalty_clause": "由履行个人信息保护职责的部门责令改正，给予警告，没收违法所得，处以罚款。",
            "applicability": "适用于违规收集、使用用户信息"
        }
    ],
    "广告违法": [
        {
            "article_id": "第9条",
            "law_name": "中华人民共和国广告法",
            "article_content": "广告不得有下列情形：（一）使用或者变相使用中华人民共和国国旗、国歌、国徽；（二）使用国家机关、国家机关工作人员的名义或者形象。",
            "penalty_clause": "由市场监督管理部门责令停止发布广告，处二十万元以上一百万元以下罚款。",
            "applicability": "适用于违法广告内容"
        }
    ]
}


class LegalKnowledgeGraph:
    """
    法律知识图谱

    使用内存存储法律知识，支持案例相似性检索和法律依据查询。

    Attributes:
        uri (str): 图数据库连接URI
        user (str): 数据库用户名
        password (str): 数据库密码
        driver: 图数据库驱动实例
        _cases_store (dict): 内存案例存储
        _legal_store (dict): 内存法律条文存储
    """

    def __init__(
        self,
        uri: str = "memory://localhost",
        user: str = "default",
        password: str = "default"
    ) -> None:
        """初始化知识图谱"""
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None

        # 内存存储
        self._cases_store = {case["case_id"]: case for case in SAMPLE_CASES}
        self._legal_store = SAMPLE_LEGAL_BASIS

        self._connect()
        logger.info("LegalKnowledgeGraph initialized successfully")

    def _connect(self) -> None:
        """建立数据库连接"""
        logger.info(f"Using in-memory storage at {self.uri}")

    def initialize_graph(self) -> None:
        """初始化知识图谱"""
        logger.info("Knowledge graph initialized with sample data")

    def query_similar_cases(self, risk_type: str) -> List:
        """查询相似案例"""
        logger.info(f"Querying similar cases for risk type: {risk_type}")

        cases = [
            case for case in self._cases_store.values()
            if case.get("risk_type") == risk_type
        ]

        # 按日期排序
        cases.sort(key=lambda x: x.get("decision_date", ""), reverse=True)

        return cases

    def get_legal_basis(self, risk_type: str) -> List:
        """获取法律依据"""
        logger.info(f"Querying legal basis for risk type: {risk_type}")

        return self._legal_store.get(risk_type, [])

    def add_case(self, case_data: Dict) -> bool:
        """添加新案例"""
        case_id = case_data.get("case_id")
        if not case_id:
            logger.error("case_id is required")
            return False

        case_data["created_at"] = datetime.now().isoformat()
        self._cases_store[case_id] = case_data

        logger.info(f"Added case {case_id} to knowledge graph")
        return True

    def update_case(self, case_id: str, update_data: Dict) -> bool:
        """更新案例"""
        if case_id not in self._cases_store:
            logger.error(f"Case {case_id} not found")
            return False

        self._cases_store[case_id].update(update_data)
        logger.info(f"Updated case {case_id}")
        return True

    def delete_case(self, case_id: str) -> bool:
        """删除案例"""
        if case_id in self._cases_store:
            del self._cases_store[case_id]
            logger.info(f"Deleted case {case_id}")
            return True
        return False

    def get_risk_type_statistics(self) -> Dict:
        """获取风险类型统计"""
        stats = {}
        for case in self._cases_store.values():
            risk_type = case.get("risk_type")
            if risk_type not in stats:
                stats[risk_type] = {
                    "count": 0,
                    "total_fine": 0,
                    "avg_fine": 0
                }
            stats[risk_type]["count"] += 1
            stats[risk_type]["total_fine"] += case.get("fine_amount", 0)

        for risk_type in stats:
            count = stats[risk_type]["count"]
            stats[risk_type]["avg_fine"] = stats[risk_type]["total_fine"] / count if count > 0 else 0

        return stats

    def get_all_cases(self) -> List:
        """获取所有案例"""
        return list(self._cases_store.values())

    def close(self) -> None:
        """关闭连接"""
        if self.driver:
            self.driver.close()
            logger.info("Knowledge graph connection closed")
