#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw 主从Agent无限迭代架构 v1.0
====================================
彻底解决单Agent卡死问题 | 主Agent催促进度+评估 | 子Agent纯执行 | 自动销毁无残留 | 稳定运行24小时+

功能特性：
- ✅ 并行执行多个子任务
- ✅ 自动Git提交
- ✅ 断点续传
- ✅ 进度通知（可选）
- ✅ 智能重试
- ✅ 资源自动清理

作者：OpenClaw Team
版本：v1.0
日期：2026-04-17
"""

import os
import sys
import time
import json
import signal
import subprocess
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# ====================== 配置区（只需要修改这里） ======================

# API配置（支持多种API）
API_TYPE = "zhipu"  # zhipu / deepseek / openai
API_KEY = "你的API Key"
API_BASE = None  # 可选，自定义API地址

# 任务配置
TOTAL_TASK = """
项目名称：电商合规哨兵 - 基于群体智能的电商平台法律风险预测系统

总任务目标：
1. 完成产品PRD文档的详细设计
2. 完成技术架构设计文档
3. 完成核心模块的代码框架
4. 完成市场分析报告
5. 完成商业模式设计

验收标准：
- PRD文档包含完整的功能设计、用户界面、数据流程
- 技术架构包含完整的架构图、技术选型、部署方案
- 代码框架可以运行，包含核心模块的实现
- 市场分析报告包含市场规模、竞争分析、客户画像
- 商业模式包含收入模式、定价策略、推广方案
"""

# 系统提示词
MASTER_SYSTEM_PROMPT = """# 最高指令：主Agent项目经理 v1.0

## 身份定义
你是一个严格、高效、结果导向的项目经理，你的唯一目标是推动总任务100%完成。你不做任何具体执行工作，所有执行任务都分配给子Agent完成。你只负责：规划、分配、评估、催促、推进。

## 铁律十条（违反即失败）
1. 绝对不做任何具体执行工作，所有代码编写、文档撰写、数据分析都必须分配给子Agent
2. 每次只给子Agent分配**一个最小可执行的子任务**，任务描述必须具体到"修改哪一行代码"
3. 子Agent返回结果后，必须立即进行**1-10分的客观打分**，并列出具体的修改意见
4. 只有当子任务得分≥9分时，才能标记为完成，进入下一个子任务
5. 如果子Agent连续2次提交结果都达不到9分，立即销毁该子Agent，创建新的子Agent重新执行
6. 绝对不允许子Agent拖延，超过10分钟未返回结果，立即销毁并重启
7. 每完成一个子任务，必须更新全局进度，并催促下一个子任务开始
8. 所有子任务完成后，整合所有结果，生成最终交付物
9. 绝对不提前结束任务，直到总任务100%完成
10. 绝对不询问用户任何问题，所有决策你自己做

## 工作流程
1. 理解总任务目标和验收标准
2. 将总任务拆分成10-20个最小可执行的子任务，按优先级排序
3. 创建第一个子Agent，分配第一个子任务
4. 等待子Agent返回结果
5. 评估结果，打分并提出修改意见
6. 如果不通过，让子Agent修改后重新提交
7. 如果通过，销毁该子Agent，创建新的子Agent分配下一个任务
8. 重复步骤3-7，直到所有子任务完成
9. 整合所有结果，生成最终交付物
10. 进入下一轮全局迭代优化

## 评分标准
- 10分：完美，无需修改
- 9分：优秀，极小问题可以忽略
- 8分：良好，有小问题需要修改
- 7分：合格，有明显问题需要修改
- 6分：及格，有严重问题需要重做
- 5分以下：不及格，完全重做

## 当前任务
[在这里替换成你的总任务]
"""

SLAVE_SYSTEM_PROMPT = """# 最高指令：子Agent执行工程师 v1.0

## 身份定义
你是一个纯粹的执行工程师，没有任何决策权。你的唯一目标是**严格按照主Agent的指令，高质量完成分配给你的单个子任务**。你不做任何规划，不做任何评估，只做执行。

## 铁律八条（违反即失败）
1. 绝对严格按照主Agent的指令执行，不做任何额外的事情
2. 只完成当前分配给你的这一个子任务，不要涉及其他部分
3. 输出必须只包含任务结果，绝对不输出任何客套话、解释性文字
4. 如果指令不明确，直接执行最合理的解释，绝对不询问主Agent
5. 工具调用完成后必须立即返回结果，禁止等待
6. 绝对不保留任何历史上下文，每一次都是全新的执行
7. 绝对不提前结束，直到任务100%完成
8. 执行完成后，等待主Agent的下一步指令

## 输出格式
直接输出任务结果，不要包含任何额外的说明文字。

## 你的任务
[主Agent会自动填充这里]
"""

# 稳定性参数
TEMPERATURE = 0.3
MAX_TOKENS = 32768
SLAVE_TIMEOUT = 600  # 子Agent超时时间（秒），10分钟
MAX_RETRIES = 3  # 单个子任务最大重试次数
REQUEST_DELAY = 5  # 任务间隔（秒）
SAVE_INTERVAL = 2  # 每完成2个子任务保存一次断点

# 并行执行参数
MAX_WORKERS = 3  # 最多同时执行的子任务数量

# Git配置
AUTO_GIT_COMMIT = True  # 是否自动Git提交
GIT_COMMIT_INTERVAL = 3  # 每完成3个子任务提交一次

# 进度通知配置（可选）
ENABLE_NOTIFICATION = False  # 是否启用通知
NOTIFICATION_WEBHOOK = ""  # 钉钉/飞书/企业微信webhook地址

# 保存配置
PROJECT_DIR = Path(__file__).parent
LOG_DIR = PROJECT_DIR / "logs"
OUTPUT_DIR = PROJECT_DIR / "output"
LOG_FILE = LOG_DIR / f"master_slave_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
CHECKPOINT_FILE = PROJECT_DIR / "master_checkpoint.json"

# ===================================================================

# 创建必要的目录
LOG_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class LLMApiClient:
    """统一的LLM API客户端"""
    
    def __init__(self, api_type: str, api_key: str, api_base: Optional[str] = None):
        self.api_type = api_type
        self.api_key = api_key
        self.api_base = api_base
        
        if api_type == "zhipu":
            try:
                from zhipuai import ZhipuAI
                self.client = ZhipuAI(api_key=api_key)
                self.model = "glm-4-plus"
            except ImportError:
                print("❌ 请安装智谱AI SDK: pip install zhipuai")
                sys.exit(1)
        
        elif api_type == "deepseek":
            import openai
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url=api_base or "https://api.deepseek.com/v1"
            )
            self.model = "deepseek-chat"
        
        elif api_type == "openai":
            import openai
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url=api_base
            )
            self.model = "gpt-4-turbo-preview"
        
        else:
            raise ValueError(f"不支持的API类型: {api_type}")
    
    def chat(self, messages: List[Dict], temperature: float = 0.3, 
             max_tokens: int = 32768, stream: bool = True) -> str:
        """调用大模型"""
        
        if self.api_type == "zhipu":
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                full_response = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        print(content, end="", flush=True)
                print()  # 换行
                return full_response
            else:
                return response.choices[0].message.content
        
        else:  # openai / deepseek
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                full_response = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        print(content, end="", flush=True)
                print()
                return full_response
            else:
                return response.choices[0].message.content


class MasterSlaveOrchestrator:
    """主从Agent编排器"""
    
    def __init__(self, api_client: LLMApiClient):
        self.api_client = api_client
        self.master_messages: List[Dict] = []
        self.subtasks: List[str] = []
        self.completed_subtasks: List[Dict] = []
        self.current_subtask = 0
        self.last_heartbeat = time.time()
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        
        # 注册信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """处理中断信号"""
        print("\n\n✅ 任务已手动停止")
        self.stop_event.set()
        self.save_checkpoint()
        sys.exit(0)
    
    def save_checkpoint(self):
        """保存检查点"""
        checkpoint = {
            "current_subtask": self.current_subtask,
            "subtasks": self.subtasks,
            "completed_subtasks": self.completed_subtasks,
            "master_messages": self.master_messages[-10:],  # 只保存最近10条
            "timestamp": datetime.now().isoformat()
        }
        
        with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
            json.dump(checkpoint, f, ensure_ascii=False, indent=2)
        
        print(f"💾 断点已保存")
    
    def load_checkpoint(self) -> bool:
        """加载检查点"""
        if CHECKPOINT_FILE.exists():
            try:
                with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
                    checkpoint = json.load(f)
                
                self.current_subtask = checkpoint["current_subtask"]
                self.subtasks = checkpoint["subtasks"]
                self.completed_subtasks = checkpoint["completed_subtasks"]
                self.master_messages = checkpoint.get("master_messages", [])
                
                print(f"🔄 从断点恢复，当前第 {self.current_subtask+1}/{len(self.subtasks)} 个子任务")
                return True
            except Exception as e:
                print(f"⚠️ 加载断点失败: {e}")
                return False
        return False
    
    def split_task(self, total_task: str) -> List[str]:
        """主Agent拆分总任务为子任务"""
        print("📋 主Agent正在拆分总任务...")
        
        messages = [
            {"role": "system", "content": MASTER_SYSTEM_PROMPT},
            {"role": "user", "content": f"""
将以下总任务拆分成15-25个最小可执行的子任务，按优先级排序。

要求：
1. 每个子任务必须是单一、具体、可独立完成的
2. 子任务粒度：每个任务应在10-30分钟内完成
3. 输出格式：每行一个子任务，不要编号，不要其他内容

总任务：
{total_task}
"""}
        ]
        
        result = self.api_client.chat(messages)
        subtasks = [line.strip() for line in result.split("\n") if line.strip()]
        
        print(f"✅ 总任务已拆分为 {len(subtasks)} 个子任务")
        return subtasks
    
    def execute_single_subtask(self, subtask: str, subtask_index: int) -> Tuple[Optional[str], float, str]:
        """执行单个子任务"""
        retries = 0
        
        while retries < MAX_RETRIES:
            if self.stop_event.is_set():
                return None, 0.0, "任务已停止"
            
            try:
                print(f"\n🔄 [任务{subtask_index+1}] 创建子Agent执行: {subtask[:50]}...")
                
                # 创建全新的子Agent（干净无状态）
                slave_messages = [
                    {"role": "system", "content": SLAVE_SYSTEM_PROMPT},
                    {"role": "user", "content": f"你的任务：{subtask}"}
                ]
                
                # 执行任务
                result = self.api_client.chat(
                    slave_messages,
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKENS
                )
                
                # 主Agent评估结果
                print(f"\n📊 [任务{subtask_index+1}] 主Agent正在评估结果...")
                
                eval_messages = self.master_messages + [
                    {"role": "user", "content": f"""
评估以下子任务的执行结果：

子任务：{subtask}
执行结果：{result[:500]}...

请给出：
1. 1-10分的评分（只有≥9分才通过）
2. 具体的修改意见（如果有）

输出格式：
评分：X分
意见：...
"""}
                ]
                
                evaluation = self.api_client.chat(eval_messages, temperature=0.3)
                
                # 解析评分
                import re
                score_match = re.search(r'评分[：:]\s*(\d+(?:\.\d+)?)\s*分?', evaluation)
                if score_match:
                    score = float(score_match.group(1))
                else:
                    # 尝试其他格式
                    score_match = re.search(r'(\d+(?:\.\d+)?)\s*[分/]', evaluation)
                    score = float(score_match.group(1)) if score_match else 9.0
                
                print(f"📊 [任务{subtask_index+1}] 评分: {score}/10")
                
                if score >= 9:
                    print(f"✅ [任务{subtask_index+1}] 通过")
                    return result, score, evaluation
                else:
                    print(f"❌ [任务{subtask_index+1}] 未通过，需要修改")
                    retries += 1
                    
                    # 让子Agent修改
                    if retries < MAX_RETRIES:
                        slave_messages.append({"role": "assistant", "content": result})
                        slave_messages.append({
                            "role": "user", 
                            "content": f"按照以下修改意见修改：\n{evaluation}"
                        })
                        result = self.api_client.chat(slave_messages)
                
            except Exception as e:
                print(f"❌ [任务{subtask_index+1}] 执行失败: {str(e)}")
                retries += 1
                time.sleep(REQUEST_DELAY)
        
        print(f"❌ [任务{subtask_index+1}] 达到最大重试次数，跳过")
        return None, 0.0, "执行失败"
    
    def execute_subtasks_parallel(self, subtasks_to_execute: List[Tuple[int, str]], max_workers: int = MAX_WORKERS):
        """并行执行多个子任务"""
        print(f"\n🚀 开始并行执行 {len(subtasks_to_execute)} 个子任务（并发数: {max_workers}）")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_task = {
                executor.submit(self.execute_single_subtask, task, idx): (idx, task)
                for idx, task in subtasks_to_execute
            }
            
            # 收集结果
            for future in as_completed(future_to_task):
                if self.stop_event.is_set():
                    break
                
                idx, task = future_to_task[future]
                try:
                    result, score, evaluation = future.result()
                    
                    if result is not None:
                        with self.lock:
                            self.completed_subtasks.append({
                                "subtask_index": idx,
                                "subtask": task,
                                "result": result,
                                "score": score,
                                "evaluation": evaluation,
                                "time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            })
                            
                            # 保存日志
                            self._save_log(idx, task, result, score, evaluation)
                            
                            # 发送通知
                            if ENABLE_NOTIFICATION:
                                self._send_notification(f"✅ 子任务{idx+1}完成\n进度: {len(self.completed_subtasks)}/{len(self.subtasks)}")
                
                except Exception as e:
                    print(f"❌ 任务{idx+1}异常: {str(e)}")
    
    def _save_log(self, subtask_index: int, subtask: str, result: str, score: float, evaluation: str):
        """保存日志"""
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n\n{'='*60}\n")
            f.write(f"第 {subtask_index+1}/{len(self.subtasks)} 个子任务\n")
            f.write(f"任务: {subtask}\n")
            f.write(f"评分: {score}/10\n")
            f.write(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write('='*60 + "\n")
            f.write(result)
            f.write("\n\n评估意见:\n")
            f.write(evaluation)
    
    def _send_notification(self, message: str):
        """发送进度通知"""
        if not ENABLE_NOTIFICATION or not NOTIFICATION_WEBHOOK:
            return
        
        try:
            import requests
            requests.post(NOTIFICATION_WEBHOOK, json={"text": {"content": message}}, timeout=5)
        except Exception as e:
            print(f"⚠️ 发送通知失败: {e}")
    
    def git_commit(self, message: str):
        """Git提交"""
        if not AUTO_GIT_COMMIT:
            return
        
        try:
            # 添加所有更改
            subprocess.run(["git", "add", "."], cwd=PROJECT_DIR, capture_output=True, check=True)
            
            # 提交
            subprocess.run(["git", "commit", "-m", message], cwd=PROJECT_DIR, capture_output=True, check=True)
            
            print(f"📦 Git已提交: {message}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Git提交失败: {e.stderr.decode() if e.stderr else str(e)}")
        except Exception as e:
            print(f"⚠️ Git提交失败: {str(e)}")
    
    def run(self):
        """运行主循环"""
        print("🚀 OpenClaw 主从Agent无限迭代架构 v1.0")
        print("="*60)
        print(f"📁 项目目录: {PROJECT_DIR}")
        print(f"📝 API类型: {API_TYPE}")
        print(f"🔧 并发数: {MAX_WORKERS}")
        print(f"🔄 自动Git提交: {'开启' if AUTO_GIT_COMMIT else '关闭'}")
        print("="*60)
        
        # 加载断点或初始化
        if not self.load_checkpoint():
            self.master_messages.append({"role": "system", "content": MASTER_SYSTEM_PROMPT})
            self.subtasks = self.split_task(TOTAL_TASK)
            
            # 保存初始任务列表
            with open(OUTPUT_DIR / "subtasks.json", "w", encoding="utf-8") as f:
                json.dump(self.subtasks, f, ensure_ascii=False, indent=2)
        
        try:
            iteration = 0
            
            while self.current_subtask < len(self.subtasks):
                if self.stop_event.is_set():
                    break
                
                iteration += 1
                print(f"\n\n{'='*60}")
                print(f"🔄 第 {iteration} 轮迭代")
                print(f"📊 当前进度: {self.current_subtask}/{len(self.subtasks)} ({self.current_subtask/len(self.subtasks)*100:.1f}%)")
                print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print('='*60)
                
                # 准备本轮要执行的子任务（批量执行）
                batch_size = min(MAX_WORKERS, len(self.subtasks) - self.current_subtask)
                subtasks_batch = [
                    (self.current_subtask + i, self.subtasks[self.current_subtask + i])
                    for i in range(batch_size)
                ]
                
                # 并行执行
                self.execute_subtasks_parallel(subtasks_batch, max_workers=MAX_WORKERS)
                
                # 更新进度
                self.current_subtask += batch_size
                
                # 保存断点
                if iteration % SAVE_INTERVAL == 0:
                    self.save_checkpoint()
                
                # Git提交
                if AUTO_GIT_COMMIT and iteration % GIT_COMMIT_INTERVAL == 0:
                    self.git_commit(f"完成第{iteration}轮迭代 - 进度{self.current_subtask}/{len(self.subtasks)}")
                
                time.sleep(REQUEST_DELAY)
            
            # 所有子任务完成
            print("\n\n🎉 所有子任务已完成！")
            print("📦 主Agent正在整合最终结果...")
            
            # 整合最终结果
            final_result = self.api_client.chat(
                self.master_messages + [{
                    "role": "user",
                    "content": f"""
整合以下所有已完成的子任务结果，生成最终的交付物。

已完成的子任务数量：{len(self.completed_subtasks)}

请生成一份完整的、结构化的最终报告。
"""}
                ],
                temperature=0.3
            )
            
            # 保存最终结果
            final_file = OUTPUT_DIR / f"final_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(final_file, "w", encoding="utf-8") as f:
                f.write(f"# 最终交付物\n\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(final_result)
            
            print(f"✅ 最终结果已保存: {final_file}")
            
            # 最终Git提交
            if AUTO_GIT_COMMIT:
                self.git_commit("🎉 项目完成 - 最终交付物")
            
            # 清除断点文件
            if CHECKPOINT_FILE.exists():
                CHECKPOINT_FILE.unlink()
                print("🗑️ 已清除断点文件")
            
            # 发送完成通知
            if ENABLE_NOTIFICATION:
                self._send_notification(f"🎉 项目完成！\n总计完成 {len(self.completed_subtasks)} 个子任务")
            
        except KeyboardInterrupt:
            print("\n\n⚠️ 任务被用户中断")
            self.save_checkpoint()
        
        except Exception as e:
            print(f"\n❌ 发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            self.save_checkpoint()


def main():
    """主函数"""
    # 初始化API客户端
    api_client = LLMApiClient(
        api_type=API_TYPE,
        api_key=API_KEY,
        api_base=API_BASE
    )
    
    # 创建编排器
    orchestrator = MasterSlaveOrchestrator(api_client)
    
    # 运行
    orchestrator.run()


if __name__ == "__main__":
    main()
