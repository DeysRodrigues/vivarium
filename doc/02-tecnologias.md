# 02. Stack

## Runtime

| Tecnologia | Uso | Motivo |
|-----------|-----|--------|
| Python 3.14 | tudo | stdlib suficiente para o domínio |
| [Rich](https://github.com/Textualize/rich) | `render/tela.py` | região viva no terminal com atualização parcial e estilo por span |
| `dataclasses` | `Stat`, `Pose` | semântica de valor, `slots`, `frozen`, `__repr__` |
| `time.monotonic` | `core/relogio.py` | monotônico, imune a ajuste de relógio do sistema |
| `random` | ritmos e escolha de pose | jitter de intervalo e sorteio de pose |

Previsto para fases seguintes: `importlib` e `os.stat` para recarga de
plugins, `json` e `pathlib` para persistência.

## Dependência única

Rich substituiu um renderizador próprio baseado em sequências ANSI. Sem ela,
uma célula não consegue carregar duas cores, o que impede desenhar corpo e
detalhe no mesmo meio-bloco.

Custo medido, com orçamento de 200.000 µs por quadro a 5 fps:

```
renderizador anterior, sem cor      75 µs    0,04%
Rich, com cor                     1457 µs    0,73%
bytes por quadro                  1595       4,1x o anterior
startup                           +97 ms     uma vez
```

`Live` é usado com `auto_refresh=False`. O ritmo é do `Relogio`; deixar o Rich
atualizar por conta própria criaria dois relógios concorrentes.

## Alternativas descartadas

| Alternativa | Motivo |
|------------|--------|
| `curses` | resolve entrada e tela, mas não dá duas cores por célula sem gerenciamento manual de pares |
| Textual | framework de widget e layout. O projeto precisa de canvas livre e loop próprio |
| asciimatics | cobre sprites e animação, mas substituiria o núcleo do projeto |
| blessed | encapsula terminal sem resolver o problema de cor por meia célula |
| pygame, pyglet, arcade | render gráfico. Descaracteriza o alvo de terminal |
| numpy | grade de 256 a 7200 pixels. Custo medido já é desprezível |
| watchdog | recarga por `os.stat` sobre uma dezena de arquivos é mais barata que a dependência |
| pickle | quebra em renomeação de classe. Save deve ser inspecionável |

## Entrada de teclado

Pendente. Rich não lê teclado. As opções são `termios`/`tty` em modo raw sobre
`stdin` não bloqueante, ou `curses` restrito à camada de entrada. Bloqueia as
ações do jogador.

## Caracteres

O render usa `▀` e `▄`. Um `▀` pinta a metade superior com a cor de frente e a
inferior com a de fundo, o que dá duas cores por célula e dobra a resolução
vertical efetiva.

Emoji não é suportado: a maioria ocupa duas colunas e desalinha a grade.
