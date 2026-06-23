# -*- coding: utf-8 -*-
"""
entrar_online.py

Entra em uma partida online criada com `hospedar_online.py`.

Uso:
    python entrar_online.py tcp://0.tcp.sa.ngrok.io:12345 --name Amigo

Também aceita endereço sem tcp://:
    python entrar_online.py 0.tcp.sa.ngrok.io:12345 --name Amigo
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Entrar em partida online de Cartas para o Farol.")
    parser.add_argument("address", help="Endereço tcp://host:porta ou host:porta.")
    parser.add_argument("--name", default="Amigo", help="Nome do jogador.")
    return parser.parse_args()


def parse_address(address: str) -> tuple[str, int]:
    if "://" not in address:
        address = "tcp://" + address

    parsed = urlparse(address)
    if parsed.scheme != "tcp" or not parsed.hostname or not parsed.port:
        raise ValueError("Use um endereço no formato tcp://host:porta")

    return parsed.hostname, int(parsed.port)


def main() -> None:
    args = parse_args()
    host, port = parse_address(args.address)

    main_py = Path(__file__).with_name("main.py")
    subprocess.call(
        [
            sys.executable,
            str(main_py),
            "--lan-join",
            host,
            "--port",
            str(port),
            "--name",
            args.name,
        ]
    )


if __name__ == "__main__":
    main()
