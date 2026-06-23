# Jogar de casas diferentes

Esta versão mantém o modo LAN e adiciona um modo extra para jogar pela internet
usando um túnel TCP legítimo.

A ideia é parecida com "gerar um link", mas para jogo TCP:
o seu computador continua sendo o host, e o túnel cria um endereço público para
o outro jogador entrar.

## Importante

Este projeto não usa phishing, não coleta dados e não cria página falsa.
Ele só abre uma ponte de rede para o jogo.

## Método 1 — Automático com ngrok

No computador que vai hospedar:

```bash
python hospedar_online.py --name Rodrigo
```

O script vai:

1. abrir o jogo como host;
2. iniciar `ngrok tcp 50555`;
3. mostrar um endereço parecido com:

```text
tcp://0.tcp.sa.ngrok.io:12345
```

Envie esse endereço para o amigo.

No computador do amigo:

```bash
python entrar_online.py tcp://0.tcp.sa.ngrok.io:12345 --name Amigo
```

Ou, sem o arquivo helper:

```bash
python main.py --lan-join 0.tcp.sa.ngrok.io --port 12345 --name Amigo
```

## Método 2 — Tailscale

O Tailscale cria uma rede privada entre os computadores.

Host:

```bash
python main.py --lan-host --name Rodrigo
```

Amigo:

```bash
python main.py --lan-join IP_DO_TAILSCALE --name Amigo
```

Exemplo:

```bash
python main.py --lan-join 100.101.102.103 --name Amigo
```

## Método 3 — Redirecionamento de porta no roteador

No computador host:

```bash
python main.py --lan-host --name Rodrigo --port 50555
```

No roteador:

```text
encaminhar TCP 50555 para o IP local do computador host
```

No computador do amigo:

```bash
python main.py --lan-join IP_PUBLICO_DO_HOST --port 50555 --name Amigo
```

Esse método pode falhar se sua operadora usar CGNAT.

## Arquivos novos

```text
hospedar_online.py
entrar_online.py
```

## Solução de problemas

Se não conectar:

1. confira se o host está com o jogo aberto;
2. confira se o endereço e a porta estão corretos;
3. no Windows, permita o Python no firewall;
4. teste primeiro na mesma rede com `--lan-host` e `--lan-join`;
5. se usar ngrok, confirme se o ngrok abriu o túnel TCP.
