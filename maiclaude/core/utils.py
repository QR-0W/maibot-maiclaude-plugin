"""MaicLaude 工具函数。"""

import re
from datetime import datetime
from typing import Any, Dict, List


def _normalize_set(values: List[str]) -> set[str]:
    """规范化字符串列表为集合。"""

    return {str(value or "").strip().lower() for value in values if str(value or "").strip()}


def _truncate_text(text: str, max_chars: int) -> str:
    """按字符数截断文本。"""

    normalized_text = str(text or "").strip()
    if max_chars <= 0 or len(normalized_text) <= max_chars:
        return normalized_text
    return f"{normalized_text[: max_chars - 1]}…"


def _plain_qq_text(text: str) -> str:
    """清理 Markdown 风格标记，保留适合 QQ 展示的纯文本。"""

    cleaned = str(text or "").replace("\r", "\n").strip()
    replacements = {
        "```": "",
        "`": "",
        "**": "",
        "__": "",
        "### ": "",
        "## ": "",
        "# ": "",
        "> ": "",
    }
    for source, target in replacements.items():
        cleaned = cleaned.replace(source, target)
    lines = [" ".join(line.split()) for line in cleaned.splitlines()]
    return "\n".join(line for line in lines if line).strip()


def _sanitize_path_text(text: str, replacements: Dict[str, str]) -> str:
    """把面向用户的文本中的本机绝对路径替换为相对描述。"""

    cleaned = str(text or "")
    ordered_items = sorted(
        ((str(source or ""), str(target or "")) for source, target in replacements.items() if str(source or "")),
        key=lambda item: len(item[0]),
        reverse=True,
    )
    for source, target in ordered_items:
        cleaned = cleaned.replace(source, target)
    return re.sub(r"/[^\s，。；：、]+/workspace/artifacts/([^\s，。；：、]+)", r"workspace/artifacts/\1", cleaned)


def _format_progress_message(task_id: str, progress_lines: List[str], max_chars: int) -> str:
    """格式化 QQ 进度消息。"""

    display_lines = []
    for line in progress_lines:
        cleaned = _plain_qq_text(line)
        if cleaned:
            display_lines.append(_truncate_text(cleaned, max_chars))

    if not display_lines:
        display_lines = ["正在处理任务。"]

    now_text = datetime.now().strftime("%H:%M:%S")
    body = "\n\n".join(f"{index}. {line}" for index, line in enumerate(display_lines, start=1))
    return (
        "任务进度\n"
        f"时间：{now_text}\n"
        f"任务ID：{task_id}\n"
        "\n"
        f"{body}"
    )


def _looks_like_final_progress(text: str) -> bool:
    """判断 Claude Code 流式输出是否已经是最终总结。"""

    cleaned = _plain_qq_text(text)
    if not cleaned:
        return False
    markers = ("产物路径", "产物：", "产物:", "artifact", "artifacts/")
    if not any(marker.lower() in cleaned.lower() for marker in markers):
        return False
    final_markers = ("已完成", "已生成", "已读取", "已整理", "生成结果", "完成")
    return any(marker in cleaned for marker in final_markers)


def _contains_cjk(text: str) -> bool:
    """判断文本是否包含中文或其他 CJK 字符。"""

    return bool(re.search(r"[\u3400-\u9fff]", str(text or "")))


def _display_task_kind(task_id: str) -> str:
    """返回用户可见的任务类型。"""

    if str(task_id or "").startswith("local_"):
        return "本机 Claude Code 任务"
    return "远程 Claude Code 任务"


def _coerce_progress_items(raw_progress: Any) -> List[Dict[str, str]]:
    """将远程服务返回的进度字段归一化为列表。"""

    if raw_progress is None:
        return []
    if isinstance(raw_progress, str):
        raw_items: List[Any] = [raw_progress]
    elif isinstance(raw_progress, list):
        raw_items = raw_progress
    else:
        return []

    progress_items: List[Dict[str, str]] = []
    for index, item in enumerate(raw_items):
        if isinstance(item, str):
            text = item.strip()
            item_id = text
        elif isinstance(item, dict):
            text = str(item.get("text") or item.get("message") or item.get("content") or "").strip()
            item_id = str(item.get("id") or item.get("seq") or item.get("sequence") or item.get("cursor") or "").strip()
            if not item_id:
                item_id = f"{index}:{text}"
        else:
            continue
        if text:
            progress_items.append({"id": item_id, "text": text})
    return progress_items


def _coerce_artifacts(raw_artifacts: Any) -> List[Dict[str, Any]]:
    """将远程服务返回的产物字段归一化为列表。"""

    if isinstance(raw_artifacts, dict):
        return [dict(raw_artifacts)]
    if not isinstance(raw_artifacts, list):
        return []
    return [dict(item) for item in raw_artifacts if isinstance(item, dict)]


