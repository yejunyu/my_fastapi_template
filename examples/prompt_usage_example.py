"""
Prompt加载工具使用示例
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils import load_prompt, format_prompt, list_prompts


def example_basic_usage():
    """基本使用示例"""
    print("=== 基本使用示例 ===")

    # 1. 列出所有可用的prompt文件
    available_prompts = list_prompts()
    print(f"可用的prompt文件: {available_prompts}")

    # 2. 加载interview prompt
    interview_prompt = load_prompt("interview")
    if interview_prompt:
        print(f"\nInterview prompt 前100字符: {interview_prompt[:100]}...")

    # 3. 加载ranking prompt
    ranking_prompt = load_prompt("ranking")
    if ranking_prompt:
        print(f"\nRanking prompt 前100字符: {ranking_prompt[:100]}...")


def example_format_usage():
    """格式化使用示例"""
    print("\n=== 格式化使用示例 ===")

    # 使用format_prompt进行参数替换
    formatted_prompt = format_prompt(
        "interview",
        job_intention="Python后端开发工程师",
        resume_experience="3年Python开发经验，熟悉FastAPI、Django等框架",
    )

    if formatted_prompt:
        print("格式化后的interview prompt:")
        print(formatted_prompt)


def example_error_handling():
    """错误处理示例"""
    print("\n=== 错误处理示例 ===")

    # 尝试加载不存在的文件
    non_existent = load_prompt("non_existent_file")
    if non_existent is None:
        print("✓ 正确处理了不存在的文件")

    # 尝试格式化缺少参数的文件
    try:
        formatted = format_prompt("interview")  # 缺少必要参数
        print("✓ 正确处理了缺少参数的情况")
    except Exception as e:
        print(f"格式化错误: {e}")


if __name__ == "__main__":
    example_basic_usage()
    example_format_usage()
    example_error_handling()
