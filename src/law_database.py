"""
法律数据库模块

从公开法律数据源加载法律条文，提供法律知识查询功能。
数据来源：LawRefBook/Laws (https://github.com/LawRefBook/Laws)
"""

import json
import os
from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# 法律数据目录
DATA_DIR = Path(__file__).parent.parent / "data" / "laws"


# 预置电商相关法律条文
BUILTIN_LAWS = {
    "广告法": {
        "name": "中华人民共和国广告法",
        "articles": [
            {
                "article_id": "第4条",
                "content": "广告不得含有虚假或者引人误解的内容，不得欺骗、误导消费者。广告主应当对广告内容的真实性负责。",
                "keywords": ["虚假", "误导", "欺骗", "真实性"],
                "risk_types": ["虚假宣传", "广告违法"]
            },
            {
                "article_id": "第9条",
                "content": "广告不得有下列情形：（一）使用或者变相使用中华人民共和国国旗、国歌、国徽；（二）使用国家机关、国家机关工作人员的名义或者形象；（三）使用'国家级'、'最高级'、'最佳'等用语。",
                "keywords": ["国家级", "最高级", "最佳", "国旗", "国徽"],
                "risk_types": ["虚假宣传", "广告违法"]
            },
            {
                "article_id": "第11条",
                "content": "广告内容涉及事项需要取得行政许可的，应当与许可的内容相符合。广告使用数据、统计资料、调查结果、文摘、引用语等引证内容的，应当真实、准确，并表明出处。",
                "keywords": ["行政许可", "数据", "统计", "调查结果"],
                "risk_types": ["虚假宣传", "广告违法"]
            },
            {
                "article_id": "第12条",
                "content": "广告中涉及专利产品或者专利方法的，应当标明专利号和专利种类。未取得专利权的，不得在广告中谎称取得专利权。禁止使用未授予专利权的专利申请和已经终止、撤销、无效的专利作广告。",
                "keywords": ["专利", "专利号", "专利权"],
                "risk_types": ["虚假宣传", "知识产权侵权"]
            },
            {
                "article_id": "第17条",
                "content": "农药、兽药、饲料和饲料添加剂广告不得含有下列内容：（一）表示功效、安全性的断言或者保证；（二）说明有效率；（三）利用科研单位、学术机构、技术推广机构等作推荐、证明。",
                "keywords": ["功效", "有效率", "保证"],
                "risk_types": ["虚假宣传"]
            },
            {
                "article_id": "第25条",
                "content": "广告主或者广告经营者在广告中使用他人名义或者形象的，应当事先取得其书面同意；使用无民事行为能力人、限制民事行为能力人的名义或者形象的，应当事先取得其监护人的书面同意。",
                "keywords": ["名义", "形象", "书面同意"],
                "risk_types": ["广告违法"]
            },
            {
                "article_id": "第28条",
                "content": "广告以虚假或者引人误解的内容欺骗、误导消费者的，构成虚假广告。有下列情形之一的，为虚假广告：（一）商品或者服务不存在的；（二）商品的性能、功能、产地、用途、质量、价格、生产者、有效期限、销售状况、曾获荣誉等信息与实际情况不符的。",
                "keywords": ["虚假广告", "欺骗", "误导"],
                "risk_types": ["虚假宣传"]
            },
            {
                "article_id": "第55条",
                "content": "违反本法规定，发布虚假广告的，由工商行政管理部门责令停止发布广告，责令广告主在相应范围内消除影响，处广告费用三倍以上五倍以下的罚款。",
                "keywords": ["虚假广告", "罚款", "责令停止"],
                "risk_types": ["虚假宣传"]
            }
        ]
    },
    "价格法": {
        "name": "中华人民共和国价格法",
        "articles": [
            {
                "article_id": "第14条",
                "content": "经营者不得有下列不正当价格行为：（一）相互串通，操纵市场价格，损害其他经营者或者消费者的合法权益；（四）利用虚假的或者使人误解的价格手段，诱骗消费者或者其他经营者与其进行交易。",
                "keywords": ["串通", "操纵价格", "虚假", "诱骗"],
                "risk_types": ["价格欺诈"]
            },
            {
                "article_id": "第13条",
                "content": "经营者销售、收购商品和提供服务，应当按照政府价格主管部门的规定明码标价，注明商品的品名、产地、规格、等级、计价单位、价格或者服务的项目、收费标准等有关情况。",
                "keywords": ["明码标价", "价格", "收费标准"],
                "risk_types": ["价格欺诈"]
            },
            {
                "article_id": "第40条",
                "content": "经营者有本法第十四条所列行为之一的，责令改正，没收违法所得，可以并处违法所得五倍以下的罚款；没有违法所得的，予以警告，可以并处罚款。",
                "keywords": ["罚款", "没收违法所得", "责令改正"],
                "risk_types": ["价格欺诈"]
            },
            {
                "article_id": "第41条",
                "content": "经营者因价格违法行为致使消费者或者其他经营者多付价款的，应当退还多付部分；造成损害的，应当依法承担赔偿责任。",
                "keywords": ["退还", "赔偿", "多付价款"],
                "risk_types": ["价格欺诈"]
            }
        ]
    },
    "消费者权益保护法": {
        "name": "中华人民共和国消费者权益保护法",
        "articles": [
            {
                "article_id": "第8条",
                "content": "消费者享有知悉其购买、使用的商品或者接受的服务的真实情况的权利。消费者有权根据商品或者服务的不同情况，要求经营者提供商品的价格、产地、生产者、用途、性能、规格、等级、主要成份、生产日期、有效期限、检验合格证明、使用方法说明书、售后服务，或者服务的内容、规格、费用等有关情况。",
                "keywords": ["知悉", "真实情况", "价格", "产地", "性能"],
                "risk_types": ["虚假宣传"]
            },
            {
                "article_id": "第20条",
                "content": "经营者向消费者提供有关商品或者服务的质量、性能、用途、有效期限等信息，应当真实、全面，不得作虚假或者引人误解的宣传。经营者对消费者就其提供的商品或者服务的质量和使用方法等问题提出的询问，应当作出真实、明确的答复。",
                "keywords": ["真实", "全面", "虚假", "引人误解"],
                "risk_types": ["虚假宣传"]
            },
            {
                "article_id": "第23条",
                "content": "经营者应当保证在正常使用商品或者接受服务的情况下其提供的商品或者服务应当具有的质量、性能、用途和有效期限；但消费者在购买该商品或者接受该服务前已经知道其存在瑕疵，且存在该瑕疵不违反法律强制性规定的除外。",
                "keywords": ["质量", "性能", "有效期限", "瑕疵"],
                "risk_types": ["产品质量问题"]
            },
            {
                "article_id": "第45条",
                "content": "对国家规定或者经营者与消费者约定包修、包换、包退的商品，经营者应当负责修理、更换或者退货。在保修期内两次修理仍不能正常使用的，经营者应当负责更换或者退货。",
                "keywords": ["包修", "包换", "包退", "修理"],
                "risk_types": ["产品质量问题"]
            },
            {
                "article_id": "第55条",
                "content": "经营者提供商品或者服务有欺诈行为的，应当按照消费者的要求增加赔偿其受到的损失，增加赔偿的金额为消费者购买商品的价款或者接受服务的费用的三倍；增加赔偿的金额不足五百元的，为五百元。",
                "keywords": ["欺诈", "赔偿", "三倍"],
                "risk_types": ["虚假宣传", "价格欺诈"]
            },
            {
                "article_id": "第56条",
                "content": "经营者有下列情形之一，除承担相应的民事责任外，由工商行政管理部门或者其他有关行政部门责令改正，可以根据情节单处或者并处警告、没收违法所得、处以违法所得一倍以上十倍以下的罚款。",
                "keywords": ["罚款", "责令改正", "没收违法所得"],
                "risk_types": ["虚假宣传", "价格欺诈", "产品质量问题"]
            }
        ]
    },
    "电子商务法": {
        "name": "中华人民共和国电子商务法",
        "articles": [
            {
                "article_id": "第17条",
                "content": "电子商务经营者应当全面、真实、准确、及时地披露商品或者服务信息，保障消费者的知情权和选择权。电子商务经营者不得以虚构交易、编造用户评价等方式进行虚假或者引人误解的商业宣传，欺骗、误导消费者。",
                "keywords": ["虚构交易", "编造评价", "虚假宣传"],
                "risk_types": ["虚假宣传", "不正当竞争"]
            },
            {
                "article_id": "第18条",
                "content": "电子商务经营者根据消费者的兴趣爱好、消费习惯等特征向其推荐商品或者服务的，应当同时向该消费者提供不针对其个人特征的选项，尊重和平等保护消费者合法权益。",
                "keywords": ["推荐", "个人特征", "消费者权益"],
                "risk_types": ["个人信息泄露"]
            },
            {
                "article_id": "第19条",
                "content": "电子商务经营者搭售商品或者服务，应当以显著方式提请消费者注意，不得将搭售商品或者服务作为默认同意的选项。",
                "keywords": ["搭售", "默认同意", "显著方式"],
                "risk_types": ["不正当竞争"]
            },
            {
                "article_id": "第22条",
                "content": "电子商务经营者因其技术优势、用户数量、对相关行业的控制能力以及其他经营者对该电子商务经营者在交易上的依赖程度等因素而具有市场支配地位的，不得滥用市场支配地位。",
                "keywords": ["市场支配地位", "滥用", "垄断"],
                "risk_types": ["不正当竞争"]
            },
            {
                "article_id": "第38条",
                "content": "电子商务平台经营者知道或者应当知道平台内经营者销售的商品或者提供的服务不符合保障人身、财产安全的要求，或者有其他侵害消费者合法权益行为，未采取必要措施的，依法与该平台内经营者承担连带责任。",
                "keywords": ["连带责任", "人身安全", "财产安全"],
                "risk_types": ["产品质量问题"]
            },
            {
                "article_id": "第76条",
                "content": "电子商务经营者违反本法规定，有下列行为之一的，由市场监督管理部门责令限期改正，可以处二万元以上十万元以下的罚款；情节严重的，处十万元以上五十万元以下的罚款。",
                "keywords": ["罚款", "责令改正", "市场监督管理"],
                "risk_types": ["虚假宣传", "广告违法"]
            }
        ]
    },
    "反不正当竞争法": {
        "name": "中华人民共和国反不正当竞争法",
        "articles": [
            {
                "article_id": "第8条",
                "content": "经营者不得对其商品的性能、功能、质量、销售状况、用户评价、曾获荣誉等作虚假或者引人误解的商业宣传，欺骗、误导消费者。经营者不得通过组织虚假交易等方式，帮助其他经营者进行虚假或者引人误解的商业宣传。",
                "keywords": ["虚假宣传", "虚假交易", "用户评价"],
                "risk_types": ["虚假宣传", "不正当竞争"]
            },
            {
                "article_id": "第20条",
                "content": "经营者违反本法第八条规定，由监督检查部门责令停止违法行为，处二十万元以上一百万元以下的罚款；情节严重的，处一百万元以上二百万元以下的罚款，可以吊销营业执照。",
                "keywords": ["罚款", "吊销营业执照"],
                "risk_types": ["虚假宣传", "不正当竞争"]
            }
        ]
    },
    "商标法": {
        "name": "中华人民共和国商标法",
        "articles": [
            {
                "article_id": "第57条",
                "content": "有下列行为之一的，均属侵犯注册商标专用权：（一）未经商标注册人的许可，在同一种商品上使用与其注册商标相同的商标的；（三）销售侵犯注册商标专用权的商品的。",
                "keywords": ["侵犯", "商标", "销售"],
                "risk_types": ["知识产权侵权"]
            }
        ]
    },
    "产品质量法": {
        "name": "中华人民共和国产品质量法",
        "articles": [
            {
                "article_id": "第49条",
                "content": "生产、销售不符合保障人体健康和人身、财产安全的国家标准、行业标准的产品的，责令停止生产、销售，没收违法生产、销售的产品，并处违法生产、销售产品货值金额等值以上三倍以下的罚款。",
                "keywords": ["不符合标准", "罚款", "没收"],
                "risk_types": ["产品质量问题"]
            }
        ]
    },
    "个人信息保护法": {
        "name": "中华人民共和国个人信息保护法",
        "articles": [
            {
                "article_id": "第5条",
                "content": "处理个人信息应当遵循合法、正当、必要和诚信原则，不得通过误导、欺诈、胁迫等方式处理个人信息。",
                "keywords": ["合法", "正当", "必要", "诚信"],
                "risk_types": ["个人信息泄露"]
            },
            {
                "article_id": "第66条",
                "content": "违反本法规定处理个人信息，或者处理个人信息未履行本法规定的个人信息保护义务的，由履行个人信息保护职责的部门责令改正，给予警告，没收违法所得，对违法处理个人信息的应用程序，责令暂停或者终止提供服务。",
                "keywords": ["责令改正", "警告", "没收违法所得"],
                "risk_types": ["个人信息泄露"]
            }
        ]
    }
}


class LawDatabase:
    """法律数据库"""

    def __init__(self, data_dir: Optional[Path] = None):
        """初始化法律数据库"""
        self.data_dir = data_dir or DATA_DIR
        self.laws = {}
        self._load_builtin_laws()
        self._load_custom_laws()
        logger.info(f"LawDatabase initialized with {len(self.laws)} laws")

    def _load_builtin_laws(self):
        """加载内置法律数据"""
        self.laws.update(BUILTIN_LAWS)
        logger.info(f"Loaded {len(BUILTIN_LAWS)} builtin laws")

    def _load_custom_laws(self):
        """加载自定义法律数据"""
        if not self.data_dir.exists():
            logger.info(f"Data directory {self.data_dir} does not exist, skipping custom laws")
            return

        for law_file in self.data_dir.glob("*.json"):
            try:
                with open(law_file, "r", encoding="utf-8") as f:
                    law_data = json.load(f)
                    law_name = law_data.get("name", law_file.stem)
                    self.laws[law_name] = law_data
                    logger.info(f"Loaded custom law: {law_name}")
            except Exception as e:
                logger.error(f"Failed to load {law_file}: {e}")

    def get_law(self, law_name: str) -> Optional[Dict]:
        """获取指定法律"""
        return self.laws.get(law_name)

    def get_all_laws(self) -> Dict:
        """获取所有法律"""
        return self.laws

    def search_articles(self, query: str, limit: int = 10) -> List[Dict]:
        """搜索法律条文"""
        results = []
        query_lower = query.lower()

        for law_name, law_data in self.laws.items():
            for article in law_data.get("articles", []):
                content = article.get("content", "")
                keywords = article.get("keywords", [])

                # 检查内容匹配
                if query_lower in content.lower():
                    results.append({
                        "law_name": law_name,
                        "full_name": law_data.get("name", law_name),
                        **article,
                        "match_type": "content"
                    })

                # 检查关键词匹配
                for keyword in keywords:
                    if keyword.lower() in query_lower:
                        results.append({
                            "law_name": law_name,
                            "full_name": law_data.get("name", law_name),
                            **article,
                            "match_type": "keyword"
                        })

        # 去重并限制数量
        seen = set()
        unique_results = []
        for r in results:
            key = (r["law_name"], r["article_id"])
            if key not in seen:
                seen.add(key)
                unique_results.append(r)

        return unique_results[:limit]

    def get_articles_by_risk_type(self, risk_type: str) -> List[Dict]:
        """根据风险类型获取相关法律条文"""
        results = []

        for law_name, law_data in self.laws.items():
            for article in law_data.get("articles", []):
                if risk_type in article.get("risk_types", []):
                    results.append({
                        "law_name": law_name,
                        "full_name": law_data.get("name", law_name),
                        **article
                    })

        return results

    def get_statistics(self) -> Dict:
        """获取统计信息"""
        total_articles = 0
        risk_type_counts = {}

        for law_name, law_data in self.laws.items():
            articles = law_data.get("articles", [])
            total_articles += len(articles)

            for article in articles:
                for risk_type in article.get("risk_types", []):
                    risk_type_counts[risk_type] = risk_type_counts.get(risk_type, 0) + 1

        return {
            "total_laws": len(self.laws),
            "total_articles": total_articles,
            "risk_type_coverage": risk_type_counts
        }


# 全局实例
_law_db = None


def get_law_database() -> LawDatabase:
    """获取法律数据库实例"""
    global _law_db
    if _law_db is None:
        _law_db = LawDatabase()
    return _law_db
