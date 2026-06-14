import os

from dotenv import load_dotenv
from openai import OpenAI


# 读取 .env 文件里的通用 LLM 配置；utf-8-sig 可以兼容 Windows 写入的 BOM。
load_dotenv(encoding="utf-8-sig")


def require_env(name):
    """读取必填环境变量，缺失时给出清晰提示。"""
    value = os.getenv(name)

    if not value:
        raise RuntimeError(f"请先在 .env 里配置 {name}")

    return value


def get_llm_config():
    """只读取精简后的 OpenAI 兼容 LLM 配置。"""
    return {
        "api_key": require_env("LLM_API_KEY"),
        "base_url": require_env("LLM_BASE_URL"),
        "model": require_env("LLM_MODEL"),
    }


def get_client():
    """创建 OpenAI 兼容客户端。"""
    config = get_llm_config()
    return OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"],
    )


def chat(messages, tools=None):
    """调用 OpenAI 兼容 Chat Completions 接口。"""
    client = get_client()
    config = get_llm_config()

    kwargs = {
        "model": config["model"],
        "messages": messages,
    }

    # 有工具时传 tools，让模型自己决定是否调用工具。
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"

    return client.chat.completions.create(**kwargs)
