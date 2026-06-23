# -*- coding: utf-8 -*-
"""
bot_manager.py

NPCs estatísticos para simular competição.

Eles não digitam de verdade. Apenas avançam na barra de progresso
com base em velocidade de WPM/CPM.

Nesta versão:
- NPC Yuri: 25.1 WPM / 125.5 CPM
- NPC Ana: metade da velocidade do Yuri:
  12.55 WPM / 62.75 CPM
"""

from __future__ import annotations

from dataclasses import dataclass
import random
import time


@dataclass
class BotPlayer:
    name: str
    wpm: float
    cpm: float
    delay: float = 0.0
    variation: float = 1.0


class BotManager:
    def __init__(self, count: int = 2):
        self.bots: list[BotPlayer] = []
        self.stage_started_at = time.time()
        self.total_chars = 1
        self.enabled = True
        self.reset_bots(count)

    def reset_bots(self, count: int = 2) -> None:
        """
        Cria bots com velocidades diferentes.
        Ana fica propositalmente com metade da velocidade de Yuri.
        """
        templates = [
            {
                "name": "NPC Ana",
                "wpm": 12.55,
                "cpm": 62.75,
            },
            {
                "name": "NPC Yuri",
                "wpm": 25.1,
                "cpm": 125.5,
            },
            {
                "name": "NPC Theo",
                "wpm": 21.0,
                "cpm": 105.0,
            },
            {
                "name": "NPC Lumi",
                "wpm": 18.0,
                "cpm": 90.0,
            },
        ]

        self.bots = []

        for index in range(max(0, count)):
            template = templates[index % len(templates)]
            self.bots.append(
                BotPlayer(
                    name=template["name"],
                    wpm=template["wpm"],
                    cpm=template["cpm"],
                    delay=random.uniform(0.2, 1.8),
                    variation=random.uniform(0.97, 1.03),
                )
            )

    def start_stage(self, total_chars: int) -> None:
        self.stage_started_at = time.time()
        self.total_chars = max(1, int(total_chars))

        for bot in self.bots:
            bot.delay = random.uniform(0.2, 1.8)
            bot.variation = random.uniform(0.97, 1.03)

    def progress_for(self, bot: BotPlayer) -> float:
        if not self.enabled:
            return 0.0

        elapsed = max(0.0, time.time() - self.stage_started_at - bot.delay)
        chars_done = (bot.cpm * bot.variation) * (elapsed / 60)
        return max(0.0, min(1.0, chars_done / self.total_chars))

    def snapshots(self) -> list[dict]:
        data = []

        for index, bot in enumerate(self.bots, start=1):
            progress = self.progress_for(bot)
            chars_done = int(progress * self.total_chars)

            data.append(
                {
                    "kind": "bot",
                    "label": f"B{index}",
                    "name": bot.name,
                    "progress": progress,
                    "chars_done": chars_done,
                    "total_chars": self.total_chars,
                    "wpm": bot.wpm,
                    "cpm": bot.cpm,
                    "color_role": "opponent",
                }
            )

        return data

    def stats_text(self) -> str:
        if not self.bots:
            return "NPC: desligado"

        return " | ".join(
            f"{bot.name}: {bot.wpm:.2f} WPM / {bot.cpm:.2f} CPM"
            for bot in self.bots
        )
