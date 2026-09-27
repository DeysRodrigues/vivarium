# 03. Arquitetura

## Camadas

A seta significa "pode importar". Qualquer outra direção é violação.

```
   plugins/  ──────>  api.py
                        │
                        v
   render/  ───────>  core/  <───────  pet/
                        ^                ^
                        └──── app.py ────┘
```

`api.py` é a camada de cima e a única que um plugin importa. A seta de `plugins/`
é de sentido único: o núcleo nunca importa um plugin — `carregador.py` varre a
pasta e importa, e os decoradores de `api` só marcam a função.

| Camada | Conhece | Não conhece |
|--------|---------|-------------|
| `core/` | nada do projeto | domínio e terminal |
| `pet/` | `core/` | terminal |
| `render/` | `core/` | regras de jogo |
| `app.py` | todos | é a única fachada |
| `api.py` | nada do projeto | é a única superfície que um plugin importa |
| `carregador.py` | `api`, `core/`, `pet/` | o que um plugin faz |

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
plugins/                   código da jogadora, recarregado a quente
vivarium/
├── app.py                 Jogo: monta as peças e roda o loop
├── api.py                 superfície pública: cada, quando, acao, log
├── carregador.py          descobre, importa e recarrega os plugins
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
│   ├── gato.py            Gato: posição, pose ativa, tick
│   └── acoes.py           Acao e Acoes: efeito por tecla e espera
└── render/
    ├── paleta.py          nomes de cor
    ├── pixels.py          mapa de pixels -> células (caractere, estilo)
    ├── hud.py             corações e barras
    ├── painel.py          painel de log
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
| `acoes.py` | efeito de cada ação e espera | ler tecla |
| `teclado.py` | entregar a tecla pendente | o que a tecla significa |
| `registro.py` | guardar, disparar e isolar handlers | o que um evento significa |
| `api.py` | marcar funções e receber `log` | registrar, agendar, executar |
| `carregador.py` | ler a pasta e traduzir marcas em inscrições | o que o handler faz |
| `painel.py` | últimas linhas de log | de onde vem a linha |
| `pixels.py` | meio-bloco e cor por célula | regra de jogo |
| `tela.py` | escrever no terminal | montar conteúdo |

## Fluxo de um quadro

```
relogio.tiques()          um tique por quadro, dorme o resto
  jogo.entrada()               tecla pendente -> acao -> efeito no pet
  gato.atualizar()             devolve os eventos do quadro
    vitais.atualizar(pose)     decaimento por segundo, riscos e dano
    ritmos[*].atualizar()      um quadro em cada movimento
    _andar()                   x += velocidade * dt, inverte na borda
  registro.emitir(...)         tique e os eventos devolvidos pelo gato
  registro.vencidos(idade)     agendamentos de @cada que venceram
  carregador.verificar()       mtime, uma vez por segundo
  app.quadro()
    grade.limpar()
    grade.estampar(gato.mapa(), x, y)
    pixels.para_celulas(grade.linhas())
    pixels.sobrepor(emote)
    hud.linhas(vitais) + células + painel.linhas(log)
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
