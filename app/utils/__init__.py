"""
工具模块
"""

from .prompt_loader import load_prompt, format_prompt, list_prompts, PromptLoader

__all__ = ["load_prompt", "format_prompt", "list_prompts", "PromptLoader"]


def calculate_total_score(
    scores: dict, weights: dict, full_scores: dict = None
) -> float:
    """
    根据各项得分、权重和原始满分计算总分。
    :param scores: 各项实际得分，如{"专业知识储备": 15, ...}
    :param weights: 各项权重，如{"专业知识储备": 0.2, ...}
    :param full_scores: 各项原始满分，如{"专业知识储备": 20, ...}，默认为20分制
    :return: 总分（0-100）
    """
    if full_scores is None:
        full_scores = {k: 20 for k in scores}
    total = 0.0
    for k in scores:
        score = scores.get(k, 0)
        weight = weights.get(k, 0)
        full = full_scores.get(k, 20)
        total += (score / full) * weight * 100
    return round(total, 2)
