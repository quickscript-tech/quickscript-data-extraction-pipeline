from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


DETERMINISTIC_UTC = datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc)


def utc_now(realtime: bool) -> datetime:
    return datetime.now(timezone.utc) if realtime else DETERMINISTIC_UTC


@dataclass
class RunLogger:
    log_path: Path
    realtime: bool = False
    lines: list[str] = field(default_factory=list)
    start_ts: datetime | None = None
    end_ts: datetime | None = None

    def start(self, input_path: Path, outdir: Path) -> None:
        self.start_ts = utc_now(self.realtime)
        self.lines.append(f"start_utc={self.start_ts.isoformat().replace('+00:00', 'Z')}")
        self.lines.append(f"input={str(input_path)}")
        self.lines.append(f"outdir={str(outdir)}")

    def info(self, msg: str) -> None:
        self.lines.append(f"info={msg}")

    def counts(self, extracted: int, valid: int, invalid: int) -> None:
        self.lines.append(f"counts extracted={extracted} valid={valid} invalid={invalid}")

    def validation_errors(self, brief_errors: Iterable[str]) -> None:
        for e in brief_errors:
            self.lines.append(f"validation_error={e}")

    def end(self) -> None:
        self.end_ts = utc_now(self.realtime)
        self.lines.append(f"end_utc={self.end_ts.isoformat().replace('+00:00', 'Z')}")

    def write(self) -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_path.write_text("\n".join(self.lines) + "\n", encoding="utf-8")