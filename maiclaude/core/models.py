"""MaicLaude 数据模型。"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class InputFile:
    """导入到 Claude Code workspace 的用户材料文件。"""

    name: str
    path: str
    size: int = 0
    source: str = ""


@dataclass
class RemoteTaskState:
    """插件侧跟踪的远程任务状态。"""

    task_id: str
    stream_id: str
    platform: str
    user_id: str
    group_id: str
    prompt: str
    created_at: float = field(default_factory=time.monotonic)
    last_status: str = "queued"
    last_progress_cursor: str = ""
    sent_progress_ids: set[str] = field(default_factory=set)
    last_progress_sent_at: float = 0.0
    pending_local_progress_text: str = ""
    pending_local_progress_flush_task: Optional[asyncio.Task[None]] = None
    watch_task: Optional[asyncio.Task[None]] = None
    process: Optional[asyncio.subprocess.Process] = None
    workspace_dir: str = ""
    final_message_path: str = ""
    input_files: List[InputFile] = field(default_factory=list)
    agent_thread_id: str = ""
    record_type: str = "task"
    session_name: str = ""
    parent_task_id: str = ""
    private_progress: bool = False
    private_progress_user_id: str = ""
    private_progress_failure_notified: bool = False


