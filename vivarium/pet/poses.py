"""Poses do gato e ciclos de movimento.

Tudo aqui é dado. Uma pose define deslocamento do corpo, velocidade
horizontal, os ciclos ativos enquanto ela durar e o custo de vitais por
segundo.

Duração de ciclo em segundos: valor fixo, ou `(min, max)` sorteado a cada
repetição.
"""

from dataclasses import dataclass
from typing import Mapping

from vivarium.pet import arte

# ----------------------------------------------------------- ciclos

# Na respiração, -1 não é pose de repouso: 1 pixel equivale a meia célula, e o
# quadro resultante fica com todo contorno sobre a divisa. Ele é o quadro de
# passagem (in-between) e dura pouco. As posições em que o corpo para (0 e -2)
# são deslocamentos pares e permanecem nítidas.
RESPIRAR = [(0, 1.4), (-1, 0.2), (-2, 0.8), (-1, 0.4)]
RESPIRAR_DORMINDO = [(0, 2.4), (-1, 0.4), (-2, 1.6), (-1, 0.4)]
RESPIRAR_ANDANDO = [(0, 1.0), (-1, 0.2), (-2, 0.6), (-1, 0.2)]

PISCAR = [(arte.OLHO_ABERTO, (1.5, 5.0)), (arte.OLHO_MEIO, 0.2),
          (arte.OLHO_FECHADO, 0.2)]
OLHOS_FECHADOS = [(arte.OLHO_FECHADO, 1.0)]

TREMER_ORELHA = [(False, (4.0, 13.0)), (True, 0.2), (False, 0.2), (True, 0.2)]
ORELHA_QUIETA = [(False, 1.0)]

BALANCAR_RABO = [(False, (3.0, 9.0)), (True, 0.4), (False, 0.2), (True, 0.4)]
RABO_ANDANDO = [(False, 0.6), (True, 0.6)]

# As patas são um ciclo como os demais. Parado o valor é fixo; andando alterna
# entre duas configurações deslocadas em uma coluna. Como o avanço é de cerca
# de 1,4 pixel por quadro, a pata traseira fica quase estacionária em relação
# ao chão.
PATAS_PARADAS = [(arte.COLUNAS_PATAS, 1.0)]
PATAS_ANDANDO = [((2, 3, 9, 10), 0.4), ((3, 4, 10, 11), 0.4)]
CORPO_NO_CHAO = [(arte.COLUNAS_CORPO, 1.0)]     # deitado, sem patas


@dataclass(frozen=True)
class Pose:
    """Configuração de uma pose: geometria, ciclos ativos e custo de vitais."""

    nome: str
    deslocar: int                 # quanto o corpo desce (em pixels)
    velocidade: float             # pixels por segundo; 0 = parado
    ciclos: Mapping[str, list]
    emote: str = ""
    # Custo por segundo nesta pose. Tédio negativo significa que a pose
    # distrai, o que produz auto-regulação do comportamento.
    gasto_fome: float = 1.1
    gasto_tedio: float = 0.8


EM_PE = Pose(
    nome="em pé", deslocar=0, velocidade=0.0,
    gasto_fome=1.1, gasto_tedio=0.8,
    ciclos={
        "respirar": RESPIRAR,
        "piscar": PISCAR,
        "patas": PATAS_PARADAS,
        "orelha_esq": TREMER_ORELHA,
        "orelha_dir": TREMER_ORELHA,
        "rabo": BALANCAR_RABO,
    },
)

ANDANDO = Pose(
    nome="andando", deslocar=0, velocidade=7.0,
    gasto_fome=1.6, gasto_tedio=-1.5,
    ciclos={
        "respirar": RESPIRAR_ANDANDO,
        "piscar": PISCAR,
        "patas": PATAS_ANDANDO,
        "orelha_esq": ORELHA_QUIETA,
        "orelha_dir": ORELHA_QUIETA,
        "rabo": RABO_ANDANDO,
    },
)

DEITADO = Pose(
    nome="deitado", deslocar=2, velocidade=0.0, emote="zZ",
    gasto_fome=0.6, gasto_tedio=0.3,
    ciclos={
        "respirar": RESPIRAR_DORMINDO,
        "piscar": OLHOS_FECHADOS,
        "patas": CORPO_NO_CHAO,
        "orelha_esq": TREMER_ORELHA,
        "orelha_dir": ORELHA_QUIETA,
        "rabo": [(False, 1.0)],
    },
)

TODAS = (EM_PE, ANDANDO, DEITADO)
