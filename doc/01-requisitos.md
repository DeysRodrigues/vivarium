# 01. Requisitos

## Escopo

Simulador de bichinho virtual para terminal. O bicho tem vitais que decaem,
escolhe o próprio comportamento e é renderizado como pixel art em meio-blocos
Unicode. O objetivo de longo prazo é expor uma API de extensão que permita
adicionar ações, clima e comportamentos com recarga a quente, sem reiniciar o
processo.

## Requisitos funcionais

### Bicho

| Item | Especificação |
|------|---------------|
| Vida | 7 corações. Internamente `0..700` para permitir meio coração em inteiro |
| Fome | `0..100`. Cheia significa alimentado, vazia significa faminto |
| Tédio | `0..100`. Cheio significa entediado |
| Poses | `em pé`, `andando`, `deitado`. Cada uma define custo de vitais e conjunto de ritmos |
| Espécies | Gato implementado. Planta prevista, com vitais próprios (`agua`, `luz`) |
| Personalidade | Previsto: vetor de traços contínuos, não enumeração |

### Simulação

* Loop de passo fixo, um tick por quadro, taxa configurável por instância.
* Animação composta por ritmos independentes, cada um com relógio próprio e
  intervalos não harmônicos entre si.
* Vitais decaem em função da pose ativa.
* Dano por extremo sustentado com carência, nunca por transição instantânea.

### Renderização

* Grade de pixels convertida em células de terminal a dois pixels por célula.
* Duas cores por célula via caractere de meio-bloco (frente e fundo).
* HUD com corações e barras coloridas por faixa.
* Escrita no terminal apenas quando o quadro muda.

### Extensibilidade (previsto)

* Diretório `plugins/` com recarga por `mtime`.
* Registro por decorador, isolamento de exceção por handler.
* Console embutido para avaliação de expressões no mundo em execução.

## Requisitos não funcionais

| Requisito | Alvo | Medido |
|-----------|------|--------|
| Custo de CPU por quadro | < 5% do orçamento | 0,73% a 5 fps |
| Tráfego para o terminal | irrelevante | 7,8 KB/s a 5 fps |
| Memória residente do estado | < 100 KB | 1,8 KB |
| Startup | < 500 ms | ~165 ms |
| Dependências de runtime | mínimas | 1 (Rich) |

O processo dorme entre quadros. Em repouso o uso de CPU é indistinguível de
zero.

## Fora de escopo

Rede e multiplayer, áudio, janela gráfica no compositor, reprodução, múltiplos
bichos simultâneos, economia de itens.
