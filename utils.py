# -*- coding: utf-8 -*-
"""
Funções utilitárias do jogo.
"""

from __future__ import annotations

import textwrap
import unicodedata

from settings import MAX_CHARS_PER_LINE


def strip_accents(text: str) -> str:
    """Remove acentos para facilitar a digitação."""
    normalized = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def normalize_text(text: str) -> str:
    """
    Normaliza textos longos:
    - remove acentos;
    - deixa minúsculo;
    - converte quebras de linha e múltiplos espaços em espaço simples.
    """
    text = strip_accents(text)
    text = text.lower()
    text = " ".join(text.split())
    return text


def normalize_key(char: str) -> str:
    """Normaliza uma tecla digitada."""
    if not char:
        return ""
    if char == " ":
        return " "
    return normalize_text(char)


def split_text_into_lines(text: str, max_chars: int = MAX_CHARS_PER_LINE) -> list[str]:
    """
    Quebra o parágrafo em linhas de no máximo 55 caracteres.
    Cada linha vira um checkpoint.
    """
    text = normalize_text(text)

    lines = textwrap.wrap(
        text,
        width=max_chars,
        break_long_words=True,
        break_on_hyphens=False,
        replace_whitespace=False,
        drop_whitespace=True,
    )

    return [line[:max_chars] for line in lines if line]


def visible_char(ch: str) -> str:
    """Exibe espaço de forma visível na interface."""
    return "␣" if ch == " " else ch


def named_char(ch: str | None) -> str:
    """Nome amigável para mensagens de erro."""
    if ch is None:
        return "—"
    if ch == " ":
        return "espaço"
    return ch
