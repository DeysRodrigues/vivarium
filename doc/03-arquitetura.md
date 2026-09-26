# 03. Arquitetura

## Camadas

A seta significa "pode importar". Qualquer outra direção é violação.

```
   render/  ───────>  core/  <───────  pet/
                        ^                ^
                        └──── app.py ────┘
```

| Camada | Conhece | Não conhece |
|--------|---------|-------------|
| `core/` | nada do projeto | domínio e terminal |
| `pet/` | `core/` | terminal |
| `render/` | `core/` | regras de jogo |
| `app.py` | todos | é a única fachada |

### Verificação

```bash
grep -rn "vivarium.render" vivarium/core vivarium/pet   # deve retornar vazio
grep -rn "vivarium.pet"    vivarium/core vivarium/render # deve retornar vazio
```

O `Gato` devolve mapa de pixels, nunca linhas de terminal. É o que permite
simular o bicho inteiro em teste sem terminal alocado.

## Módulos

```
run.py                     ponto de entrada
vivarium/
├── app.py                 Jogo: monta as peças e roda o loop
├── core/
│   ├── relogio.py         Relogio: tempo real -> ticks de passo fixo
│   ├── ritmo.py           Ritmo: ciclo de (valor, duração) com relógio próprio
│   ├── grade.py           Grade: buffer de pixels do mundo
│   ├── mapa.py            carregar(): parse e validação de mapa de pixels
│   └── stat.py            Stat: número com limites
├── pet/
│   ├── arte.py            mapa do gato e anatomia derivada dele
│   ├── poses.py           Pose e os ciclos de cada movimento
│   ├── corpo.py           compor(): pose + movimentos -> mapa de pixels
│   ├── vitais.py          Vitais e Risco: decaimento e dano
│   └── gato.py            Gato: posição, pose ativa, tick
└── render/
    ├── paleta.py          nomes de cor
    ├── pixels.py          mapa de pixels -> células (caractere, estilo)
    ├── hud.py             corações e barras
    └── tela.py            Tela: região viva via rich.live.Live
```

### Responsabilidade

| Módulo | Responsável por | Não responsável por |
|--------|-----------------|---------------------|
| `relogio.py` | converter tempo real em ticks | saber o que é um tick |
| `ritmo.py` | quando um valor muda | qual é o valor |
| `grade.py` | guardar e estampar pixels | desenhar |
| `stat.py` | limites e clamp | significado do número |
| `poses.py` | dados de pose e ciclos | executar |
| `corpo.py` | compor o mapa do quadro | quando compor |
| `vitais.py` | decaimento e dano | apresentação |
| `gato.py` | estado e escolha de pose | render |
| `pixels.py` | meio-bloco e cor por célula | regra de jogo |
| `tela.py` | escrever no terminal | montar conteúdo |

## Fluxo de um quadro

```
relogio.tiques()          um tique por quadro, dorme o resto
  gato.atualizar()
    vitais.atualizar(pose)     decaimento por segundo, riscos e dano
    ritmos[*].atualizar()      um quadro em cada movimento
    _andar()                   x += velocidade * dt, inverte na borda
  app.quadro()
    grade.limpar()
    grade.estampar(gato.mapa(), x, y)
    pixels.para_celulas(grade.linhas())
    pixels.sobrepor(emote)
    hud.linhas(vitais) + células
  tela.mostrar(células, rodapé)   descarta se idêntico ao anterior
```

Ordem de desenho define profundidade: grade, emote, HUD. O HUD é informação e
não pode ser coberto pelo bicho.

## Injeção de dependência

`Relogio` recebe `agora` e `dormir`; `Gato` e `Ritmo` recebem o `Relogio`.
Não há singleton nem estado global mutável. Consequências:

* `Jogo(fps=20)` e `Jogo(fps=5)` coexistem no mesmo processo.
* Um relógio falso simula minutos de jogo em milissegundos.
* Em Python o módulo já é singleton: `arte.MAPA` é carregado uma vez e
  compartilhado por todos os quadros (flyweight).

## Padrões

| Padrão | Aplicação |
|--------|-----------|
| Facade | `Jogo` |
| Strategy | `Ritmo` parametrizado por ciclo |
| Composite | `compor()` sobrepõe camadas independentes |
| Flyweight | `arte.MAPA` imutável compartilhado |
| Data class como valor | `Pose`, `Stat`, `Risco` |
