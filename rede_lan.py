# -*- coding: utf-8 -*-
"""
rede_lan.py

Conexão simples jogador x jogador via LAN usando TCP.

Uso técnico:
- Um jogador hospeda:
    python main.py --lan-host --name Rodrigo

- Outro jogador entra usando o IP local do host:
    python main.py --lan-join 192.168.0.10 --name Amigo

Porta padrão:
    50555

Protocolo:
- JSON por linha.
- Cada mensagem possui:
    {
        "type": "snapshot",
        "name": "Jogador",
        "payload": {...}
    }

Segurança:
- Use apenas com pessoas conhecidas.
- Em rede local, libere a porta no firewall do Windows se necessário.
"""

from __future__ import annotations

import json
import socket
import threading
import time
from dataclasses import dataclass
from typing import Callable, Optional


MessageCallback = Callable[[dict], None]
StatusCallback = Callable[[str], None]


@dataclass
class LanStatus:
    connected: bool = False
    role: str = "solo"
    peer_address: str = ""


class LanPeer:
    def __init__(self, root, player_name: str = "Jogador", port: int = 50555):
        self.root = root
        self.player_name = player_name or "Jogador"
        self.port = int(port)

        self.status = LanStatus()
        self._server_socket: Optional[socket.socket] = None
        self._socket: Optional[socket.socket] = None
        self._file = None

        self._on_message: Optional[MessageCallback] = None
        self._on_status: Optional[StatusCallback] = None

        self._closed = False
        self._lock = threading.Lock()

    # ------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------

    def set_handlers(self, on_message: MessageCallback, on_status: StatusCallback) -> None:
        self._on_message = on_message
        self._on_status = on_status

    def _emit_status(self, text: str) -> None:
        if self._on_status is not None:
            self.root.after(0, lambda: self._on_status(text))

    def _emit_message(self, msg: dict) -> None:
        if self._on_message is not None:
            self.root.after(0, lambda: self._on_message(msg))

    # ------------------------------------------------------------
    # LAN
    # ------------------------------------------------------------

    def start_host(self) -> None:
        self.status.role = "host"
        thread = threading.Thread(target=self._host_worker, daemon=True)
        thread.start()

    def _host_worker(self) -> None:
        try:
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server_socket.bind(("0.0.0.0", self.port))
            self._server_socket.listen(1)

            local_ip = get_local_ip()
            self._emit_status(f"Hospedando em {local_ip}:{self.port}. Aguardando jogador...")

            conn, addr = self._server_socket.accept()
            self._attach_socket(conn, f"{addr[0]}:{addr[1]}")
            self.send("hello", {"message": "conectado", "port": self.port})
        except OSError as exc:
            self._emit_status(f"Erro ao hospedar LAN: {exc}")

    def join(self, host_ip: str) -> None:
        self.status.role = "client"
        thread = threading.Thread(target=self._join_worker, args=(host_ip,), daemon=True)
        thread.start()

    def _join_worker(self, host_ip: str) -> None:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(8)
            self._emit_status(f"Conectando em {host_ip}:{self.port}...")
            sock.connect((host_ip, self.port))
            sock.settimeout(None)
            self._attach_socket(sock, f"{host_ip}:{self.port}")
            self.send("hello", {"message": "entrei", "port": self.port})
        except OSError as exc:
            self._emit_status(f"Erro ao conectar: {exc}")

    def _attach_socket(self, sock: socket.socket, peer_address: str) -> None:
        with self._lock:
            self._socket = sock
            self._file = sock.makefile("r", encoding="utf-8", newline="\n")
            self.status.connected = True
            self.status.peer_address = peer_address

        self._emit_status(f"Conectado com {peer_address}.")
        thread = threading.Thread(target=self._reader_worker, daemon=True)
        thread.start()

    def _reader_worker(self) -> None:
        try:
            while not self._closed and self._file is not None:
                line = self._file.readline()
                if not line:
                    break

                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    continue

                self._emit_message(msg)
        except OSError:
            pass
        finally:
            self.status.connected = False
            self._emit_status("Conexão LAN encerrada.")

    # ------------------------------------------------------------
    # Envio
    # ------------------------------------------------------------

    def send(self, msg_type: str, payload: dict | None = None) -> None:
        if payload is None:
            payload = {}

        msg = {
            "type": msg_type,
            "name": self.player_name,
            "time": time.time(),
            "payload": payload,
        }

        data = (json.dumps(msg, ensure_ascii=False) + "\n").encode("utf-8")

        with self._lock:
            sock = self._socket

        if sock is None:
            return

        try:
            sock.sendall(data)
        except OSError:
            self.status.connected = False
            self._emit_status("Falha ao enviar dados pela LAN.")

    def close(self) -> None:
        self._closed = True

        with self._lock:
            sock = self._socket
            server = self._server_socket
            self._socket = None
            self._server_socket = None

        for obj in (sock, server):
            if obj is not None:
                try:
                    obj.close()
                except OSError:
                    pass


def get_local_ip() -> str:
    """
    Tenta descobrir o IP local real da máquina.
    Se falhar, usa 127.0.0.1.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        return ip
    except OSError:
        return "127.0.0.1"
