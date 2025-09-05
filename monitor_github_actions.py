#!/usr/bin/env python3
"""
GitHub Actions 监控脚本
用于检查CI/CD流程的状态
"""

import json
import time
from datetime import datetime

import requests

# GitHub API配置
GITHUB_REPO = "shinytsing/QAToolBox"
GITHUB_API_BASE = "https://api.github.com"
WORKFLOW_NAME = "QAToolBox Unified CI/CD Pipeline"


def get_latest_workflow_run():
    """获取最新的工作流运行状态"""
    url = f"{GITHUB_API_BASE}/repos/{GITHUB_REPO}/actions/runs"
    params = {"per_page": 1, "status": "all"}  # 包括所有状态

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("workflow_runs"):
            return data["workflow_runs"][0]
        return None
    except requests.RequestException as e:
        print(f"❌ 获取工作流状态失败: {e}")
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text[:200]}")
        return None


def get_workflow_jobs(run_id):
    """获取工作流的作业详情"""
    url = f"{GITHUB_API_BASE}/repos/{GITHUB_REPO}/actions/runs/{run_id}/jobs"

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get("jobs", [])
    except requests.RequestException as e:
        print(f"❌ 获取作业详情失败: {e}")
        return []


def print_status_icon(status, conclusion):
    """打印状态图标"""
    if status == "completed":
        if conclusion == "success":
            return "✅"
        elif conclusion == "failure":
            return "❌"
        elif conclusion == "cancelled":
            return "⏹️"
        else:
            return "⚠️"
    elif status == "in_progress":
        return "🔄"
    elif status == "queued":
        return "⏳"
    else:
        return "❓"


def format_duration(started_at, completed_at=None):
    """格式化持续时间"""
    if not started_at:
        return "未知"

    start_time = datetime.fromisoformat(started_at.replace("Z", "+00:00"))

    if completed_at:
        end_time = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
        duration = end_time - start_time
        return f"{duration.total_seconds():.1f}秒"
    else:
        duration = datetime.now(start_time.tzinfo) - start_time
        return f"{duration.total_seconds():.1f}秒 (进行中)"


def monitor_workflow():
    """监控工作流状态"""
    print("🔍 检查GitHub Actions状态...")

    # 获取最新工作流运行
    workflow_run = get_latest_workflow_run()
    if not workflow_run:
        print("❌ 无法获取工作流信息")
        return False

    # 基本信息
    run_id = workflow_run["id"]
    status = workflow_run["status"]
    conclusion = workflow_run.get("conclusion")
    created_at = workflow_run["created_at"]
    started_at = workflow_run.get("started_at")
    completed_at = workflow_run.get("completed_at")

    print(f"\n📊 工作流信息:")
    print(f"  ID: {run_id}")
    print(f"  状态: {print_status_icon(status, conclusion)} {status}")
    if conclusion:
        print(f"  结果: {conclusion}")
    print(f"  创建时间: {created_at}")
    print(f"  持续时间: {format_duration(started_at, completed_at)}")
    print(f"  提交: {workflow_run['head_sha'][:8]}")
    print(f"  分支: {workflow_run['head_branch']}")

    # 获取作业详情
    jobs = get_workflow_jobs(run_id)
    if jobs:
        print(f"\n📋 作业详情:")
        for job in jobs:
            job_status = job["status"]
            job_conclusion = job.get("conclusion")
            job_name = job["name"]
            job_started = job.get("started_at")
            job_completed = job.get("completed_at")

            print(f"  {print_status_icon(job_status, job_conclusion)} {job_name}")
            print(f"    状态: {job_status}")
            if job_conclusion:
                print(f"    结果: {job_conclusion}")
            print(f"    持续时间: {format_duration(job_started, job_completed)}")

            # 如果有步骤信息
            if job.get("steps"):
                print(f"    步骤:")
                for step in job["steps"]:
                    step_status = step["status"]
                    step_conclusion = step.get("conclusion")
                    step_name = step["name"]
                    print(f"      {print_status_icon(step_status, step_conclusion)} {step_name}")

    # 判断整体状态
    if status == "completed":
        if conclusion == "success":
            print(f"\n🎉 工作流执行成功!")
            return True
        else:
            print(f"\n❌ 工作流执行失败!")
            return False
    elif status == "in_progress":
        print(f"\n🔄 工作流正在执行中...")
        return None
    else:
        print(f"\n⚠️ 工作流状态异常: {status}")
        return False


def main():
    """主函数"""
    print("🚀 GitHub Actions 监控器")
    print("=" * 50)

    # 检查一次
    result = monitor_workflow()

    if result is None:
        print("\n⏳ 工作流正在执行，等待完成...")
        print("按 Ctrl+C 停止监控")

        try:
            while True:
                time.sleep(30)  # 每30秒检查一次
                result = monitor_workflow()
                if result is not None:
                    break
        except KeyboardInterrupt:
            print("\n\n⏹️ 监控已停止")

    # 输出结果
    if result is True:
        print("\n✅ 所有检查通过! 代码质量达标")
    elif result is False:
        print("\n❌ 检查失败，需要修复问题")
    else:
        print("\n⚠️ 状态未知")


if __name__ == "__main__":
    main()
