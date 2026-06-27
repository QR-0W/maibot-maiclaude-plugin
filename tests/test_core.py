"""MaicLaude 核心模块测试。"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestConstants:
    """常量模块测试。"""

    def test_plugin_id(self):
        from maiclaude.core.constants import PLUGIN_ID
        assert PLUGIN_ID == "qr0w.maiclaude"
        assert "." in PLUGIN_ID

    def test_status_sets(self):
        from maiclaude.core.constants import ACTIVE_STATUSES, TERMINAL_STATUSES
        assert "succeeded" in TERMINAL_STATUSES
        assert "failed" in TERMINAL_STATUSES
        assert "cancelled" in TERMINAL_STATUSES
        assert "queued" in ACTIVE_STATUSES
        assert "running" in ACTIVE_STATUSES

    def test_env_allowlist(self):
        from maiclaude.core.constants import DEFAULT_CLAUDE_ENV_ALLOWLIST
        assert "PATH" in DEFAULT_CLAUDE_ENV_ALLOWLIST
        assert "HOME" in DEFAULT_CLAUDE_ENV_ALLOWLIST
        assert "CLAUDE_HOME" in DEFAULT_CLAUDE_ENV_ALLOWLIST

    def test_command_prefixes(self):
        from maiclaude.core.constants import SUPPORTED_COMMAND_PREFIXES
        assert "/claude" in SUPPORTED_COMMAND_PREFIXES

    def test_status_aliases(self):
        from maiclaude.core.constants import STATUS_ALIASES
        assert STATUS_ALIASES["complete"] == "succeeded"
        assert STATUS_ALIASES["error"] == "failed"
        assert STATUS_ALIASES["canceled"] == "cancelled"


class TestModels:
    """数据模型测试。"""

    def test_input_file_creation(self):
        from maiclaude.core.models import InputFile
        f = InputFile(name="test.txt", path="/tmp/test.txt", size=100, source="qq")
        assert f.name == "test.txt"
        assert f.size == 100

    def test_remote_task_state_defaults(self):
        from maiclaude.core.models import RemoteTaskState
        s = RemoteTaskState(
            task_id="t1", stream_id="s1", platform="qq",
            user_id="u1", group_id="", prompt="hi"
        )
        assert s.task_id == "t1"
        assert s.last_status == "queued"
        assert s.record_type == "task"
        assert s.private_progress is False


class TestUtils:
    """工具函数测试。"""

    def test_truncate_text(self):
        from maiclaude.core.utils import _truncate_text
        assert _truncate_text("hello", 10) == "hello"
        result = _truncate_text("hello world, this is a long text", 10)
        assert len(result) <= 13  # text + "..."
        assert result.endswith("...")

    def test_plain_qq_text(self):
        from maiclaude.core.utils import _plain_qq_text
        assert "**" not in _plain_qq_text("**bold**")
        assert "`" not in _plain_qq_text("`code`")

    def test_contains_cjk(self):
        from maiclaude.core.utils import _contains_cjk
        assert _contains_cjk("你好世界")
        assert not _contains_cjk("hello world")
        assert _contains_cjk("混合mixed")

    def test_normalize_set(self):
        from maiclaude.core.utils import _normalize_set
        result = _normalize_set(["  QQ:123  ", "", "qq:456"])
        assert "qq:123" in result
        assert "qq:456" in result
        assert "" not in result

    def test_display_task_kind(self):
        from maiclaude.core.utils import _display_task_kind
        local = _display_task_kind("local_20260626_test")
        remote = _display_task_kind("remote_20260626_test")
        assert "本机" in local
        assert "远程" in remote

    def test_coerce_progress_items(self):
        from maiclaude.core.utils import _coerce_progress_items
        assert _coerce_progress_items(["a", "b"]) == ["a", "b"]
        assert _coerce_progress_items("single") == ["single"]
        assert _coerce_progress_items(None) == []

    def test_coerce_artifacts(self):
        from maiclaude.core.utils import _coerce_artifacts
        assert _coerce_artifacts(None) == []
        assert _coerce_artifacts([{"name": "f.txt"}]) == [{"name": "f.txt"}]
