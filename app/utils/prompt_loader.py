"""
Prompt加载工具
提供简单的prompt文件读取功能，支持Jinja2模板
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger
from jinja2 import Template, Environment, BaseLoader


class PromptLoader:
    """Prompt文件加载器"""

    def __init__(self, prompt_dir: str = "app/prompt"):
        """
        初始化PromptLoader

        Args:
            prompt_dir: prompt文件目录路径
        """
        self.prompt_dir = Path(prompt_dir)
        if not self.prompt_dir.exists():
            logger.warning(f"Prompt目录不存在: {self.prompt_dir}")
            self.prompt_dir.mkdir(parents=True, exist_ok=True)

    def load_prompt(self, filename: str) -> Optional[str]:
        """
        加载指定文件名的prompt内容

        Args:
            filename: prompt文件名（不包含扩展名）

        Returns:
            prompt内容字符串，如果文件不存在则返回None
        """
        # 尝试不同的文件扩展名
        possible_extensions = ["", ".txt", ".md", ".prompt"]

        for ext in possible_extensions:
            file_path = self.prompt_dir / f"{filename}{ext}"
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    logger.info(f"成功加载prompt文件: {file_path}")
                    return content
                except Exception as e:
                    logger.error(f"读取prompt文件失败 {file_path}: {e}")
                    return None

        logger.error(f"未找到prompt文件: {filename}")
        return None

    def list_prompts(self) -> list[str]:
        """
        列出所有可用的prompt文件名

        Returns:
            prompt文件名列表
        """
        if not self.prompt_dir.exists():
            return []

        prompts = []
        for file_path in self.prompt_dir.iterdir():
            if file_path.is_file():
                # 移除可能的扩展名
                name = file_path.stem
                prompts.append(name)

        return sorted(prompts)

    def format_prompt(self, filename: str, **kwargs) -> Optional[str]:
        """
        加载并格式化prompt内容（使用Jinja2模板）

        Args:
            filename: prompt文件名
            **kwargs: 用于格式化的参数

        Returns:
            格式化后的prompt内容
        """
        content = self.load_prompt(filename)
        if content is None:
            return None

        try:
            # 使用Jinja2模板引擎
            template = Template(content)
            return template.render(**kwargs)
        except Exception as e:
            logger.error(f"Jinja2模板格式化失败: {e}")
            return content


# 创建全局实例
prompt_loader = PromptLoader()


def load_prompt(filename: str) -> Optional[str]:
    """
    便捷函数：加载prompt文件

    Args:
        filename: prompt文件名

    Returns:
        prompt内容
    """
    return prompt_loader.load_prompt(filename)


def format_prompt(filename: str, **kwargs) -> Optional[str]:
    """
    便捷函数：加载并格式化prompt

    Args:
        filename: prompt文件名
        **kwargs: 格式化参数

    Returns:
        格式化后的prompt内容
    """
    return prompt_loader.format_prompt(filename, **kwargs)


def list_prompts() -> list[str]:
    """
    便捷函数：列出所有prompt文件

    Returns:
        prompt文件名列表
    """
    return prompt_loader.list_prompts()
