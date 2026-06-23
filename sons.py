# -*- coding: utf-8 -*-
"""
Sons do jogo.
"""

from __future__ import annotations

import random
import threading
import tkinter as tk

try:
    import winsound
except ImportError:
    winsound = None


class SoundManager:
    def __init__(self, root: tk.Tk):
        self.root = root

    def beep(self, frequency: int, duration_ms: int) -> None:
        if winsound is not None:
            def worker() -> None:
                try:
                    winsound.Beep(max(37, int(frequency)), max(1, int(duration_ms)))
                except RuntimeError:
                    self.fallback_bell()

            threading.Thread(target=worker, daemon=True).start()
        else:
            self.fallback_bell()

    def fallback_bell(self) -> None:
        try:
            self.root.bell()
        except tk.TclError:
            pass

    def key(self) -> None:
        self.beep(1250 + random.randint(-150, 120), 18)

    def space(self) -> None:
        self.beep(820, 24)

    def error(self) -> None:
        self.beep(300, 130)

    def critical_loss(self) -> None:
        self.beep(220, 140)
        self.root.after(95, lambda: self.beep(530, 160))

    def success(self) -> None:
        self.beep(1500, 60)
        self.root.after(70, lambda: self.beep(1900, 75))

    def checkpoint(self) -> None:
        self.beep(1050, 40)
        self.root.after(50, lambda: self.beep(1420, 40))

    def breathe(self) -> None:
        self.beep(700, 80)

    def carriage_return(self) -> None:
        # Pequena sequência para lembrar o retorno do carro da máquina.
        self.beep(980, 35)
        self.root.after(45, lambda: self.beep(740, 35))
        self.root.after(90, lambda: self.beep(520, 45))

    def suspense(self) -> None:
        # Toque curto, grave e espaçado para criar suspense sem atrapalhar a digitação.
        self.beep(185 + random.randint(-10, 12), 90)

    def roulette_tick(self) -> None:
        self.beep(730 + random.randint(-60, 80), 15)
