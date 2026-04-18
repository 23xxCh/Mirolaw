"""
法规爬虫模块

从公开法律数据源获取最新法律条文。
数据来源：
- 国家法律法规数据库 (flk.npc.gov.cn)
- LawRefBook/Laws (https://github.com/LawRefBook/Laws)
"""

import os
import json
import logging
import re
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

# 数据目录
DATA_DIR = Path(__file__).parent.parent / "data" / "laws"


class LawCrawler:
    """法规爬虫"""

    def __init__(self, data_dir: Optional[Path] = None):
        self.data_dir = data_dir or DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def crawl_from_github(self, repo_url: str = "https://api.github.com/repos/LawRefBook/Laws/contents") -> List[Dict]:
        """从GitHub仓库获取法律数据"""
        laws = []

        try:
            import requests

            # 获取仓库文件列表
            response = requests.get(repo_url, timeout=10)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch from GitHub: {response.status_code}")
                return []

            files = response.json()

            for file_info in files[:20]:  # 限制数量
                if file_info.get("type") == "file" and file_info.get("name", "").endswith(".md"):
                    try:
                        content_url = file_info.get("download_url")
                        if content_url:
                            content_response = requests.get(content_url, timeout=10)
                            if content_response.status_code == 200:
                                law_data = self._parse_markdown_law(
                                    content_response.text,
                                    file_info.get("name")
                                )
                                if law_data:
                                    laws.append(law_data)
                    except Exception as e:
                        logger.error(f"Failed to parse {file_info.get('name')}: {e}")

            logger.info(f"Crawled {len(laws)} laws from GitHub")

        except ImportError:
            logger.warning("requests not installed, skipping GitHub crawl")
        except Exception as e:
            logger.error(f"GitHub crawl failed: {e}")

        return laws

    def _parse_markdown_law(self, content: str, filename: str) -> Optional[Dict]:
        """解析Markdown格式的法律文件"""
        lines = content.split("\n")

        # 提取标题
        title = ""
        for line in lines[:10]:
            if line.startswith("# "):
                title = line[2:].strip()
                break

        if not title:
            title = filename.replace(".md", "")

        # 提取条文
        articles = []
        current_article = None

        for line in lines:
            # 匹配条文标题 (如：第X条)
            match = re.match(r"^#+\s*第([零一二三四五六七八九十百]+)条", line)
            if match:
                if current_article:
                    articles.append(current_article)
                current_article = {
                    "article_id": f"第{match.group(1)}条",
                    "content": ""
                }
            elif current_article:
                current_article["content"] += line.strip() + " "

        if current_article:
            articles.append(current_article)

        return {
            "name": title,
            "source": "github",
            "filename": filename,
            "articles": articles,
            "crawled_at": datetime.now().isoformat()
        }

    def save_laws(self, laws: List[Dict]) -> int:
        """保存法律数据"""
        saved_count = 0

        for law in laws:
            name = law.get("name", "unknown")
            # 清理文件名
            safe_name = re.sub(r'[^\w\u4e00-\u9fff]', '_', name)
            filepath = self.data_dir / f"{safe_name}.json"

            try:
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(law, f, ensure_ascii=False, indent=2)
                saved_count += 1
                logger.info(f"Saved: {filepath}")
            except Exception as e:
                logger.error(f"Failed to save {name}: {e}")

        return saved_count

    def get_cached_laws(self) -> List[Dict]:
        """获取缓存的法律数据"""
        laws = []

        for filepath in self.data_dir.glob("*.json"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    laws.append(json.load(f))
            except Exception as e:
                logger.error(f"Failed to load {filepath}: {e}")

        return laws

    def update_laws(self) -> Dict:
        """更新法律数据"""
        # 从GitHub获取
        github_laws = self.crawl_from_github()

        # 保存
        saved = self.save_laws(github_laws)

        return {
            "crawled": len(github_laws),
            "saved": saved,
            "updated_at": datetime.now().isoformat()
        }


class LawUpdateScheduler:
    """法律更新调度器"""

    def __init__(self, crawler: Optional[LawCrawler] = None):
        self.crawler = crawler or LawCrawler()
        self.last_update = None

    def check_update_needed(self) -> bool:
        """检查是否需要更新"""
        if self.last_update is None:
            return True

        # 每周更新一次
        days_since_update = (datetime.now() - self.last_update).days
        return days_since_update >= 7

    def run_update(self) -> Dict:
        """执行更新"""
        if not self.check_update_needed():
            return {"status": "skipped", "reason": "Not due for update"}

        result = self.crawler.update_laws()
        self.last_update = datetime.now()

        return {
            "status": "completed",
            "result": result
        }


# 全局实例
_law_crawler = None


def get_law_crawler() -> LawCrawler:
    """获取法规爬虫实例"""
    global _law_crawler
    if _law_crawler is None:
        _law_crawler = LawCrawler()
    return _law_crawler
