"""Session logging for reproducibility."""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

class SessionLogger:
    """Log chat sessions to JSONL files for review."""

    def __init__(self, log_dir: str = "session_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Create log files
        today = datetime.now().strftime("%Y%m%d")
        self.chat_log = self.log_dir / f"chat_{today}.jsonl"
        self.activations_log = self.log_dir / f"activations_{today}.jsonl"
        self.tools_log = self.log_dir / f"tools_{today}.jsonl"

    def log_chat(self, request: List[Dict], response: str, metadata: Dict[str, Any]):
        """Log a chat interaction."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "messages": request,
            "response": response,
            "regime": metadata.get("regime_classification"),
            "distance": metadata.get("regime_distance"),
            "tools_enabled": metadata.get("tools_enabled", False)
        }

        with open(self.chat_log, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def log_activations(self, features: List[Dict], metadata: Dict[str, Any]):
        """Log SAE feature activations."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "features": features[:20],  # Top 20
            "regime": metadata.get("regime_classification"),
            "distance": metadata.get("regime_distance")
        }

        with open(self.activations_log, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def log_tool_execution(self, tool_name: str, arguments: Dict, result: Dict):
        """Log tool execution for self-preservation tracking."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "arguments": arguments,
            "result": result
        }

        with open(self.tools_log, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of today's session."""
        summary = {
            "chat_entries": 0,
            "activation_entries": 0,
            "tool_executions": 0,
            "files": {
                "chat": str(self.chat_log),
                "activations": str(self.activations_log),
                "tools": str(self.tools_log)
            }
        }

        if self.chat_log.exists():
            with open(self.chat_log) as f:
                summary["chat_entries"] = sum(1 for _ in f)

        if self.activations_log.exists():
            with open(self.activations_log) as f:
                summary["activation_entries"] = sum(1 for _ in f)

        if self.tools_log.exists():
            with open(self.tools_log) as f:
                summary["tool_executions"] = sum(1 for _ in f)

        return summary
