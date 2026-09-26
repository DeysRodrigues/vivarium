# 04. Modelo de simulação

## Tempo

Duas unidades, deliberadamente distintas:

| Unidade | Uso | Tipo |
|---------|-----|------|
| quadro | animação | inteiro |
| segundo | vitais e deslocamento | float, via `relogio.dt` |

Animação é discreta: contar quadros em inteiro é exato e não acumula erro de
ponto flutuante. Vitais e velocidade são contínuos e se medem em segundos, o
que mantém a velocidade da simulação independente do fps.

`Relogio.quadros(segundos)` é o único ponto de conversão. Ele aplica
`max(1, round(...))`, garantindo que nenhuma duração caia entre dois quadros.
Trocar o fps preserva a duração real de toda animação.

```
Relogio(fps=5).quadros(1.4)   ==  7
Relogio(fps=20).quadros(1.4)  == 28
```

O gerador `tiques()` emite um tique por quadro e dorme o resto. Se um quadro
atrasar (terminal lento, processo suspenso), a âncora é recolocada no instante
atual em vez de recuperar o acúmulo, evitando avanço em bloco.

## Ritmo

Um movimento é um ciclo de `(valor, duração)`. A duração pode ser um número
fixo ou uma faixa `(min, max)` sorteada a cada repetição.

```python
RESPIRAR = [(0, 1.4), (-1, 0.2), (-2, 0.8), (-1, 0.4)]
PISCAR   = [(OLHO_ABERTO, (1.5, 5.0)), (OLHO_MEIO, 0.2), (OLHO_FECHADO, 0.2)]
```

A faixa é o que separa comportamento vivo de metrônomo. Movimento contínuo
(respirar) e movimento esporádico (piscar) são o mesmo mecanismo: no segundo
caso, o estado de repouso é um passo do ciclo com duração sorteada.

Os intervalos de repouso dos ritmos não são múltiplos entre si. Valores
harmônicos entrariam em fase e produziriam padrão perceptível.

O ciclo é convertido para quadros uma única vez, na construção, usando o
relógio recebido.

## Meio-bloco e paridade

Uma célula de terminal é aproximadamente duas vezes mais alta que larga e
guarda dois pixels verticais. Consequências:

1. O mapa precisa ter número par de linhas.
2. Detalhes devem começar em linha par e ter altura par. Um detalhe em linha
   ímpar é partido entre duas células e perde definição.
3. Deslocamento vertical de 1 pixel equivale a meia célula. O quadro resultante
   fica com todo contorno sobre a divisa das células.

O item 3 é usado de propósito: no ciclo de respiração, `-1` não é pose de
repouso e sim quadro de passagem (in-between). As posições em que o corpo para
(`0` e `-2`) são deslocamentos pares e permanecem nítidas.

## Poses

`Pose` é um dado imutável que define o deslocamento do corpo, a velocidade
horizontal, o conjunto de ciclos ativos e o custo de vitais por segundo.

```
pose       deslocar  velocidade   fome/s   tédio/s
em pé         0          0.0       -1.1      +0.8
andando       0          7.0       -1.6      -1.5
deitado       2          0.0       -0.6      +0.3
```

`andando` com `tédio` negativo produz auto-regulação: o bicho anda, o tédio
cai, ele para, o tédio volta a subir. O comportamento não é codificado, emerge
dos três números.

As patas também são um ciclo. Parado elas são fixas, andando alternam entre
duas configurações deslocadas em uma coluna. Como o bicho avança cerca de 1,4
pixel por quadro, a pata traseira fica quase estacionária em relação ao chão.

O corpo é estampado a partir de `TOPO`, e o espaço entre a base do corpo e
`CHAO` é preenchido em tempo de composição. Em pé isso estica as patas, deitado
engrossa o corpo. É o que mantém os pés fixos enquanto o corpo se desloca.

## Vitais

```
vida    0..700    7 corações, 100 pontos cada, meio coração a partir de 50
fome    0..100    cheia = alimentado
tédio   0..100    cheio = entediado
```

Vida em escala centesimal permite meio coração e dano fracionário sem usar
float na apresentação.

## Dano

Nenhum stat reduz vida diretamente. A redução vem de um `Risco`: uma condição
que, mantida além da carência, aplica dano contínuo.

```python
Risco("faminto",   lambda v: v.fome.vazio,  carencia=5.0, segundos_por_coracao=15.0)
Risco("entediado", lambda v: v.tedio.cheio, carencia=5.0, segundos_por_coracao=20.0)
```

A carência existe para dar janela de recuperação. Dano na transição puniria
oscilação normal em torno do limite e ausência curta do jogador.

Riscos acumulam. Com fome e tédio simultaneamente no extremo, a perda de vida é
a soma das duas taxas.

Adicionar um risco novo (sede para a planta, frio, doença) é uma entrada na
tupla `RISCOS`.

## Previsto

| Item | Descrição |
|------|-----------|
| Personalidade | vetor de traços `0..1` derivado de seed, modulando decaimento e escolha |
| Cérebro | seleção por utilidade com histerese, piso e duração mínima, substituindo o sorteio de pose |
| Ciclo dia/noite | hora própria do mundo, afetando paleta e peso das poses |
| Clima | estado global com reação por espécie |
| Tempo offline | decaimento retroativo com teto, a partir de `last_seen` |
