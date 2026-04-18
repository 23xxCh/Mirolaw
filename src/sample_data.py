# -*- coding: utf-8 -*-
"""
示例数据模块

提供电商违规案例的示例数据，用于系统演示和测试。
"""

from typing import Dict, List, Any
import random

# 示例平台数据
SAMPLE_PLATFORM_DATA = {
    "product_info": {
        "name": "智能健康手环Pro",
        "category": "智能穿戴",
        "description": "世界首创技术，全球唯一认证，治愈各种疾病",
        "price": 299.00,
        "original_price": 599.00
    },
    "sales_data": [
        {"date": "2024-01-01", "amount": 10000, "quantity": 50},
        {"date": "2024-01-02", "amount": 15000, "quantity": 75},
        {"date": "2024-01-03", "amount": 8000, "quantity": 40}
    ],
    "marketing_content": [
        {"type": "title", "text": "全球首创黑科技，世界第一智能手环"},
        {"type": "description", "text": "独家专利技术，唯一获得国际认证"},
        {"type": "claim", "text": "7天根治失眠，30天治愈高血压"}
    ],
    "customer_feedback": [
        {"rating": 5, "comment": "产品很好用"},
        {"rating": 4, "comment": "功能强大"},
        {"rating": 3, "comment": "一般般"}
    ],
    "company_size": "中型",
    "annual_revenue": 10000000,
    "violation_history": []
}

# 高风险示例数据
HIGH_RISK_PLATFORM_DATA = {
    "product_info": {
        "name": "神奇减肥茶",
        "category": "保健品",
        "description": "最有效的减肥产品，7天瘦20斤，100%纯天然，无副作用",
        "price": 199.00,
        "original_price": 999.00
    },
    "sales_data": [
        {"date": "2024-01-01", "amount": 50000, "quantity": 250}
    ],
    "marketing_content": [
        {"type": "title", "text": "世界第一减肥神器"},
        {"type": "description", "text": "国家级科研成果，央视推荐"},
        {"type": "claim", "text": "无需运动，躺着就能瘦，治愈肥胖症"}
    ],
    "customer_feedback": [],
    "company_size": "小型",
    "annual_revenue": 2000000,
    "violation_history": [
        {"type": "虚假宣传", "date": "2023-06-01", "fine": 50000}
    ]
}

# 低风险示例数据
LOW_RISK_PLATFORM_DATA = {
    "product_info": {
        "name": "纯棉T恤",
        "category": "服装",
        "description": "100%纯棉材质，舒适透气",
        "price": 59.00,
        "original_price": 79.00
    },
    "sales_data": [
        {"date": "2024-01-01", "amount": 5000, "quantity": 100}
    ],
    "marketing_content": [
        {"type": "title", "text": "夏季必备纯棉T恤"},
        {"type": "description", "text": "优质棉料，穿着舒适"}
    ],
    "customer_feedback": [
        {"rating": 5, "comment": "质量很好"},
        {"rating": 5, "comment": "穿着舒服"}
    ],
    "company_size": "小型",
    "annual_revenue": 500000,
    "violation_history": []
}


# 商品示例数据
SAMPLE_PRODUCTS = [
    {
        "id": "prod_001",
        "name": "智能空气净化器",
        "description": "采用独家专利技术，净化效率高达99.99%，全球首创五层过滤系统",
        "category": "家电",
        "price": 1299.00
    },
    {
        "id": "prod_002",
        "name": "有机绿茶",
        "description": "来自海拔1800米的高山茶园，纯天然无污染，具有减肥瘦身功效",
        "category": "食品",
        "price": 128.00
    },
    {
        "id": "prod_003",
        "name": "美白精华液",
        "description": "7天美白，28天换肤，100%有效，国家级认证产品",
        "category": "化妆品",
        "price": 299.00
    },
    {
        "id": "prod_004",
        "name": "儿童学习桌",
        "description": "符合人体工学设计，护眼防近视，畅销十年，家长首选",
        "category": "家具",
        "price": 1599.00
    },
    {
        "id": "prod_005",
        "name": "智能手表",
        "description": "世界第一的智能手表品牌，功能最全，质量最好，用户评价最高",
        "category": "电子产品",
        "price": 899.00
    },
    {
        "id": "prod_006",
        "name": "减肥胶囊",
        "description": "独家秘方，一周瘦10斤，无效全额退款，FDA认证",
        "category": "保健品",
        "price": 398.00
    },
    {
        "id": "prod_007",
        "name": "羽绒服",
        "description": "原价1999，现价399，限量100件，手慢无",
        "category": "服装",
        "price": 399.00
    },
    {
        "id": "prod_008",
        "name": "进口奶粉",
        "description": "100%原装进口，新西兰奶源，最接近母乳的配方",
        "category": "食品",
        "price": 368.00
    }
]


# 营销内容示例
SAMPLE_MARKETING = [
    {
        "id": "mkt_001",
        "type": "banner",
        "text": "双十一狂欢，全场1折起，错过等一年！",
        "position": "首页"
    },
    {
        "id": "mkt_002",
        "type": "video",
        "text": "央视推荐品牌，国家领导人同款",
        "position": "详情页"
    },
    {
        "id": "mkt_003",
        "type": "popup",
        "text": "限时秒杀，最后3件，抢到就是赚到！",
        "position": "弹窗"
    },
    {
        "id": "mkt_004",
        "type": "article",
        "text": "XX专家强烈推荐，治愈率98%",
        "position": "公众号"
    },
    {
        "id": "mkt_005",
        "type": "live",
        "text": "全网最低价，比竞品便宜50%，假一赔十",
        "position": "直播间"
    }
]


# 典型违规案例
VIOLATION_CASES = [
    {
        "case_id": "case_001",
        "title": "虚假宣传减肥功效",
        "description": "某电商宣称其减肥产品7天瘦30斤，实际无科学依据",
        "risk_type": "虚假宣传",
        "law": "广告法第28条",
        "penalty": "罚款20万元",
        "platform": "淘宝",
        "date": "2024-01-15"
    },
    {
        "case_id": "case_002",
        "title": "使用绝对化用语",
        "description": "商品详情页使用世界第一、最好等绝对化用语",
        "risk_type": "广告违法",
        "law": "广告法第9条",
        "penalty": "罚款10万元",
        "platform": "京东",
        "date": "2024-02-20"
    },
    {
        "case_id": "case_003",
        "title": "虚构原价促销",
        "description": "双十一期间标注原价1999现价399，实际从未以1999元销售",
        "risk_type": "价格欺诈",
        "law": "价格法第14条",
        "penalty": "罚款50万元",
        "platform": "天猫",
        "date": "2024-11-12"
    },
    {
        "case_id": "case_004",
        "title": "编造用户评价",
        "description": "雇佣刷单团队虚构交易和好评",
        "risk_type": "虚假宣传",
        "law": "电子商务法第17条",
        "penalty": "罚款30万元",
        "platform": "拼多多",
        "date": "2024-03-05"
    },
    {
        "case_id": "case_005",
        "title": "未经授权使用专利标识",
        "description": "产品宣传中标注专利标识，实际专利已过期",
        "risk_type": "知识产权侵权",
        "law": "广告法第12条",
        "penalty": "罚款15万元",
        "platform": "抖音电商",
        "date": "2024-04-10"
    },
    {
        "case_id": "case_006",
        "title": "销售假冒注册商标商品",
        "description": "销售假冒国际品牌运动鞋",
        "risk_type": "知识产权侵权",
        "law": "商标法第57条",
        "penalty": "罚款100万元，吊销营业执照",
        "platform": "微信小程序",
        "date": "2024-05-22"
    },
    {
        "case_id": "case_007",
        "title": "保健食品虚假宣传治疗功效",
        "description": "普通保健食品宣称可以治疗糖尿病",
        "risk_type": "虚假宣传",
        "law": "广告法第17条",
        "penalty": "罚款25万元",
        "platform": "快手电商",
        "date": "2024-06-18"
    },
    {
        "case_id": "case_008",
        "title": "个人信息泄露",
        "description": "未经用户同意将用户信息用于营销推广",
        "risk_type": "个人信息泄露",
        "law": "个人信息保护法第66条",
        "penalty": "罚款50万元",
        "platform": "自营APP",
        "date": "2024-07-30"
    }
]


def get_sample_data(risk_level: str = "medium") -> Dict:
    """获取示例数据"""
    if risk_level == "high":
        return HIGH_RISK_PLATFORM_DATA
    elif risk_level == "low":
        return LOW_RISK_PLATFORM_DATA
    else:
        return SAMPLE_PLATFORM_DATA


def get_all_sample_data() -> List[Dict]:
    """获取所有示例数据"""
    return [
        {"name": "标准示例", "data": SAMPLE_PLATFORM_DATA, "risk_level": "medium"},
        {"name": "高风险示例", "data": HIGH_RISK_PLATFORM_DATA, "risk_level": "high"},
        {"name": "低风险示例", "data": LOW_RISK_PLATFORM_DATA, "risk_level": "low"}
    ]


def generate_platform_data(
    product_id: str = None,
    include_marketing: bool = True,
    include_reviews: bool = True
) -> Dict[str, Any]:
    """
    生成平台数据

    Args:
        product_id: 指定商品ID，None则随机选择
        include_marketing: 是否包含营销内容
        include_reviews: 是否包含用户评价

    Returns:
        平台数据字典
    """
    # 选择商品
    if product_id:
        product = next((p for p in SAMPLE_PRODUCTS if p["id"] == product_id), SAMPLE_PRODUCTS[0])
    else:
        product = random.choice(SAMPLE_PRODUCTS)

    data = {
        "product_info": {
            "name": product["name"],
            "description": product["description"],
            "category": product["category"],
            "price": product["price"]
        }
    }

    if include_marketing:
        data["marketing_content"] = random.sample(
            SAMPLE_MARKETING,
            k=min(2, len(SAMPLE_MARKETING))
        )

    if include_reviews:
        data["customer_feedback"] = [
            {"rating": 5, "comment": "质量很好"},
            {"rating": 4, "comment": "性价比高"}
        ]

    return data


def get_violation_cases(risk_type: str = None) -> List[Dict]:
    """
    获取违规案例

    Args:
        risk_type: 风险类型筛选
    """
    if risk_type:
        return [c for c in VIOLATION_CASES if c["risk_type"] == risk_type]
    return VIOLATION_CASES


# 测试用例
TEST_CASES = [
    {
        "name": "虚假宣传检测测试",
        "platform_data": {
            "product_info": {
                "name": "测试产品",
                "description": "世界第一，全球首创"
            },
            "marketing_content": [
                {"text": "最先进的技术"}
            ]
        },
        "expected_risk_types": ["虚假宣传"]
    },
    {
        "name": "价格欺诈检测测试",
        "platform_data": {
            "product_info": {
                "name": "促销商品",
                "description": "限时特价"
            },
            "marketing_content": [
                {"text": "原价999，现价99"}
            ]
        },
        "expected_risk_types": ["价格欺诈"]
    }
]


def run_tests():
    """运行测试"""
    from .predictor import RiskPredictor

    predictor = RiskPredictor(config={})
    results = []

    for test_case in TEST_CASES:
        result = predictor.predict(test_case["platform_data"])
        results.append({
            "name": test_case["name"],
            "result": result
        })

    return results


if __name__ == "__main__":
    # 演示使用
    print("=== 示例数据演示 ===")
    print()
    print("1. 标准示例数据:")
    print("   产品名称:", SAMPLE_PLATFORM_DATA["product_info"]["name"])
    print("   产品描述:", SAMPLE_PLATFORM_DATA["product_info"]["description"])
    print()
    print("2. 高风险示例数据:")
    print("   产品名称:", HIGH_RISK_PLATFORM_DATA["product_info"]["name"])
    print("   产品描述:", HIGH_RISK_PLATFORM_DATA["product_info"]["description"])
    print()
    print("3. 低风险示例数据:")
    print("   产品名称:", LOW_RISK_PLATFORM_DATA["product_info"]["name"])
    print("   产品描述:", LOW_RISK_PLATFORM_DATA["product_info"]["description"])
    print()
    print("4. 典型违规案例:")
    for case in VIOLATION_CASES[:3]:
        print("   -", case["title"], ":", case["penalty"])
