import hashlib
import json

from core.result import now_text
from core.runtime import LOG_DIR


MAX_FIELD_CHARS = 800


def shorten(value, max_chars=MAX_FIELD_CHARS):
    """审计日志只保存摘要，避免大文件内容把日志撑爆。"""
    text = json.dumps(value, ensure_ascii=False, default=str)

    if len(text) <= max_chars:
        return value

    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return {
        "truncated": True,
        "sha256": digest,
        "preview": text[:max_chars],
        "original_chars": len(text),
    }


def audit_event(event_type, **fields):
    """追加一条审计日志，使用 jsonl 方便后续按行检索。"""
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        log_file = LOG_DIR / "audit.jsonl"
        item = {
            "time": now_text(),
            "event_type": event_type,
            **fields,
        }

        with log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(shorten(item, 4000), ensure_ascii=False, default=str) + "\n")
    except OSError:
        # 审计失败不能打断业务工具；部署时应修复日志目录权限。
        return
