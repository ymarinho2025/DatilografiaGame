# -*- coding: utf-8 -*-
"""
Desenhos do jogo: mesa, papel, máquina, linhas, checkpoints e roleta.
"""

from __future__ import annotations

import math
import random
import tkinter as tk

from settings import COLORS, FONTS, MAX_CHARS_PER_LINE, LINES_PER_BLOCK


class TypewriterVisual:
    def __init__(self):
        self.colors = COLORS
        self.fonts = FONTS
        self.stars = [(random.randint(10, 1190), random.randint(8, 130)) for _ in range(80)]

    def draw_start_art(self, canvas: tk.Canvas) -> None:
        c = self.colors
        canvas.delete("all")
        canvas.create_rectangle(0, 0, 960, 130, fill="#111c33", outline="")
        canvas.create_rectangle(0, 130, 960, 330, fill=c["wood"], outline="")

        for y in range(145, 330, 24):
            canvas.create_line(0, y, 960, y + 6, fill=c["wood2"])

        rng = random.Random(19)
        for _ in range(55):
            x = rng.randint(10, 940)
            y = rng.randint(8, 112)
            canvas.create_oval(x, y, x + 2, y + 2, fill="#f5f7fb", outline="")

        canvas.create_rectangle(365, 35, 595, 222, fill=c["paper_shadow"], outline="")
        canvas.create_rectangle(350, 25, 580, 210, fill=c["paper"], outline="#d8c997", width=2)
        canvas.create_text(465, 60, text="CARTAS AO FAROL", fill=c["ink"], font=("Courier New", 22, "bold"))
        canvas.create_text(465, 102, text="a folha espera", fill="#6b5d3d", font=("Courier New", 14, "bold"))
        canvas.create_text(465, 137, text="a primeira tecla", fill="#6b5d3d", font=("Courier New", 14, "bold"))

        canvas.create_oval(250, 170, 710, 315, fill=c["metal"], outline="#101520", width=5)
        canvas.create_rectangle(285, 212, 675, 315, fill=c["metal_light"], outline="#101520", width=4)
        canvas.create_rectangle(325, 235, 635, 272, fill="#111827", outline="")
        canvas.create_text(480, 254, text="mesa de datilografia", fill=c["accent"], font=("Segoe UI", 14, "bold"))

    def draw_scene(
        self,
        canvas: tk.Canvas,
        phase_title: str,
        phase_source: str,
        lines: list[str],
        line_index: int,
        typed_line: str,
        wrong_char: str | None,
        active_key: str | None,
        completed_paragraphs: int,
        total_phases: int,
        line_ready: bool = False,
        carriage_offset: int = 0,
        race_markers: list[dict] | None = None,
    ) -> None:
        c = self.colors
        canvas.delete("all")
        w = canvas.winfo_width() or 1180
        h = canvas.winfo_height() or 555
        cx = w // 2

        canvas.create_rectangle(0, 0, w, int(h * 0.24), fill="#111c33", outline="")
        canvas.create_rectangle(0, int(h * 0.24), w, h, fill=c["wood"], outline="")

        for y in range(int(h * 0.24) + 8, h, 24):
            canvas.create_line(0, y, w, y + 6, fill=c["wood2"])

        for x, y in self.stars:
            if x < w and y < int(h * 0.22):
                canvas.create_oval(x, y, x + 2, y + 2, fill="#f5f7fb", outline="")

        self.draw_lighthouse(canvas, w, h, completed_paragraphs, total_phases)

        table_top = int(h * 0.28)
        canvas.create_rectangle(45, table_top, w - 45, h - 18, fill=c["wood2"], outline=c["wood_dark"], width=4)

        paper_w = min(930, w - 230)
        paper_h = 310
        px1 = cx - paper_w // 2 + carriage_offset
        py1 = 30
        px2 = px1 + paper_w
        py2 = py1 + paper_h

        canvas.create_rectangle(px1 + 16, py1 + 13, px2 + 16, py2 + 13, fill=c["paper_shadow"], outline="")
        border_color = c["accent"] if line_ready else "#d8c997"
        border_width = 5 if line_ready else 2
        canvas.create_rectangle(px1, py1, px2, py2, fill=c["paper"], outline=border_color, width=border_width)

        canvas.create_text(
            cx,
            py1 + 18,
            text=f"FASE: {phase_title.upper()}",
            fill="#7a6a47",
            font=("Segoe UI", 10, "bold"),
        )
        canvas.create_text(
            cx,
            py1 + 36,
            text=phase_source,
            fill="#958663",
            font=("Segoe UI", 9, "italic"),
        )
        self.draw_line_block(canvas, px1 + 36, py1 + 70, lines, line_index, typed_line, wrong_char)

        if line_ready:
            canvas.create_text(
                cx,
                py2 - 18,
                text="...",
                fill=c["accent"],
                font=("Segoe UI", 22, "bold"),
            )

        body_y = py2 - 5
        canvas.create_oval(cx - 350, body_y - 42, cx + 350, body_y + 190, fill="#111827", outline="")
        canvas.create_oval(cx - 335, body_y - 54, cx + 335, body_y + 160, fill=c["metal"], outline="#101520", width=5)
        canvas.create_rectangle(cx - 305, body_y + 5, cx + 305, body_y + 170, fill=c["metal"], outline="#101520", width=5)
        canvas.create_rectangle(cx - 250, body_y - 22, cx + 250, body_y + 25, fill=c["metal_light"], outline="#101520", width=3)
        canvas.create_rectangle(cx - 260, body_y + 40, cx + 260, body_y + 80, fill="#111827", outline="#050813", width=3)
        canvas.create_text(cx, body_y + 60, text="A MAQUINA ESCUTA CADA TOQUE", fill=c["accent"], font=("Segoe UI", 13, "bold"))

        hammer_offset = (len(typed_line) % 11) - 5
        hammer_x = cx + hammer_offset * 16
        canvas.create_line(cx - 95, body_y + 32, hammer_x, py2 - 16, fill="#b7c0cc", width=3)
        canvas.create_line(cx + 95, body_y + 32, hammer_x + 8, py2 - 16, fill="#b7c0cc", width=3)
        canvas.create_oval(hammer_x - 8, py2 - 25, hammer_x + 16, py2 - 2, fill="#cfd6df", outline="#101520")

        self.draw_keyboard(canvas, cx, body_y + 101, active_key)

        canvas.create_text(
            35,
            h - 35,
            anchor="w",
            text="A carta avança em silêncio. Continue.",
            fill=c["accent"],
            font=("Segoe UI", 12, "bold"),
        )

        if wrong_char is not None:
            canvas.create_text(
                w - 35,
                h - 35,
                anchor="e",
                text="Algo saiu fora da ordem.",
                fill=c["danger"],
                font=("Segoe UI", 12, "bold"),
            )

    def draw_line_block(
        self,
        canvas: tk.Canvas,
        x: int,
        y: int,
        lines: list[str],
        line_index: int,
        typed_line: str,
        wrong_char: str | None,
    ) -> None:
        c = self.colors
        if not lines:
            return

        block_start = (line_index // LINES_PER_BLOCK) * LINES_PER_BLOCK
        block_end = min(block_start + LINES_PER_BLOCK, len(lines))
        char_w = 12
        line_h = 52

        # Mantém o texto centralizado na folha, sem explicar mecanicamente
        # onde há checkpoint, blocos ou contagem de caracteres.
        max_line_len = max((len(line) for line in lines[block_start:block_end]), default=1)
        usable_w = MAX_CHARS_PER_LINE * char_w
        start_x = x + max(0, (usable_w - max_line_len * char_w) // 2)

        for idx in range(block_start, block_end):
            line = lines[idx]
            row = idx - block_start
            line_y = y + row * line_h
            line_x = start_x + max(0, (max_line_len - len(line)) * char_w // 2)

            if idx < line_index:
                canvas.create_text(
                    line_x,
                    line_y,
                    anchor="w",
                    text=line,
                    fill=c["safe"],
                    font=self.fonts["paper"],
                )
                continue

            if idx > line_index:
                canvas.create_text(
                    line_x,
                    line_y,
                    anchor="w",
                    text=line,
                    fill="#6d6248",
                    font=self.fonts["paper"],
                )
                continue

            for i, ch in enumerate(line):
                draw_x = line_x + i * char_w

                if i < len(typed_line):
                    color = c["safe"]
                    display = ch
                elif i == len(typed_line) and wrong_char is not None:
                    color = c["danger"]
                    display = wrong_char
                elif i == len(typed_line):
                    color = c["accent"]
                    display = ch
                else:
                    color = "#6d6248"
                    display = ch

                canvas.create_text(draw_x, line_y, anchor="w", text=display, fill=color, font=self.fonts["paper"])

                if i == len(typed_line) and wrong_char is None:
                    canvas.create_line(draw_x, line_y + 14, draw_x + 10, line_y + 14, fill=c["accent"], width=2)

    def draw_race_progress_line(
        self,
        canvas: tk.Canvas,
        x1: int,
        y: int,
        x2: int,
        markers: list[dict],
    ) -> None:
        c = self.colors
        canvas.delete("all")

        w = canvas.winfo_width() or 1000
        h = canvas.winfo_height() or 70

        # Fundo discreto
        canvas.create_rectangle(0, 0, w, h, fill="#0f1a2b", outline="")

        # Linha principal de corrida
        canvas.create_line(x1, y, x2, y, fill="#7a6a47", width=4)

        # Marcadores todos alinhados na mesma linha
        ordered = sorted(markers, key=lambda item: 0 if item.get("kind") == "self" else 1)

        for marker in ordered:
            progress = max(0.0, min(1.0, float(marker.get("progress", 0.0))))
            mx = int(x1 + (x2 - x1) * progress)

            kind = marker.get("kind", "opponent")
            label = str(marker.get("label", "?"))

            if kind == "self":
                fill = c["self_blue"]
                outline = "#d7ecff"
                radius = 13
            elif kind == "opponent":
                fill = c["opponent_red"]
                outline = "#ffd6df"
                radius = 12
            else:
                fill = c["bot_red"]
                outline = "#ffd6df"
                radius = 12

            # Linha vertical pequena para reforçar posição
            canvas.create_line(mx, y - 14, mx, y + 14, fill=fill, width=2)

            canvas.create_oval(
                mx - radius,
                y - radius,
                mx + radius,
                y + radius,
                fill=fill,
                outline=outline,
                width=2,
            )
            canvas.create_text(
                mx,
                y,
                text=label,
                fill="white",
                font=("Segoe UI", 10, "bold"),
            )

        # Legenda pequena
        canvas.create_text(
            x1,
            y - 22,
            anchor="w",
            text="corrida da frase",
            fill="#f3cd6b",
            font=("Segoe UI", 10, "bold"),
        )

        canvas.create_text(
            x2,
            y - 22,
            anchor="e",
            text="fim",
            fill="#7a6a47",
            font=("Segoe UI", 9, "bold"),
        )

    def draw_lighthouse(self, canvas: tk.Canvas, w: int, h: int, completed: int, total: int) -> None:
        c = self.colors
        tower_x = int(w * 0.89)
        canvas.create_oval(int(w * 0.79), int(h * 0.20), w + 50, int(h * 0.33), fill="#2f3e46", outline="")
        canvas.create_rectangle(tower_x, 45, tower_x + 52, int(h * 0.25), fill="#e9ecef", outline="")
        canvas.create_polygon(
            tower_x - 8, 45, tower_x + 60, 45, tower_x + 43, 20, tower_x + 9, 20,
            fill=c["danger"], outline="",
        )
        canvas.create_rectangle(tower_x + 18, 63, tower_x + 35, 86, fill=c["accent"], outline="")

        progress = completed / max(total, 1)
        if progress > 0:
            canvas.create_polygon(
                tower_x + 26, 75, int(w * 0.50), 38, int(w * 0.50), 125,
                fill=c["accent"], outline="", stipple="gray50" if progress < 0.55 else "gray25",
            )

    def draw_keyboard(self, canvas: tk.Canvas, cx: int, y: int, active_key: str | None) -> None:
        c = self.colors
        rows = [
            ("qwertyuiop", cx - 226),
            ("asdfghjkl", cx - 202),
            ("zxcvbnm", cx - 158),
        ]
        key_w, key_h, gap = 38, 30, 7

        for row_index, (letters, start_x) in enumerate(rows):
            row_y = y + row_index * 39
            for i, letter in enumerate(letters):
                x = start_x + i * (key_w + gap)
                active = active_key == letter
                fill = c["key_active"] if active else c["key"]
                fg = "#0b1020" if active else c["key_text"]
                canvas.create_oval(x, row_y, x + key_w, row_y + key_h, fill=fill, outline="#738095", width=2)
                canvas.create_text(x + key_w // 2, row_y + key_h // 2, text=letter.upper(), fill=fg, font=("Consolas", 12, "bold"))

        active_space = active_key == "space"
        fill = c["key_active"] if active_space else c["key"]
        fg = "#0b1020" if active_space else c["key_text"]
        sx1 = cx - 130
        sy1 = y + 122
        canvas.create_rectangle(sx1, sy1, sx1 + 260, sy1 + 26, fill=fill, outline="#738095", width=2)
        canvas.create_text(cx, sy1 + 13, text="ESPAÇO", fill=fg, font=("Segoe UI", 10, "bold"))

    def draw_roulette(self, canvas: tk.Canvas, selected: int, critical_number: int, final: bool) -> None:
        c = self.colors
        w = canvas.winfo_width() or 1180
        h = canvas.winfo_height() or 555
        cx = int(w * 0.17)
        cy = int(h * 0.52)
        radius = 84

        canvas.create_oval(cx - 126, cy - 126, cx + 126, cy + 126, fill="#0b1020", outline=c["accent"], width=4)
        canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill="#1b2435", outline="#738095", width=3)

        for i in range(6):
            n = i + 1
            angle = math.radians(-90 + i * 60)
            x = cx + int(55 * math.cos(angle))
            y = cy + int(55 * math.sin(angle))
            is_selected = n == selected
            is_critical = n == critical_number

            if is_selected:
                fill = c["danger"] if final and is_critical else c["accent"]
                fg = "white" if fill == c["danger"] else "#0b1020"
                size = 38
            else:
                fill = "#2f3a4a"
                fg = c["text"]
                size = 31

            canvas.create_oval(x - size, y - size, x + size, y + size, fill=fill, outline="#dce3ee", width=2)
            canvas.create_text(x, y, text=str(n), fill=fg, font=("Segoe UI", 20, "bold"))

        canvas.create_oval(cx - 19, cy - 19, cx + 19, cy + 19, fill=c["accent2"], outline="")
        canvas.create_polygon(cx - 14, cy - 111, cx + 14, cy - 111, cx, cy - 82, fill=c["accent"], outline="")
        canvas.create_text(cx, cy - 145, text="ROLETA DE RISCO", fill=c["accent"], font=("Segoe UI", 15, "bold"))
        canvas.create_text(cx, cy + 145, text=f"Número crítico: {critical_number}", fill=c["danger"], font=("Segoe UI", 13, "bold"))

    def draw_victory_art(self, canvas: tk.Canvas) -> None:
        c = self.colors
        canvas.delete("all")
        canvas.create_rectangle(0, 0, 940, 130, fill="#14324a", outline="")
        canvas.create_rectangle(0, 130, 940, 310, fill=c["wood"], outline="")

        canvas.create_oval(75, 34, 140, 99, fill=c["accent"], outline="")
        canvas.create_rectangle(620, 45, 695, 174, fill="#e9ecef", outline="")
        canvas.create_polygon(610, 45, 705, 45, 680, 16, 635, 16, fill=c["danger"], outline="")
        canvas.create_rectangle(647, 66, 670, 93, fill=c["accent"], outline="")
        canvas.create_polygon(658, 78, 155, 25, 155, 140, fill=c["accent"], outline="", stipple="gray25")

        canvas.create_rectangle(325, 55, 560, 215, fill=c["paper_shadow"], outline="")
        canvas.create_rectangle(310, 43, 545, 203, fill=c["paper"], outline="#d8c997", width=2)
        canvas.create_text(427, 98, text="A CARTA CHEGOU", fill=c["ink"], font=("Courier New", 18, "bold"))
        canvas.create_text(427, 134, text="fim da travessia", fill="#7a6a47", font=("Courier New", 13, "bold"))

        canvas.create_oval(235, 177, 705, 300, fill=c["metal"], outline="#101520", width=5)
        canvas.create_rectangle(268, 215, 672, 300, fill=c["metal_light"], outline="#101520", width=4)
        canvas.create_text(470, 244, text="a ultima tecla acendeu o farol", fill=c["accent"], font=("Segoe UI", 15, "bold"))
