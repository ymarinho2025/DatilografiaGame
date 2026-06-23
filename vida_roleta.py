# -*- coding: utf-8 -*-
"""
Controle de vidas e roleta de risco.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import random

from settings import MAX_LIVES, ROULETTE_SIDES


@dataclass
class RouletteResult:
    number: int
    critical: bool
    lost_life: bool
    remaining_lives: int


@dataclass
class LifeRouletteController:
    max_lives: int = MAX_LIVES
    sides: int = ROULETTE_SIDES
    lives: int = MAX_LIVES
    critical_number: int = field(default_factory=lambda: random.randint(1, ROULETTE_SIDES))

    def reset(self, critical_number: int | None = None) -> None:
        self.lives = self.max_lives
        if critical_number is None:
            self.critical_number = random.randint(1, self.sides)
        else:
            self.critical_number = int(critical_number)

    def spin(self) -> RouletteResult:
        number = random.randint(1, self.sides)
        critical = number == self.critical_number
        lost_life = False

        if critical:
            self.lives = max(0, self.lives - 1)
            lost_life = True

        return RouletteResult(
            number=number,
            critical=critical,
            lost_life=lost_life,
            remaining_lives=self.lives,
        )

    def is_game_over(self) -> bool:
        return self.lives <= 0

    def hearts(self) -> str:
        filled = "❤ " * self.lives
        empty = "♡ " * (self.max_lives - self.lives)
        return (filled + empty).strip()
