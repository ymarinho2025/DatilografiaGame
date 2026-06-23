# -*- coding: utf-8 -*-
"""
Interface principal do jogo.
"""

from __future__ import annotations

import random
import tkinter as tk
from tkinter import ttk

from settings import (
    APP_TITLE,
    WINDOW_GEOMETRY,
    WINDOW_MIN_SIZE,
    COLORS,
    FONTS,
    BREATH_SECONDS,
    LINES_PER_BLOCK,
    LINE_READY_SECONDS,
    BACKGROUND_SUSPENSE_MS,
    BOT_COUNT,
)
from bot_manager import BotManager
from utils import normalize_key
from sons import SoundManager
from visual import TypewriterVisual
from estado_jogo import GameState
from vida_roleta import LifeRouletteController


class TypewriterGameApp:
    def __init__(self, root: tk.Tk, network=None, player_name: str = "Jogador"):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_GEOMETRY)
        self.root.minsize(*WINDOW_MIN_SIZE)

        self.colors = COLORS
        self.fonts = FONTS
        self.sound = SoundManager(root)
        self.visual = TypewriterVisual()
        self.state = GameState()
        self.life = LifeRouletteController()
        self.network = network
        self.player_name = player_name or "Jogador"
        self.network_status_text = "Modo solo"
        self.opponent_snapshot = None
        self.bots = BotManager(count=BOT_COUNT)

        self.state.load_record()

        self.frame: tk.Frame | None = None
        self.canvas: tk.Canvas | None = None
        self.timer_bar: ttk.Progressbar | None = None
        self.lives_label: tk.Label | None = None
        self.score_label: tk.Label | None = None
        self.progress_label: tk.Label | None = None
        self.risk_label: tk.Label | None = None
        self.stats_label: tk.Label | None = None
        self.opponent_label: tk.Label | None = None
        self.status_label: tk.Label | None = None
        self.race_canvas: tk.Canvas | None = None
        self.roulette_label: tk.Label | None = None
        self.expected_label: tk.Label | None = None

        self.timer_job = None
        self.stats_job = None
        self.roulette_job = None
        self.key_flash_job = None
        self.breath_job = None
        self.line_ready_job = None
        self.background_sound_job = None
        self.line_ready_job = None
        self.background_sound_job = None
        self.wrong_char: str | None = None
        self.active_key: str | None = None
        self.timeout_failure = False
        self.line_ready_mode = False
        self.carriage_offset = 0

        self.configure_style()
        self.show_start_screen()

    # ------------------------------------------------------------------
    # Base visual
    # ------------------------------------------------------------------

    def configure_style(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Light.Horizontal.TProgressbar",
            troughcolor=self.colors["panel"],
            background=self.colors["accent"],
            bordercolor=self.colors["panel"],
            lightcolor=self.colors["accent"],
            darkcolor=self.colors["accent"],
        )

    def clear_screen(self) -> None:
        for job in (self.timer_job, self.stats_job, self.roulette_job, self.key_flash_job, self.breath_job, self.line_ready_job, self.background_sound_job):
            if job is not None:
                try:
                    self.root.after_cancel(job)
                except tk.TclError:
                    pass

        self.timer_job = None
        self.stats_job = None
        self.roulette_job = None
        self.key_flash_job = None
        self.breath_job = None
        self.line_ready_job = None
        self.background_sound_job = None

        self.root.unbind("<KeyPress>")

        for widget in self.root.winfo_children():
            widget.destroy()

        self.frame = tk.Frame(self.root, bg=self.colors["bg"])
        self.frame.pack(fill="both", expand=True)

    def button(self, parent, text: str, command, width: int = 20):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=self.fonts["button"],
            bg=self.colors["accent"],
            fg="#0b1020",
            activebackground="#ffe08a",
            activeforeground="#0b1020",
            relief="flat",
            bd=0,
            padx=14,
            pady=9,
            width=width,
            cursor="hand2",
        )

    # ------------------------------------------------------------------
    # Telas iniciais
    # ------------------------------------------------------------------

    def show_start_screen(self) -> None:
        self.clear_screen()

        outer = tk.Frame(self.frame, bg=self.colors["bg"])
        outer.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            outer,
            text="Cartas para o Farol",
            font=self.fonts["title"],
            bg=self.colors["bg"],
            fg=self.colors["accent"],
        ).pack(pady=(0, 6))

        tk.Label(
            outer,
            text="A carta já está na máquina. Quando começar, o tempo corre.",
            font=self.fonts["subtitle"],
            bg=self.colors["bg"],
            fg=self.colors["text"],
        ).pack(pady=(0, 14))

        canvas = tk.Canvas(outer, width=960, height=330, bg=self.colors["night"], highlightthickness=0)
        canvas.pack(pady=(0, 16))
        self.visual.draw_start_art(canvas)

        record = (
            f"Recorde: {self.state.record['score']} pontos | "
            f"{self.state.record['wpm']:.1f} WPM | {self.state.record['cpm']:.1f} CPM"
        )
        tk.Label(
            outer,
            text=record,
            font=("Segoe UI", 11, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["accent2"],
        ).pack(pady=(0, 8))

        lan_line = ""
        if self.network is not None:
            lan_line = f"\nLAN: {self.network_status_text}"

        msg = (
            "Observe a folha, siga o texto e digite sem apertar Enter.\n"
            "Cada toque será analisado no instante em que acontecer.\n"
            "A máquina não explica tudo: você descobre o ritmo jogando."
            + lan_line
        )
        tk.Label(
            outer,
            text=msg,
            font=self.fonts["normal"],
            bg=self.colors["bg"],
            fg=self.colors["muted"],
            justify="center",
        ).pack(pady=(0, 18))

        buttons = tk.Frame(outer, bg=self.colors["bg"])
        buttons.pack()
        self.button(buttons, "Iniciar jogo", self.start_game).grid(row=0, column=0, padx=7)
        self.button(buttons, "Como jogar", self.show_how_to_play, width=16).grid(row=0, column=1, padx=7)
        self.button(buttons, "Sair", self.root.destroy, width=12).grid(row=0, column=2, padx=7)

    def show_how_to_play(self) -> None:
        self.clear_screen()
        box = tk.Frame(self.frame, bg=self.colors["panel"], padx=35, pady=35)
        box.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            box,
            text="Como jogar",
            font=self.fonts["title"],
            bg=self.colors["panel"],
            fg=self.colors["accent"],
        ).pack(pady=(0, 18))

        text = (
            "1. Leia o texto na folha.\n"
            "2. Digite na mesma ordem, sem apertar Enter.\n"
            "3. Espaços, vírgulas e pontos fazem parte do texto real.\n"
            "4. Se sair da ordem, a roleta aparece.\n"
            "5. Se cair no número crítico, você perde 1 vida.\n"
            "6. Com 3 vidas perdidas, aparece VOCÊ PERDEU.\n"
            "7. O restante você descobre jogando."
        )
        tk.Label(
            box,
            text=text,
            font=("Segoe UI", 13),
            justify="left",
            bg=self.colors["panel"],
            fg=self.colors["text"],
        ).pack(pady=(0, 24))

        self.button(box, "Voltar", self.show_start_screen, width=14).pack()

    def start_background_suspense(self) -> None:
        if self.background_sound_job is not None:
            try:
                self.root.after_cancel(self.background_sound_job)
            except tk.TclError:
                pass

        def pulse() -> None:
            if self.frame is not None and self.canvas is not None:
                self.sound.suspense()
                self.background_sound_job = self.root.after(BACKGROUND_SUSPENSE_MS, pulse)

        self.background_sound_job = self.root.after(BACKGROUND_SUSPENSE_MS, pulse)

    def show_waiting_screen(self) -> None:
        self.clear_screen()

        box = tk.Frame(self.frame, bg=self.colors["panel"], padx=35, pady=35)
        box.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            box,
            text="Aguardando partida",
            font=self.fonts["title"],
            bg=self.colors["panel"],
            fg=self.colors["accent"],
        ).pack(pady=(0, 14))

        tk.Label(
            box,
            text=self.network_status_text,
            font=("Segoe UI", 14),
            bg=self.colors["panel"],
            fg=self.colors["text"],
            justify="center",
            wraplength=720,
        ).pack(pady=(0, 22))

        self.button(box, "Menu", self.show_start_screen, width=12).pack()

    def on_network_status(self, text: str) -> None:
        self.network_status_text = text

        if self.opponent_label is not None:
            self.opponent_label.config(text=f"LAN: {text}")

    def on_network_message(self, msg: dict) -> None:
        msg_type = msg.get("type")
        payload = msg.get("payload") or {}
        name = msg.get("name", "Jogador")

        if msg_type == "hello":
            self.opponent_snapshot = {"name": name, "status": "conectado"}
            if self.opponent_label is not None:
                self.opponent_label.config(text=f"Adversário: {name} conectado")
            return

        if msg_type == "request_start":
            if self.network is not None and getattr(self.network.status, "role", "solo") == "host":
                self.start_game()
            return

        if msg_type == "start_game":
            self.start_game(
                seed=payload.get("seed"),
                critical_number=payload.get("critical_number"),
                notify_network=False,
            )
            return

        if msg_type == "snapshot":
            self.opponent_snapshot = {
                "name": name,
                "score": payload.get("score", 0),
                "lives": payload.get("lives", 0),
                "phase": payload.get("phase", "—"),
                "line": payload.get("line", 0),
                "total_lines": payload.get("total_lines", 0),
                "status": payload.get("status", "jogando"),
                "stage_index": payload.get("stage_index", 0),
                "progress": payload.get("progress", 0.0),
                "chars_done": payload.get("chars_done", 0),
                "total_chars": payload.get("total_chars", 0),
            }
            self.update_opponent_label()
            return

        if msg_type == "game_over":
            self.opponent_snapshot = {
                "name": name,
                "status": "perdeu",
                "score": payload.get("score", 0),
                "lives": 0,
                "phase": payload.get("phase", "—"),
                "line": payload.get("line", 0),
                "total_lines": payload.get("total_lines", 0),
            }
            self.update_opponent_label()
            return

        if msg_type == "victory":
            self.opponent_snapshot = {
                "name": name,
                "status": "venceu",
                "score": payload.get("score", 0),
                "lives": payload.get("lives", 0),
                "phase": payload.get("phase", "—"),
                "line": payload.get("line", 0),
                "total_lines": payload.get("total_lines", 0),
            }
            self.update_opponent_label()

    def send_snapshot(self, status: str = "jogando") -> None:
        if self.network is None or not getattr(self.network.status, "connected", False):
            return

        phase = self.state.current_phase()
        self.network.send(
            "snapshot",
            {
                "score": self.state.score,
                "lives": self.life.lives,
                "phase": phase.get("title", "—"),
                "line": min(self.state.line_index + 1, max(len(self.state.lines), 1)),
                "total_lines": len(self.state.lines),
                "status": status,
                "stage_index": self.state.stage_index,
                "progress": self.state.phase_progress(),
                "chars_done": self.state.completed_chars_in_current_phase(),
                "total_chars": self.state.phase_total_chars(),
            },
        )

    def update_opponent_label(self) -> None:
        if self.opponent_label is None:
            return

        if not self.opponent_snapshot:
            self.opponent_label.config(text=f"LAN: {self.network_status_text}")
            return

        snap = self.opponent_snapshot
        progress = float(snap.get("progress", 0.0)) * 100
        text = (
            f"Adversário: {snap.get('name', 'Jogador')} | "
            f"{snap.get('status', 'jogando')} | "
            f"{snap.get('score', 0)} pts | "
            f"vidas {snap.get('lives', 0)} | "
            f"{progress:.0f}%"
        )
        self.opponent_label.config(text=text)

    # ------------------------------------------------------------------
    # Fluxo
    # ------------------------------------------------------------------

    def start_game(self) -> None:
        self.state.reset()
        self.life.reset()
        self.wrong_char = None
        self.active_key = None
        self.timeout_failure = False
        self.line_ready_mode = False
        self.carriage_offset = 0
        self.line_ready_mode = False
        self.carriage_offset = 0
        self.show_game_screen()

    def show_game_screen(self) -> None:
        self.clear_screen()

        top = tk.Frame(self.frame, bg=self.colors["panel"], padx=16, pady=10)
        top.pack(fill="x")

        self.lives_label = tk.Label(top, text="", font=("Segoe UI", 13, "bold"), bg=self.colors["panel"], fg=self.colors["danger"])
        self.lives_label.pack(side="left", padx=(0, 16))

        self.score_label = tk.Label(top, text="", font=("Segoe UI", 13, "bold"), bg=self.colors["panel"], fg=self.colors["text"])
        self.score_label.pack(side="left", padx=(0, 16))

        self.progress_label = tk.Label(top, text="", font=("Segoe UI", 13, "bold"), bg=self.colors["panel"], fg=self.colors["accent2"])
        self.progress_label.pack(side="left", padx=(0, 16))

        self.risk_label = tk.Label(top, text="", font=("Segoe UI", 12, "bold"), bg=self.colors["panel"], fg=self.colors["warning"])
        self.risk_label.pack(side="right")

        stats_bar = tk.Frame(self.frame, bg=self.colors["panel2"], padx=16, pady=8)
        stats_bar.pack(fill="x")

        self.stats_label = tk.Label(stats_bar, text="", font=self.fonts["mono"], bg=self.colors["panel2"], fg=self.colors["accent"])
        self.stats_label.pack(side="left")

        self.opponent_label = tk.Label(
            stats_bar,
            text="",
            font=("Segoe UI", 11, "bold"),
            bg=self.colors["panel2"],
            fg=self.colors["accent2"],
        )
        self.opponent_label.pack(side="right")
        self.update_opponent_label()

        self.canvas = tk.Canvas(self.frame, bg=self.colors["night"], height=555, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=18, pady=(12, 8))
        self.canvas.bind("<Button-1>", lambda event: self.root.focus_set())

        timer_frame = tk.Frame(self.frame, bg=self.colors["bg"])
        timer_frame.pack(fill="x", padx=95, pady=(0, 5))
        self.timer_bar = ttk.Progressbar(timer_frame, orient="horizontal", mode="determinate", maximum=100, value=100, style="Light.Horizontal.TProgressbar")
        self.timer_bar.pack(fill="x")

        bottom = tk.Frame(self.frame, bg=self.colors["bg"], pady=8)
        bottom.pack(fill="x")

        self.expected_label = tk.Label(bottom, text="", font=("Segoe UI", 13, "bold"), bg=self.colors["bg"], fg=self.colors["accent2"])
        self.expected_label.pack()

        self.status_label = tk.Label(
            bottom,
            text="",
            font=("Segoe UI", 13, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["text"],
            wraplength=980,
            justify="center",
        )
        self.status_label.pack(pady=(4, 3))

        self.race_canvas = tk.Canvas(
            bottom,
            width=980,
            height=72,
            bg="#0f1a2b",
            highlightthickness=0,
        )
        self.race_canvas.pack(fill="x", padx=56, pady=(4, 8))

        self.roulette_label = tk.Label(
            bottom,
            text="Roleta de risco: —",
            font=("Segoe UI", 21, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["accent2"],
        )
        self.roulette_label.pack()

        controls = tk.Frame(self.frame, bg=self.colors["bg"], pady=6)
        controls.pack(fill="x")
        self.button(controls, "Reiniciar", self.start_game, width=14).pack(side="left", padx=(20, 8))
        self.button(controls, "Menu", self.show_start_screen, width=12).pack(side="left")
        self.button(controls, "Sair", self.root.destroy, width=12).pack(side="right", padx=(8, 20))

        self.root.bind("<KeyPress>", self.on_keypress)
        self.root.focus_set()

        self.update_stats_loop()
        self.start_background_suspense()
        self.load_stage()

    def load_stage(self) -> None:
        if self.state.all_base_phases_done():
            self.show_double_or_nothing_prompt()
            return

        if self.state.bonus_done():
            self.show_victory()
            return

        self.state.load_current_stage()
        self.bots.start_stage(self.state.phase_total_chars())
        self.wrong_char = None
        self.active_key = None
        self.timeout_failure = False

        self.status_label.config(
            text="A folha entrou na máquina. O tempo começou.",
            fg=self.colors["text"],
        )
        self.roulette_label.config(text="Roleta de risco: —", fg=self.colors["accent2"])
        self.update_hud()
        self.update_expected_label()
        self.draw_scene()
        self.send_snapshot("jogando")
        self.start_timer()
        self.root.focus_set()

    def start_bonus_stage(self) -> None:
        self.state.append_bonus_phase()
        self.show_game_screen()
        self.status_label.config(
            text="Não tem por onde escapar... agora os pontos valem o dobro.",
            fg=self.colors["danger"],
        )

    def show_double_or_nothing_prompt(self) -> None:
        self.state.locked = True
        self.state.save_record()
        self.clear_screen()

        box = tk.Frame(self.frame, bg=self.colors["panel"], padx=36, pady=36)
        box.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            box,
            text="Quer prosseguir pelo dobro do prêmio?",
            font=("Segoe UI", 28, "bold"),
            bg=self.colors["panel"],
            fg=self.colors["accent"],
        ).pack(pady=(0, 14))

        tk.Label(
            box,
            text=(
                f"Pontuação atual: {self.state.score}\n"
                "Se continuar, a próxima fase vale o dobro dos pontos.\n"
                "Se recusar, talvez o jogo não aceite tão facilmente..."
            ),
            font=("Segoe UI", 14),
            bg=self.colors["panel"],
            fg=self.colors["text"],
            justify="center",
        ).pack(pady=(0, 24))

        buttons = tk.Frame(box, bg=self.colors["panel"])
        buttons.pack()
        self.button(buttons, "Sim, continuar", self.start_bonus_stage, width=18).grid(row=0, column=0, padx=8)
        self.button(buttons, "Não", self.fake_loss_then_force_bonus, width=12).grid(row=0, column=1, padx=8)

    def fake_loss_then_force_bonus(self) -> None:
        self.clear_screen()
        self.frame.configure(bg=self.colors["danger"])

        tk.Label(
            self.frame,
            text="VOCÊ PERDEU",
            font=("Segoe UI", 58, "bold"),
            bg=self.colors["danger"],
            fg="white",
        ).place(relx=0.5, rely=0.43, anchor="center")

        tk.Label(
            self.frame,
            text="pegadinha...",
            font=("Segoe UI", 18, "bold"),
            bg=self.colors["danger"],
            fg="white",
        ).place(relx=0.5, rely=0.56, anchor="center")

        self.root.after(3000, self.start_bonus_stage)

    # ------------------------------------------------------------------
    # Linha, checkpoint e respiração
    # ------------------------------------------------------------------

    def finish_line(self) -> None:
        self.state.locked = True

        gained = self.state.complete_line()
        self.sound.checkpoint()
        self.status_label.config(
            text=(
                f"+{gained} pontos. "
                f"Ritmo recente: {self.state.stats.last_line_wpm:.1f} WPM / "
                f"{self.state.stats.last_line_cpm:.1f} CPM."
            ),
            fg=self.colors["safe"],
        )
        self.update_hud()
        self.draw_scene()
        self.send_snapshot("jogando")

        if self.state.phase_completed():
            self.cancel_timer()
            self.state.advance_stage()
            if self.state.bonus_done():
                self.root.after(900, self.show_victory)
            else:
                self.root.after(900, self.load_stage)
            return

        if self.state.should_breathe_now():
            self.start_breath_break(BREATH_SECONDS)
            return

        self.start_line_ready_pause()

    def start_line_ready_pause(self) -> None:
        self.state.locked = True
        self.line_ready_mode = True
        self.carriage_offset = -70
        self.sound.carriage_return()
        self.status_label.config(
            text="O papel voltou. Prepare a próxima linha.",
            fg=self.colors["accent"],
        )
        self.expected_label.config(
            text="Prepare-se...",
            fg=self.colors["accent"],
        )
        self.draw_scene()

        def release() -> None:
            self.line_ready_mode = False
            self.carriage_offset = 0
            self.state.locked = False
            self.status_label.config(
                text="Continue.",
                fg=self.colors["text"],
            )
            self.update_expected_label()
            self.draw_scene()
            self.root.focus_set()

        self.line_ready_job = self.root.after(int(LINE_READY_SECONDS * 1000), release)

    def start_breath_break(self, seconds_left: int) -> None:
        self.state.locked = True
        self.cancel_timer()

        if seconds_left == BREATH_SECONDS:
            self.sound.breathe()

        self.status_label.config(
            text=f"Respire... a máquina volta em {seconds_left} segundo(s).",
            fg=self.colors["accent"],
        )
        self.expected_label.config(
            text=f"Respire: {seconds_left}",
            fg=self.colors["accent"],
        )
        self.line_ready_mode = True
        self.carriage_offset = -70
        self.draw_scene()

        if seconds_left <= 0:
            self.state.start_new_block_timer()
            self.line_ready_mode = False
            self.carriage_offset = 0
            self.state.locked = False
            self.status_label.config(
                text="O papel avançou. Continue.",
                fg=self.colors["warning"],
            )
            self.update_expected_label()
            self.draw_scene()
            self.start_timer()
            self.root.focus_set()
            return

        self.breath_job = self.root.after(1000, lambda: self.start_breath_break(seconds_left - 1))

    # ------------------------------------------------------------------
    # Digitação
    # ------------------------------------------------------------------

    def on_keypress(self, event) -> None:
        if self.state.locked:
            return

        if event.keysym in {"Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R", "Tab", "Caps_Lock", "Escape"}:
            return

        if event.keysym == "BackSpace":
            if self.state.typed_line:
                self.state.typed_line = self.state.typed_line[:-1]
                self.sound.space()
                self.active_key = "backspace"
                self.flash_key()
                self.update_expected_label()
                self.draw_scene()
            return

        char = normalize_key(event.char)
        if not char or len(char) != 1:
            return

        expected = self.state.expected_char()
        if expected is None:
            return

        self.state.register_key(correct=(char == expected))
        self.active_key = "space" if char == " " else char
        self.sound.space() if char == " " else self.sound.key()
        self.flash_key()

        if char == expected:
            self.state.add_typed_char(char)
            self.update_expected_label()
            self.draw_scene()
            self.send_snapshot("jogando")

            if self.state.line_finished():
                self.finish_line()
            return

        self.wrong_char = char
        self.draw_scene()
        self.handle_wrong(char, expected)

    def flash_key(self) -> None:
        if self.key_flash_job is not None:
            try:
                self.root.after_cancel(self.key_flash_job)
            except tk.TclError:
                pass

        def clear() -> None:
            self.active_key = None
            self.draw_scene()

        self.key_flash_job = self.root.after(120, clear)

    def handle_wrong(self, wrong: str, expected: str) -> None:
        self.state.locked = True
        self.state.reset_combo()
        self.state.pause_block_timer()
        self.sound.error()
        self.cancel_timer()
        self.timeout_failure = False

        self.status_label.config(
            text="Algo saiu fora da ordem. A roleta vai decidir o risco.",
            fg=self.colors["danger"],
        )
        self.spin_roulette()

    # ------------------------------------------------------------------
    # Timer e estatísticas
    # ------------------------------------------------------------------

    def start_timer(self) -> None:
        self.cancel_timer()
        self.tick_timer()

    def cancel_timer(self) -> None:
        if self.timer_job is not None:
            try:
                self.root.after_cancel(self.timer_job)
            except tk.TclError:
                pass
            self.timer_job = None

    def tick_timer(self) -> None:
        if self.state.locked:
            return

        percent = self.state.block_time_percent()
        self.timer_bar["value"] = percent

        if self.state.remaining_block_time() <= 0:
            self.handle_timeout()
            return

        self.timer_job = self.root.after(90, self.tick_timer)

    def handle_timeout(self) -> None:
        self.state.locked = True
        self.state.reset_combo()
        self.state.pause_block_timer()
        self.sound.error()
        self.timeout_failure = True
        self.cancel_timer()

        self.status_label.config(
            text="O tempo acabou. A roleta de risco vai girar.",
            fg=self.colors["warning"],
        )
        self.spin_roulette()

    def update_stats_loop(self) -> None:
        if self.stats_label is not None:
            import time

            wpm, cpm = self.state.average_speed()
            accuracy = self.state.stats.accuracy()
            elapsed = int(max(0, time.time() - self.state.game_started_at))
            minutes = elapsed // 60
            seconds = elapsed % 60
            remaining = int(self.state.remaining_block_time())

            self.stats_label.config(
                text=(
                    f"Velocidade: {wpm:5.1f} WPM | {cpm:5.1f} CPM   "
                    f"Precisão: {accuracy:5.1f}%   "
                    f"Tempo: {remaining:02d}s   "
                    f"Pontos: {self.state.score}   "
                    f"Total: {minutes:02d}:{seconds:02d}   "
                    f"{self.bots.stats_text()}"
                )
            )

        if not self.state.locked:
            self.stats_job = self.root.after(300, self.update_stats_loop)

    def update_hud(self) -> None:
        if self.state.phases:
            current_num = min(self.state.stage_index + 1, max(len(self.state.phases), 1))
            phase = self.state.current_phase()
            phase_text = f"Fase {current_num}/{len(self.state.phases)} | {phase['title']}"
        else:
            phase_text = "—"

        self.lives_label.config(text=f"Vidas: {self.life.hearts()}")
        self.score_label.config(text=f"Pontos: {self.state.score}")
        self.progress_label.config(text=phase_text)
        self.risk_label.config(text=f"Número crítico: {self.life.critical_number}")

    def update_expected_label(self) -> None:
        if self.expected_label is None or self.state.locked:
            return

        expected = self.state.expected_char()
        if expected is None:
            self.expected_label.config(text="Continue.", fg=self.colors["safe"])
            return

        self.expected_label.config(
            text="Continue digitando...",
            fg=self.colors["accent2"],
        )

    # ------------------------------------------------------------------
    # Roleta
    # ------------------------------------------------------------------

    def spin_roulette(self) -> None:
        spins = random.randint(18, 26)
        final_result = self.life.spin()

        def animate(step: int) -> None:
            if step < spins:
                number = (step % 6) + 1
                self.sound.roulette_tick()
                self.roulette_label.config(text=f"Roleta de risco: {number}", fg=self.colors["accent2"])
                self.draw_scene()
                self.visual.draw_roulette(self.canvas, number, self.life.critical_number, final=False)
                self.roulette_job = self.root.after(70 + step * 5, lambda: animate(step + 1))
                return

            self.resolve_roulette(final_result)

        animate(0)

    def resolve_roulette(self, result) -> None:
        self.draw_scene()
        self.visual.draw_roulette(self.canvas, result.number, self.life.critical_number, final=True)

        if result.critical:
            self.sound.critical_loss()
            self.flash_loss("VOCÊ PERDEU UMA VIDA")
            self.roulette_label.config(
                text=f"Roleta de risco: {result.number} | VOCÊ PERDEU UMA VIDA",
                fg=self.colors["danger"],
            )

            if self.life.is_game_over():
                self.update_hud()
                self.status_label.config(text="As três vidas acabaram.", fg=self.colors["danger"])
                self.root.after(900, self.show_game_over)
                return

            self.status_label.config(
                text=f"Caiu no número crítico {result.number}. Você perdeu 1 vida.",
                fg=self.colors["danger"],
            )
        else:
            self.roulette_label.config(text=f"Roleta de risco: {result.number} | seguro", fg=self.colors["safe"])
            self.status_label.config(
                text=f"Caiu no número seguro {result.number}. Nenhuma vida foi perdida.",
                fg=self.colors["safe"],
            )

        self.wrong_char = None
        self.active_key = None
        self.update_hud()
        self.send_snapshot("jogando")
        self.root.after(1500, self.restart_same_line)

    def restart_same_line(self) -> None:
        self.state.restart_current_line_from_checkpoint()
        self.state.start_new_block_timer()
        self.timeout_failure = False
        self.wrong_char = None
        self.active_key = None
        self.line_ready_mode = False
        self.carriage_offset = 0
        self.roulette_label.config(text="Roleta de risco: —", fg=self.colors["accent2"])

        self.status_label.config(
            text="A folha voltou ao ponto seguro. O tempo recomeçou.",
            fg=self.colors["warning"],
        )

        self.update_expected_label()
        self.draw_scene()
        self.start_timer()
        self.root.focus_set()

    def flash_loss(self, message: str) -> None:
        overlay = tk.Frame(self.frame, bg=self.colors["danger"])
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        tk.Label(
            overlay,
            text=message,
            font=("Segoe UI", 42, "bold"),
            bg=self.colors["danger"],
            fg="white",
        ).place(relx=0.5, rely=0.48, anchor="center")

        self.root.after(520, overlay.destroy)

    # ------------------------------------------------------------------
    # Desenho e finais
    # ------------------------------------------------------------------

    def build_race_markers(self) -> list[dict]:
        markers: list[dict] = []

        self_progress = self.state.phase_progress()
        markers.append(
            {
                "kind": "self",
                "label": "EU",
                "name": self.player_name,
                "progress": self_progress,
                "chars_done": self.state.completed_chars_in_current_phase(),
                "total_chars": self.state.phase_total_chars(),
                "color_role": "self",
            }
        )

        others: list[dict] = []

        if self.opponent_snapshot:
            opponent_stage = int(self.opponent_snapshot.get("stage_index", self.state.stage_index))
            # Mostra o adversário na barra quando está na mesma frase/fase.
            # Se ele já mudou de fase, aparece como 100%.
            if opponent_stage == self.state.stage_index:
                opponent_progress = float(self.opponent_snapshot.get("progress", 0.0))
            elif opponent_stage > self.state.stage_index:
                opponent_progress = 1.0
            else:
                opponent_progress = 0.0

            others.append(
                {
                    "kind": "opponent",
                    "name": self.opponent_snapshot.get("name", "Adversário"),
                    "progress": opponent_progress,
                    "chars_done": self.opponent_snapshot.get("chars_done", 0),
                    "total_chars": self.opponent_snapshot.get("total_chars", self.state.phase_total_chars()),
                    "wpm": None,
                    "cpm": None,
                }
            )

        others.extend(self.bots.snapshots())

        # Ranking visual dos outros jogadores/NPCs.
        # O número 1 vermelho indica quem está mais à frente entre os adversários.
        others_sorted = sorted(others, key=lambda item: float(item.get("progress", 0.0)), reverse=True)

        for index, item in enumerate(others_sorted, start=1):
            item = dict(item)
            item["label"] = str(index)
            if item.get("kind") == "bot":
                item["label"] = f"B{index}"
            markers.append(item)

        return markers

    def draw_scene(self) -> None:
        phase = self.state.current_phase()
        markers = self.build_race_markers()

        self.visual.draw_scene(
            canvas=self.canvas,
            phase_title=phase["title"],
            phase_source=phase["source"],
            lines=self.state.lines,
            line_index=self.state.line_index,
            typed_line=self.state.typed_line,
            wrong_char=self.wrong_char,
            active_key=self.active_key,
            completed_paragraphs=self.state.stats.completed_paragraphs,
            total_phases=len(self.state.phases),
            line_ready=self.line_ready_mode,
            carriage_offset=self.carriage_offset,
            race_markers=markers,
        )

        if self.race_canvas is not None:
            self.visual.draw_race_progress_line(
                canvas=self.race_canvas,
                x1=45,
                y=38,
                x2=max(200, (self.race_canvas.winfo_width() or 980) - 45),
                markers=markers,
            )

    def show_game_over(self) -> None:
        self.state.save_record()
        if self.network is not None:
            self.network.send(
                "game_over",
                {
                    "score": self.state.score,
                    "phase": self.state.current_phase().get("title", "—"),
                    "line": self.state.line_index,
                    "total_lines": len(self.state.lines),
                },
            )
        self.clear_screen()
        self.frame.configure(bg=self.colors["danger"])

        wpm, cpm = self.state.average_speed()
        accuracy = self.state.stats.accuracy()

        tk.Label(
            self.frame,
            text="VOCÊ PERDEU",
            font=("Segoe UI", 58, "bold"),
            bg=self.colors["danger"],
            fg="white",
        ).place(relx=0.5, rely=0.30, anchor="center")

        tk.Label(
            self.frame,
            text="As três vidas acabaram.",
            font=("Segoe UI", 18, "bold"),
            bg=self.colors["danger"],
            fg="white",
        ).place(relx=0.5, rely=0.43, anchor="center")

        stats = (
            f"Pontos: {self.state.score}\n"
            f"Velocidade média: {wpm:.1f} WPM / {cpm:.1f} CPM\n"
            f"Precisão: {accuracy:.1f}%\n"
            f"Melhor combo: x{self.state.best_combo}"
        )
        tk.Label(
            self.frame,
            text=stats,
            font=("Consolas", 16, "bold"),
            bg=self.colors["danger"],
            fg="white",
            justify="center",
        ).place(relx=0.5, rely=0.58, anchor="center")

        buttons = tk.Frame(self.frame, bg=self.colors["danger"])
        buttons.place(relx=0.5, rely=0.76, anchor="center")
        self.button(buttons, "Tentar novamente", self.start_game, width=18).grid(row=0, column=0, padx=8)
        self.button(buttons, "Menu", self.show_start_screen, width=12).grid(row=0, column=1, padx=8)

    def show_victory(self) -> None:
        self.state.save_record()
        if self.network is not None:
            self.network.send(
                "victory",
                {
                    "score": self.state.score,
                    "lives": self.life.lives,
                    "phase": self.state.current_phase().get("title", "—"),
                    "line": self.state.line_index,
                    "total_lines": len(self.state.lines),
                },
            )
        self.clear_screen()

        outer = tk.Frame(self.frame, bg=self.colors["bg"])
        outer.place(relx=0.5, rely=0.5, anchor="center")

        canvas = tk.Canvas(outer, width=940, height=310, bg=self.colors["night"], highlightthickness=0)
        canvas.pack(pady=(0, 18))
        self.visual.draw_victory_art(canvas)

        tk.Label(
            outer,
            text="Vitória!",
            font=self.fonts["title"],
            bg=self.colors["bg"],
            fg=self.colors["safe"],
        ).pack(pady=(0, 8))

        wpm, cpm = self.state.average_speed()
        accuracy = self.state.stats.accuracy()

        tk.Label(
            outer,
            text="A última folha saiu da máquina. O farol acendeu e a carta chegou ao destino.",
            font=("Segoe UI", 14, "italic"),
            bg=self.colors["bg"],
            fg=self.colors["text"],
            wraplength=900,
            justify="center",
        ).pack(pady=(0, 18))

        stats = (
            f"Pontuação final: {self.state.score}\n"
            f"Velocidade média: {wpm:.1f} WPM / {cpm:.1f} CPM\n"
            f"Precisão: {accuracy:.1f}% | Melhor combo: x{self.state.best_combo}\n"
            f"Recorde salvo: {self.state.record['score']} pontos | "
            f"{self.state.record['wpm']:.1f} WPM | {self.state.record['cpm']:.1f} CPM"
        )
        tk.Label(
            outer,
            text=stats,
            font=("Consolas", 13, "bold"),
            bg=self.colors["bg"],
            fg=self.colors["accent"],
            justify="center",
        ).pack(pady=(0, 20))

        buttons = tk.Frame(outer, bg=self.colors["bg"])
        buttons.pack()
        self.button(buttons, "Jogar novamente", self.start_game, width=18).grid(row=0, column=0, padx=8)
        self.button(buttons, "Menu", self.show_start_screen, width=12).grid(row=0, column=1, padx=8)
        self.button(buttons, "Sair", self.root.destroy, width=12).grid(row=0, column=2, padx=8)
