"""Session state management for multi-round SRS review workflow.

Persists review progress so the skill can resume across invocations: which
requirements have been reviewed, what decisions were made, what fixes were
applied, and what's still pending.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Per-round change record
# ---------------------------------------------------------------------------

@dataclass
class RoundRecord:
    round_number: int
    timestamp: str = ""
    action: str = ""                # "generate" | "fix" | "approve"
    input_summary: str = ""         # what input changed
    requirement_changes: list[str] = field(default_factory=list)
    decisions: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

@dataclass
class SessionState:
    module: str
    session_id: str = ""
    created_at: str = ""
    updated_at: str = ""

    # Current phase
    current_phase: str = "init"     # init | generate | review | fix | done

    # Requirement-level review status
    reviewed_ids: set[str] = field(default_factory=set)
    approved_ids: set[str] = field(default_factory=set)
    needs_fix_ids: set[str] = field(default_factory=set)

    # Round history
    rounds: list[RoundRecord] = field(default_factory=list)
    total_rounds: int = 0

    # Open items remaining
    open_item_count: int = 0
    blocking_count: int = 0

    # Gate verdict per round
    gate_verdicts: dict[int, str] = field(default_factory=dict)  # round -> verdict

    # Output artifacts
    output_dir: str = ""
    srs_file: str = ""
    review_record_file: str = ""


# ---------------------------------------------------------------------------
# Session store
# ---------------------------------------------------------------------------

_SESSIONS_ROOT = Path(".fc-sessions")


class SessionStore:
    """Persist and load review session state.

    Session file: .fc-sessions/{module}/session.json
    """

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or _SESSIONS_ROOT

    def _session_path(self, module: str) -> Path:
        return self.root / module / "session.json"

    def load(self, module: str) -> SessionState | None:
        path = self._session_path(module)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return SessionState(
                module=data.get("module", module),
                session_id=data.get("session_id", ""),
                created_at=data.get("created_at", ""),
                updated_at=data.get("updated_at", ""),
                current_phase=data.get("current_phase", "init"),
                reviewed_ids=set(data.get("reviewed_ids", [])),
                approved_ids=set(data.get("approved_ids", [])),
                needs_fix_ids=set(data.get("needs_fix_ids", [])),
                rounds=[RoundRecord(**r) for r in data.get("rounds", [])],
                total_rounds=data.get("total_rounds", 0),
                open_item_count=data.get("open_item_count", 0),
                blocking_count=data.get("blocking_count", 0),
                gate_verdicts={int(k): v for k, v in data.get("gate_verdicts", {}).items()},
                output_dir=data.get("output_dir", ""),
                srs_file=data.get("srs_file", ""),
                review_record_file=data.get("review_record_file", ""),
            )
        except (json.JSONDecodeError, KeyError, TypeError):
            return None

    def save(self, state: SessionState) -> None:
        path = self._session_path(state.module)
        path.parent.mkdir(parents=True, exist_ok=True)
        state.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {
            "module": state.module,
            "session_id": state.session_id,
            "created_at": state.created_at,
            "updated_at": state.updated_at,
            "current_phase": state.current_phase,
            "reviewed_ids": sorted(state.reviewed_ids),
            "approved_ids": sorted(state.approved_ids),
            "needs_fix_ids": sorted(state.needs_fix_ids),
            "rounds": [
                {
                    "round_number": r.round_number,
                    "timestamp": r.timestamp,
                    "action": r.action,
                    "input_summary": r.input_summary,
                    "requirement_changes": r.requirement_changes,
                    "decisions": r.decisions,
                }
                for r in state.rounds
            ],
            "total_rounds": state.total_rounds,
            "open_item_count": state.open_item_count,
            "blocking_count": state.blocking_count,
            "gate_verdicts": {str(k): v for k, v in state.gate_verdicts.items()},
            "output_dir": state.output_dir,
            "srs_file": state.srs_file,
            "review_record_file": state.review_record_file,
        }
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def create(self, module: str, output_dir: str = "") -> SessionState:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        session_id = f"{module}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        state = SessionState(
            module=module,
            session_id=session_id,
            created_at=now,
            updated_at=now,
            current_phase="init",
            output_dir=output_dir,
        )
        self.save(state)
        return state

    def add_round(
        self,
        state: SessionState,
        action: str,
        input_summary: str = "",
        requirement_changes: list[str] | None = None,
        decisions: list[str] | None = None,
    ) -> SessionState:
        state.total_rounds += 1
        round_rec = RoundRecord(
            round_number=state.total_rounds,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            action=action,
            input_summary=input_summary,
            requirement_changes=requirement_changes or [],
            decisions=decisions or [],
        )
        state.rounds.append(round_rec)
        return state

    def transition(self, state: SessionState, phase: str) -> SessionState:
        state.current_phase = phase
        return state


# ---------------------------------------------------------------------------
# Final review record builder — aggregates all rounds into one review record
# ---------------------------------------------------------------------------

def render_final_review_record(state: SessionState) -> str:
    """Generate the final review record Markdown with full round history."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        f"# SRS 评审记录 — {state.module}",
        "",
        f"**会话ID**: {state.session_id}",
        f"**创建时间**: {state.created_at}",
        f"**完成时间**: {now}",
        f"**总轮次**: {state.total_rounds}",
        "",
        "---",
        "",
        "## 评审结论",
        "",
    ]

    final_verdict = state.gate_verdicts.get(state.total_rounds, "待确认")
    lines.append(f"**最终结论**: {final_verdict}")
    lines.append("")

    # ---- Round history ----
    lines.append("## 评审轮次历史")
    lines.append("")
    lines.append("| 轮次 | 时间 | 动作 | 输入变更 | 需求变更数 | 决策 |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for r in state.rounds:
        lines.append(
            f"| Round {r.round_number} | {r.timestamp} | {r.action} | "
            f"{r.input_summary[:60]} | {len(r.requirement_changes)} | "
            f"{'; '.join(r.decisions[:3])} |"
        )
    lines.append("")

    # ---- Change details per round ----
    for r in state.rounds:
        if r.requirement_changes:
            lines.append(f"### Round {r.round_number} 变更明细")
            lines.append("")
            for ch in r.requirement_changes:
                lines.append(f"- {ch}")
            lines.append("")

    # ---- Final status ----
    lines.append("## 需求最终状态")
    lines.append("")
    lines.append(f"| 指标 | 数值 |")
    lines.append(f"| --- | --- |")
    lines.append(f"| 已评审 | {len(state.reviewed_ids)} |")
    lines.append(f"| 已批准 | {len(state.approved_ids)} |")
    lines.append(f"| 待修正 | {len(state.needs_fix_ids)} |")
    lines.append(f"| 遗留开放项 | {state.open_item_count} |")
    lines.append(f"| 阻断项 | {state.blocking_count} |")
    lines.append("")

    # ---- Approval block ----
    lines.extend([
        "---",
        "",
        "## 审批签署",
        "",
        f"**评审人**: _________  ",
        f"**日期**: _________  ",
        "",
        f"**批准人**: _________  ",
        f"**日期**: _________  ",
        "",
    ])

    return "\n".join(lines)
