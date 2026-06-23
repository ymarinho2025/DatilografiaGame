# -*- coding: utf-8 -*-
"""
Estado, pontuação, fases, linhas, checkpoints e estatísticas.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import random
from pathlib import Path
import time

from frases import PHASES, BONUS_PHASE
from settings import (
    BLOCK_BASE_SECONDS,
    BLOCK_SECONDS_PER_CHAR,
    LINES_PER_BLOCK,
    MIN_BLOCK_SECONDS,
)
from utils import split_text_into_lines


@dataclass
class TypingStats:
    total_keys: int = 0
    correct_keys: int = 0
    completed_chars: int = 0
    completed_lines: int = 0
    completed_paragraphs: int = 0
    last_line_wpm: float = 0.0
    last_line_cpm: float = 0.0

    def accuracy(self) -> float:
        if self.total_keys == 0:
            return 100.0
        return (self.correct_keys / self.total_keys) * 100


@dataclass
class GameState:
    record_file: Path = field(default_factory=lambda: Path(__file__).with_name("recorde.json"))
    phases: list[dict] = field(default_factory=list)
    stage_index: int = 0

    lines: list[str] = field(default_factory=list)
    line_index: int = 0
    typed_line: str = ""

    score: int = 0
    combo: int = 0
    best_combo: int = 0
    multiplier: int = 1
    in_bonus: bool = False
    locked: bool = False

    game_started_at: float = 0.0
    line_started_at: float = 0.0
    block_started_at: float = 0.0
    block_time_limit: float = 0.0
    block_remaining: float = 0.0
    timer_paused: bool = False

    stats: TypingStats = field(default_factory=TypingStats)
    record: dict = field(default_factory=lambda: {"score": 0, "wpm": 0.0, "cpm": 0.0})

    def load_record(self) -> None:
        if not self.record_file.exists():
            return
        try:
            data = json.loads(self.record_file.read_text(encoding="utf-8"))
            self.record = {
                "score": int(data.get("score", 0)),
                "wpm": float(data.get("wpm", 0.0)),
                "cpm": float(data.get("cpm", 0.0)),
            }
        except Exception:
            self.record = {"score": 0, "wpm": 0.0, "cpm": 0.0}

    def save_record(self) -> None:
        wpm, cpm = self.average_speed()
        changed = False

        if self.score > self.record["score"]:
            self.record["score"] = self.score
            changed = True

        if wpm > self.record["wpm"]:
            self.record["wpm"] = round(wpm, 1)
            changed = True

        if cpm > self.record["cpm"]:
            self.record["cpm"] = round(cpm, 1)
            changed = True

        if changed:
            try:
                self.record_file.write_text(
                    json.dumps(self.record, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
            except OSError:
                pass

    def reset(self, seed: int | None = None) -> None:
        self.phases = [
            {
                "title": phase["title"],
                "source": phase["source"],
                "text": phase["text"],
                "lines": split_text_into_lines(phase["text"]),
            }
            for phase in PHASES
        ]
        rng = random.Random(seed)
        rng.shuffle(self.phases)

        self.stage_index = 0
        self.lines = []
        self.line_index = 0
        self.typed_line = ""

        self.score = 0
        self.combo = 0
        self.best_combo = 0
        self.multiplier = 1
        self.in_bonus = False
        self.locked = False

        self.game_started_at = time.time()
        self.line_started_at = time.time()
        self.block_started_at = time.time()
        self.block_time_limit = 0.0
        self.block_remaining = 0.0
        self.timer_paused = False

        self.stats = TypingStats()

    def current_phase(self) -> dict:
        if not self.phases:
            return {"title": "—", "source": "—", "text": "", "lines": []}
        index = min(self.stage_index, len(self.phases) - 1)
        return self.phases[index]

    def load_current_stage(self) -> None:
        phase = self.current_phase()
        self.lines = phase["lines"]
        self.line_index = 0
        self.typed_line = ""
        self.locked = False
        self.line_started_at = time.time()
        self.start_new_block_timer()

    def start_new_block_timer(self) -> None:
        block_lines = self.current_block_lines()
        char_count = sum(len(line) for line in block_lines)
        self.block_time_limit = max(
            MIN_BLOCK_SECONDS,
            BLOCK_BASE_SECONDS + char_count * BLOCK_SECONDS_PER_CHAR,
        )
        self.block_remaining = self.block_time_limit
        self.block_started_at = time.time()
        self.timer_paused = False
        self.line_started_at = time.time()

    def current_block_start(self) -> int:
        return (self.line_index // LINES_PER_BLOCK) * LINES_PER_BLOCK

    def current_block_end(self) -> int:
        return min(self.current_block_start() + LINES_PER_BLOCK, len(self.lines))

    def current_block_lines(self) -> list[str]:
        return self.lines[self.current_block_start(): self.current_block_end()]

    def current_line(self) -> str:
        if not self.lines or self.line_index >= len(self.lines):
            return ""
        return self.lines[self.line_index]

    def expected_char(self) -> str | None:
        line = self.current_line()
        if len(self.typed_line) >= len(line):
            return None
        return line[len(self.typed_line)]

    def register_key(self, correct: bool) -> None:
        self.stats.total_keys += 1
        if correct:
            self.stats.correct_keys += 1

    def add_typed_char(self, ch: str) -> None:
        self.typed_line += ch

    def line_finished(self) -> bool:
        return self.typed_line == self.current_line() and bool(self.current_line())

    def complete_line(self) -> int:
        elapsed = max(time.time() - self.line_started_at, 0.1)
        line = self.current_line()

        self.stats.last_line_wpm = (len(line) / 5) / (elapsed / 60)
        self.stats.last_line_cpm = len(line) / (elapsed / 60)
        self.stats.completed_lines += 1
        self.stats.completed_chars += len(line)

        self.combo += 1
        self.best_combo = max(self.best_combo, self.combo)

        base = 90
        size_bonus = len(line) * 3
        speed_bonus = int(max(0, 12 - elapsed) * 14)
        combo_bonus = self.combo * 25
        gained = (base + size_bonus + speed_bonus + combo_bonus) * self.multiplier
        self.score += gained

        # Checkpoint: ao completar a linha, a próxima tentativa começa na linha seguinte.
        self.line_index += 1
        self.typed_line = ""
        self.line_started_at = time.time()

        return gained

    def restart_current_line_from_checkpoint(self) -> None:
        self.typed_line = ""
        self.locked = False
        self.line_started_at = time.time()

    def reset_combo(self) -> None:
        self.combo = 0

    def phase_completed(self) -> bool:
        return self.line_index >= len(self.lines) and bool(self.lines)

    def advance_stage(self) -> None:
        self.stats.completed_paragraphs += 1
        self.stage_index += 1
        self.lines = []
        self.line_index = 0
        self.typed_line = ""

    def should_breathe_now(self) -> bool:
        return (
            not self.phase_completed()
            and self.line_index > 0
            and self.line_index % LINES_PER_BLOCK == 0
        )

    def pause_block_timer(self) -> None:
        if self.timer_paused:
            return
        elapsed = time.time() - self.block_started_at
        self.block_remaining = max(0.0, self.block_remaining - elapsed)
        self.timer_paused = True

    def resume_block_timer(self) -> None:
        self.block_started_at = time.time()
        self.timer_paused = False

    def remaining_block_time(self) -> float:
        if self.timer_paused:
            return self.block_remaining
        elapsed = time.time() - self.block_started_at
        return max(0.0, self.block_remaining - elapsed)

    def block_time_percent(self) -> float:
        if self.block_time_limit <= 0:
            return 100.0
        return (self.remaining_block_time() / self.block_time_limit) * 100

    def all_base_phases_done(self) -> bool:
        return self.stage_index >= len(self.phases) and not self.in_bonus

    def append_bonus_phase(self) -> None:
        bonus = {
            "title": BONUS_PHASE["title"],
            "source": BONUS_PHASE["source"],
            "text": BONUS_PHASE["text"],
            "lines": split_text_into_lines(BONUS_PHASE["text"]),
        }
        self.phases.append(bonus)
        self.stage_index = len(self.phases) - 1
        self.multiplier = 2
        self.in_bonus = True

    def bonus_done(self) -> bool:
        return self.in_bonus and self.stage_index >= len(self.phases)

    def average_speed(self) -> tuple[float, float]:
        elapsed_minutes = max((time.time() - self.game_started_at) / 60, 1 / 60)
        wpm = (self.stats.completed_chars / 5) / elapsed_minutes
        cpm = self.stats.completed_chars / elapsed_minutes
        return wpm, cpm

    def phase_total_chars(self) -> int:
        return sum(len(line) for line in self.lines) if self.lines else 0

    def completed_chars_in_current_phase(self) -> int:
        if not self.lines:
            return 0
        done = sum(len(line) for line in self.lines[: self.line_index])
        done += len(self.typed_line)
        return done

    def phase_progress(self) -> float:
        total = self.phase_total_chars()
        if total <= 0:
            return 0.0
        return max(0.0, min(1.0, self.completed_chars_in_current_phase() / total))

    def progress_text(self) -> str:
        if not self.lines:
            return "0/0"
        current = min(self.line_index + 1, len(self.lines))
        return f"linha {current}/{len(self.lines)} | caractere {len(self.typed_line)}/{len(self.current_line())}"
