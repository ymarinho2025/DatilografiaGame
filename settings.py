# -*- coding: utf-8 -*-
"""
Configurações visuais e gerais do jogo.
"""

APP_TITLE = "Cartas para o Farol"

WINDOW_GEOMETRY = "1240x840"
WINDOW_MIN_SIZE = (1060, 740)

MAX_LIVES = 3
ROULETTE_SIDES = 6

MAX_CHARS_PER_LINE = 55
LINES_PER_BLOCK = 3
BREATH_SECONDS = 3
LINE_READY_SECONDS = 1
BACKGROUND_SUSPENSE_MS = 2600
BOT_COUNT = 2


# Tempo do bloco de 3 linhas.
# Não reinicia a cada linha. Reinicia somente a cada 3 linhas concluídas.
BLOCK_BASE_SECONDS = 11.0
BLOCK_SECONDS_PER_CHAR = 0.17
MIN_BLOCK_SECONDS = 22.0

COLORS = {
    "bg": "#0e1726",
    "night": "#101827",
    "panel": "#182235",
    "panel2": "#22304a",
    "paper": "#fff6df",
    "paper_shadow": "#c6b68a",
    "ink": "#1e2a38",
    "muted": "#aeb9cc",
    "text": "#f7f7fb",
    "accent": "#ffd166",
    "accent2": "#7bdff2",
    "danger": "#ef476f",
    "safe": "#06d6a0",
    "warning": "#f8961e",
    "wood": "#6f432a",
    "wood2": "#8a5a3b",
    "wood_dark": "#3d2417",
    "metal": "#2f3a4a",
    "metal_light": "#4b5d73",
    "key": "#1b2435",
    "key_active": "#ffd166",
    "key_text": "#f5f7fb",
    "self_blue": "#4dabf7",
    "opponent_red": "#ff4d6d",
    "bot_red": "#ff758f",
}

FONTS = {
    "title": ("Segoe UI", 30, "bold"),
    "subtitle": ("Segoe UI", 14),
    "normal": ("Segoe UI", 12),
    "mono": ("Consolas", 12, "bold"),
    "paper": ("Courier New", 13, "bold"),
    "button": ("Segoe UI", 12, "bold"),
}
