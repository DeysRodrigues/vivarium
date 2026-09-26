<div align="center">

```
  ██  ██    ██
  ██▀█▀██   ██
  ██▄█▄██  ██
   ▄███▄▄▄▄█
   ████████
   ████████
   ██    ██
```

# Vivarium

**Um bichinho virtual de terminal, em pixel art de meio-bloco.**

[![Python](https://img.shields.io/badge/python-3.14-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Rich](https://img.shields.io/badge/rich-15.0-0f766e)](https://github.com/Textualize/rich)
[![Licença](https://img.shields.io/badge/licen%C3%A7a-MIT-blue)](#licença)
[![Estado](https://img.shields.io/badge/estado-em%20desenvolvimento-f59e0b)](doc/06-roadmap.md)
[![Dependências](https://img.shields.io/badge/depend%C3%AAncias-1-22c55e)](doc/02-tecnologias.md)
[![CPU](https://img.shields.io/badge/CPU-0.73%25%20do%20quadro-22c55e)](doc/01-requisitos.md)

[Documentação](doc/README.md) ·
[Arquitetura](doc/03-arquitetura.md) ·
[Simulação](doc/04-simulacao.md) ·
[Roadmap](doc/06-roadmap.md)

</div>

---

## O que é

Um bicho que vive no seu terminal. Ele respira, pisca, mexe as orelhas, anda de
um lado para o outro, deita para dormir, tem fome e fica entediado. Ninguém
comanda nada disso: cada movimento tem relógio próprio e o comportamento emerge
do custo de cada pose.

O desenho é um mapa de pixels renderizado em meio-blocos Unicode, o que dobra a
resolução vertical e permite duas cores por célula de terminal.

## Instalação

```bash
git clone <url> vivarium
cd vivarium
sudo pacman -S --needed python-rich      # ou: pip install rich
python run.py                            # Ctrl+C para sair
```

Requer Python 3.10 ou superior e um terminal com suporte a Unicode.

## Uso

```python
from vivarium.app import Jogo

Jogo(fps=5).rodar()                      # padrão
Jogo(fps=20).rodar()                     # mais suave, mesma velocidade
Jogo(fps=5, largura=80).rodar()          # mundo mais largo
Jogo(fps=5, depuracao=False).rodar()     # sem a linha de instrumentação
```

A duração de toda animação é declarada em segundos e convertida para quadros
pelo relógio. Trocar o fps altera a suavidade, não a velocidade.

## Como funciona

```
┌──────────────┐
│   Relogio    │  tempo real -> ticks de passo fixo, um tick por quadro
└──────┬───────┘
       │
┌──────▼───────┐
│     Gato     │  vitais decaem, ritmos avançam, pose ativa define o custo
└──────┬───────┘
       │ mapa de pixels
┌──────▼───────┐
│    Grade     │  buffer do mundo
└──────┬───────┘
       │
┌──────▼───────┐
│    Render    │  meio-bloco, duas cores por célula, HUD por cima
└──────┬───────┘
       │
┌──────▼───────┐
│     Tela     │  rich.live.Live, descarta quadro idêntico
└──────────────┘
```

Três decisões sustentam o resto:

**Animação em quadros, simulação em segundos.** Animação é discreta e conta
inteiros, sem acúmulo de erro. Vitais e deslocamento são contínuos e usam
`relogio.dt`, o que mantém a simulação independente do fps.

**Movimento é dado, não código.** Um ritmo é um ciclo de `(valor, duração)`,
com duração fixa ou sorteada em faixa. Respirar, piscar, mexer a orelha e
balançar o rabo usam o mesmo mecanismo.

```python
RESPIRAR = [(0, 1.4), (-1, 0.2), (-2, 0.8), (-1, 0.4)]
PISCAR   = [(OLHO_ABERTO, (1.5, 5.0)), (OLHO_MEIO, 0.2), (OLHO_FECHADO, 0.2)]
```

**Dano por extremo sustentado.** Nenhum stat reduz vida diretamente. Um risco
é uma condição que, mantida além de uma carência, aplica dano contínuo, o que
garante janela de recuperação.

## Desempenho

Medido com orçamento de 200.000 µs por quadro a 5 fps.

| Métrica | Valor |
|---------|-------|
| CPU por quadro | 1457 µs (0,73%) |
| Tráfego ao terminal | 7,8 KB/s |
| Estado residente | 1,8 KB |
| Startup | ~165 ms |
| Render de terminal cheio (120x30) | 806 µs (0,40%) |

A tela só é escrita quando o quadro muda. Em repouso o processo dorme.

## Estrutura

```
vivarium/
├── core/        tempo, ritmo, grade, stat. Sem domínio.
├── pet/         arte, poses, vitais, estado. Sem terminal.
└── render/      meio-bloco, paleta, HUD, saída.
```

A regra de dependência é verificável:

```bash
grep -rn "vivarium.render" vivarium/core vivarium/pet    # vazio
```

## Estado

Implementado: loop de passo fixo, sistema de animação, três poses, deslocamento
com espelhamento, vitais com dano por risco, HUD e render colorido.

Próximo: entrada de teclado, ações do jogador, partículas, personalidade e
cérebro por utilidade, plugins com recarga a quente.

Detalhes em [doc/06-roadmap.md](doc/06-roadmap.md).

## Documentação

| Doc | Conteúdo |
|-----|----------|
| [01. Requisitos](doc/01-requisitos.md) | Escopo e requisitos não funcionais medidos |
| [02. Stack](doc/02-tecnologias.md) | Dependências e alternativas descartadas |
| [03. Arquitetura](doc/03-arquitetura.md) | Camadas, módulos, fluxo de um quadro |
| [04. Simulação](doc/04-simulacao.md) | Tempo, ritmos, poses, vitais, dano |
| [05. API de plugin](doc/05-api-de-plugin.md) | Contrato de extensão (projetado) |
| [06. Roadmap](doc/06-roadmap.md) | Estado e fases seguintes |
| [07. Testes](doc/07-testes.md) | Estratégia e pontos de injeção |

## Licença

MIT.
