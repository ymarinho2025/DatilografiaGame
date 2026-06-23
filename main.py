# -*- coding: utf-8 -*-
"""
Arquivo principal para iniciar o jogo.

Modo solo:
    python main.py

Hospedar na LAN:
    python main.py --lan-host --name Rodrigo

Entrar na partida LAN:
    python main.py --lan-join 192.168.0.10 --name Amigo

Escolher porta:
    python main.py --lan-host --port 50555
    python main.py --lan-join 192.168.0.10 --port 50555
"""

from __future__ import annotations

import argparse
import socket
import tkinter as tk

from interface import TypewriterGameApp
from rede_lan import LanPeer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Cartas para o Farol")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--lan-host", action="store_true", help="Hospeda uma partida na rede local.")
    group.add_argument("--lan-join", metavar="IP", help="Entra em uma partida LAN pelo IP do host.")
    parser.add_argument("--port", type=int, default=50555, help="Porta TCP da partida LAN.")
    parser.add_argument("--name", default=socket.gethostname(), help="Nome do jogador.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    root = tk.Tk()

    network = None
    if args.lan_host or args.lan_join:
        network = LanPeer(root, player_name=args.name, port=args.port)

    app = TypewriterGameApp(root, network=network, player_name=args.name)

    if network is not None:
        network.set_handlers(app.on_network_message, app.on_network_status)

        if args.lan_host:
            network.start_host()
        elif args.lan_join:
            network.join(args.lan_join)

        root.protocol("WM_DELETE_WINDOW", lambda: (network.close(), root.destroy()))
    else:
        root.protocol("WM_DELETE_WINDOW", root.destroy)

    root.mainloop()


if __name__ == "__main__":
    main()
