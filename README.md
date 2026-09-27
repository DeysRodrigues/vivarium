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

**Um bicho de terminal com vida própria, que você cuida escrevendo código.**

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

A outra metade é que **você programa o cuidado dele**. A rotina do bicho é código
seu, em arquivos soltos numa pasta, aplicados ao bicho vivo sem reiniciar:

```python
# plugins/minha_rotina.py
from vivarium.api import cada, quando, log

@cada(horas=4)
def cafe(pet):
    pet.alimentar(30)
    log("servi o café")

@quando("fome_vazia")
def emergencia(pet):
    pet.alimentar(50)
```

Ele vive enquanto o terminal está aberto.

> A persistência ainda não existe: hoje a idade zera ao fechar o terminal, então
> use `@cada(minutos=...)` para ver algo acontecer. É a próxima fase
> ([08](doc/08-persistencia.md)).

O desenho é um mapa de pixels renderizado em meio-blocos Unicode, o que dobra a
resolução vertical e permite duas cores por célula de terminal.

## Para que serve

Dois objetivos, e eles decidem empates de projeto:

1. **Um bicho divertido com vida própria** — interessante de olhar mesmo sem
   nenhum plugin escrito.
2. **Um lugar para treinar Python sempre** — sessões curtas, código de verdade,
   sem montar projeto novo. Por isso errar é barato: exceção de plugin vira
   traceback no painel de log e o bicho continua vivo.

## Rodar

```bash
git clone <url> vivarium
cd vivarium
sudo pacman -S --needed python-rich      # ou: pip install rich
python run.py                            # Ctrl+C para sair
```

Requer Python 3.10 ou superior e um terminal com suporte a Unicode.

## Escrever um plugin

Crie qualquer `.py` na pasta `plugins/`. Salvar o arquivo aplica o efeito ao bicho
que está na tela — sem reiniciar, sem perder o estado.

```python
# plugins/meu_primeiro.py
from vivarium.api import cada, quando, acao, log


@cada(segundos=20, agora=True)          # agora=True: dispara já, pra você ver
def vigiar(pet):
    log(f"fome {pet.fome:.0f}, tédio {pet.tedio:.0f}, idade {pet.idade:.0f}s")


@quando("fome_vazia")                   # transição: dispara uma vez
def emergencia(pet):
    pet.alimentar(50)
    log("! corri com a ração")


@acao("banho", tecla="h", rotulo="banho", espera=45.0, emote="~~")
def banho(pet):
    pet.tedio -= 30                     # a tecla h aparece no rodapé
```

O que você pode chamar:

| No `pet` | |
|---|---|
| `.alimentar(quanto=30)`, `.acariciar()`, `.brincar()` | as ações |
| `.fome`, `.tedio`, `.vida` | leitura e escrita, com limites aplicados |
| `.idade`, `.especie`, `.pose`, `.x` | estado |
| `.reagir(emote, segundos=1.6)` | emote temporário sobre a cabeça |

| Decorador | Quando roda |
|---|---|
| `@cada(horas=, minutos=, segundos=, agora=False)` | a cada tanto de **idade do bicho** |
| `@quando(evento, se=None)` | `tique`, `fome_vazia`, `tedio_cheio`, `dormiu`, `acordou`, `morreu` |
| `@acao(nome, tecla=, rotulo=, espera=, emote=)` | quando você aperta a tecla |

`log("! algo")` sai em vermelho no painel.

**Quando você erra**, o bicho não morre junto: o erro aparece resumido e aquele
handler fica desativado até você salvar o arquivo de novo.

```
! meu_primeiro.py.vigiar: meu_primeiro.py:7 AttributeError: 'Gato' object has no attribute 'fomee'
! desativado até você salvar o arquivo
```

Só `vivarium.api` é público — `core/`, `pet/` e `render/` são internos. Se um
plugin precisa alcançar um deles, é lacuna na API. Contrato completo em
[doc/05](doc/05-api-de-plugin.md); `plugins/exemplo.py` está no repositório.

A pasta é `./plugins` quando existe, senão `$XDG_CONFIG_HOME/vivarium/plugins`.

## Ações

Definidas uma vez e alcançáveis por dois caminhos: `pet.alimentar()` no seu
plugin, e a tecla na mão enquanto você olha. O teclado é atalho, não a interface
principal.

| Tecla | Ação | Efeito | Espera |
|-------|------|--------|--------|
| `a` | alimentar | fome +30 | 8 s |
| `c` | carinho | tédio −8, vida +10 | 3 s |
| `b` | brincar | tédio −25, fome −6 | 12 s |
| `ctrl+c` | sair | | |

A espera existe para que a ação não anule o modelo de vitais: sem ela, segurar
a tecla mantém qualquer stat no máximo e o sistema de risco nunca dispara. Ação
em espera aparece no rodapé com parêntese em vez de colchete. Carinho é o único
ponto que recupera vida.

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

Implementado: loop de passo fixo, animação por ritmos, três poses, deslocamento
com espelhamento, vitais com dano por risco, HUD, render colorido, teclado, as
três ações, e a **API de plugin com recarga a quente** — registro que isola
exceção, agendamento por idade, eventos e painel de log.

Falta:

| Fase | O que destrava |
|------|----------------|
| 1. Persistência | a idade acumular entre sessões; hoje zera ao fechar |
| 3. Painel de abertura | ver o que você já escreveu, ao abrir |
| 4. Console na tecla `:` | avaliar Python no bicho vivo |
| 5. Balanceamento e morte | dois furos conhecidos, medidos |
| 6-9 | cérebro por utilidade, partículas, segunda espécie, clima |

Sem persistência, fechar o terminal reinicia o bicho — e `@cada(horas=4)` não
chega perto de disparar. Use minutos ou segundos por enquanto.

Detalhes e critério de pronto de cada fase em
[doc/06-roadmap.md](doc/06-roadmap.md).

## Documentação

| Doc | Conteúdo |
|-----|----------|
| [01. Requisitos](doc/01-requisitos.md) | Escopo e requisitos não funcionais medidos |
| [02. Stack](doc/02-tecnologias.md) | Dependências e alternativas descartadas |
| [03. Arquitetura](doc/03-arquitetura.md) | Camadas, módulos, fluxo de um quadro |
| [04. Simulação](doc/04-simulacao.md) | Tempo, ritmos, poses, vitais, dano |
| [05. API de plugin](doc/05-api-de-plugin.md) | A superfície onde você escreve código |
| [06. Roadmap](doc/06-roadmap.md) | Estado e fases seguintes |
| [07. Testes](doc/07-testes.md) | Estratégia e pontos de injeção |
| [08. Persistência](doc/08-persistencia.md) | Save, os três relógios e a ausência (projetado) |
| [Ideias](doc/ideias.md) | Backlog de intenção: o que ainda não é fase |

## Licença

MIT.
