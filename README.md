# Cartas para o Farol - Versão v4

Jogo visual de datilografia em Python, organizado em módulos.

## Como executar

Entre na pasta do projeto e rode:

```bash
python main.py
```

## Ajustes desta versão

- As fases aparecem em ordem aleatória a cada nova partida.
- Foi adicionada a fase "Noites escuras", com texto em russo transliterado no alfabeto brasileiro.
- Ao avançar para a próxima linha, o jogo dá 1 segundo de preparação.
- Nesse instante, a borda da folha fica amarela.
- Há um som de retorno da máquina de escrever entre linhas.
- O carro/folha da máquina se desloca para a esquerda no retorno.
- Foi adicionado um toque grave e espaçado de suspense ao fundo.
- A interface continua limpa, sem revelar mecanicamente linhas, blocos ou checkpoints.
- Ao errar, a roleta gira uma vez e o tempo reinicia na retomada.

## Estrutura

```text
cartas_para_o_farol_modular_v4/
├── main.py
├── interface.py
├── visual.py
├── frases.py
├── estado_jogo.py
├── vida_roleta.py
├── sons.py
├── settings.py
├── utils.py
└── README.md
```

## Direitos autorais

O projeto não inclui letras completas de músicas protegidas por direitos autorais.  
As fases com nomes de músicas usam textos autorais temáticos.


## Multiplayer LAN

Hospedar:

```bash
python main.py --lan-host --name Rodrigo
```

Entrar:

```bash
python main.py --lan-join IP_DO_HOST --name Amigo
```

Porta padrão:

```text
50555
```

Se quiser outra porta:

```bash
python main.py --lan-host --port 50556 --name Rodrigo
python main.py --lan-join IP_DO_HOST --port 50556 --name Amigo
```

## Jogar online de casas diferentes

Leia o arquivo:

```text
ONLINE.md
```


## Hospedagem online com túnel TCP

Além do modo LAN, esta versão inclui:

```text
hospedar_online.py
entrar_online.py
```

Hospedar para alguém de outra casa:

```bash
python hospedar_online.py --name Rodrigo
```

Entrar pelo endereço gerado:

```bash
python entrar_online.py tcp://HOST:PORTA --name Amigo
```

Mais detalhes em:

```text
ONLINE.md
```


## Barra de progresso com jogadores e bots

A v7 adiciona uma linha de progresso discreta na folha:

- `EU` aparece em azul.
- O adversário LAN/online aparece em vermelho.
- Bots/NPCs aparecem em vermelho claro com marcadores B1, B2 etc.
- Os bots usam estatística fixa:
  - WPM: 25.1
  - CPM: 125.5

Eles não digitam de verdade; apenas simulam corrida para motivar o jogador.


## Ajuste visual da barra de progresso

Nesta versão:
- a linha de progresso saiu da folha;
- ela fica em uma faixa própria, bem visível, abaixo da área de status;
- todos os jogadores e bots ficam alinhados exatamente na mesma linha.


## v9 — Bots em tempo real

Nesta versão:
- os bots avançam na linha de progresso enquanto o tempo passa;
- eles não dependem mais de o usuário digitar para a barra atualizar;
- NPC Yuri usa 25.1 WPM / 125.5 CPM;
- NPC Ana usa metade da velocidade do Yuri: 12.55 WPM / 62.75 CPM.
