# -*- coding: utf-8 -*-
"""
hospedar_online.py

Hospeda o jogo para alguém entrar de outra casa usando túnel TCP legítimo.

Este arquivo NÃO usa phishing e NÃO coleta dados.
Ele apenas:
1. abre o jogo como servidor local;
2. executa `ngrok tcp PORTA`;
3. lê o endereço público gerado pelo ngrok;
4. mostra o comando que seu amigo deve rodar.

Requisitos:
- Ter o ngrok instalado no computador que vai hospedar.
- Ter uma conta/authtoken do ngrok configurada, se o ngrok pedir.
- O amigo precisa ter este mesmo projeto baixado.

Uso:
    python hospedar_online.py --name Rodrigo

Com porta personalizada:
    python hospedar_online.py --name Rodrigo --port 50555

O amigo vai entrar com algo assim:
    python entrar_online.py tcp://0.tcp.sa.ngrok.io:12345 --name Amigo
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlparse


DEFAULT_PORT = 50555


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Hospedar Cartas para o Farol online com túnel TCP.")
    parser.add_argument("--name", default="Host", help="Nome do jogador que vai hospedar.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Porta local do jogo.")
    parser.add_argument(
        "--ngrok-path",
        default="ngrok",
        help="Caminho do executável ngrok. Padrão: ngrok no PATH.",
    )
    return parser.parse_args()


def check_ngrok(ngrok_path: str) -> None:
    if Path(ngrok_path).exists():
        return
    if shutil.which(ngrok_path):
        return

    print("\nERRO: ngrok não encontrado.")
    print("Instale o ngrok e deixe o executável no PATH, ou use --ngrok-path.")
    print("\nExemplo:")
    print("python hospedar_online.py --ngrok-path C:\\\\ngrok\\\\ngrok.exe --name Rodrigo")
    raise SystemExit(1)


def start_ngrok(ngrok_path: str, port: int) -> subprocess.Popen:
    print(f"Iniciando túnel TCP: ngrok tcp {port}")
    return subprocess.Popen(
        [ngrok_path, "tcp", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        text=True,
    )


def get_ngrok_tcp_url(timeout: int = 25) -> str:
    """
    Lê a API local do ngrok:
    http://127.0.0.1:4040/api/tunnels

    Retorna algo como:
    tcp://0.tcp.sa.ngrok.io:12345
    """
    api_url = "http://127.0.0.1:4040/api/tunnels"
    started = time.time()

    while time.time() - started < timeout:
        try:
            with urllib.request.urlopen(api_url, timeout=2) as response:
                data = json.loads(response.read().decode("utf-8"))

            for tunnel in data.get("tunnels", []):
                public_url = tunnel.get("public_url", "")
                if public_url.startswith("tcp://"):
                    return public_url
        except Exception:
            pass

        time.sleep(1)

    raise RuntimeError("Não consegui ler o endereço TCP do ngrok.")


def parse_tcp_url(tcp_url: str) -> tuple[str, int]:
    parsed = urlparse(tcp_url)
    if parsed.scheme != "tcp" or not parsed.hostname or not parsed.port:
        raise ValueError(f"Endereço TCP inválido: {tcp_url}")
    return parsed.hostname, int(parsed.port)


def start_game_host(name: str, port: int) -> subprocess.Popen:
    main_py = Path(__file__).with_name("main.py")
    return subprocess.Popen(
        [
            sys.executable,
            str(main_py),
            "--lan-host",
            "--name",
            name,
            "--port",
            str(port),
        ]
    )


def main() -> None:
    args = parse_args()
    check_ngrok(args.ngrok_path)

    ngrok_proc = None
    game_proc = None

    try:
        game_proc = start_game_host(args.name, args.port)
        time.sleep(1)

        ngrok_proc = start_ngrok(args.ngrok_path, args.port)
        tcp_url = get_ngrok_tcp_url()
        remote_host, remote_port = parse_tcp_url(tcp_url)

        print("\n" + "=" * 72)
        print("PARTIDA ONLINE CRIADA")
        print("=" * 72)
        print(f"Endereço público: {tcp_url}")
        print("\nEnvie para seu amigo este comando:")
        print(f"python entrar_online.py {tcp_url} --name Amigo")
        print("\nOu este comando direto:")
        print(f"python main.py --lan-join {remote_host} --port {remote_port} --name Amigo")
        print("=" * 72)
        print("\nMantenha esta janela aberta enquanto vocês jogam.")
        print("Para encerrar, feche o jogo e pressione Ctrl+C aqui.")

        while True:
            if game_proc.poll() is not None:
                print("O jogo foi fechado. Encerrando túnel.")
                break
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nEncerrando...")
    except Exception as exc:
        print(f"\nERRO: {exc}")
        print("\nVerifique se:")
        print("- o ngrok está instalado;")
        print("- o authtoken do ngrok está configurado;")
        print("- a porta escolhida não está bloqueada;")
        print("- o jogo abriu como host.")
    finally:
        if ngrok_proc is not None and ngrok_proc.poll() is None:
            ngrok_proc.terminate()
        if game_proc is not None and game_proc.poll() is None:
            game_proc.terminate()


if __name__ == "__main__":
    main()
