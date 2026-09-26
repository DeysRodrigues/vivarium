"""Arte do gato e anatomia derivada do mapa.

O mapa é dado, não código. Anatomia (orelhas, colunas do corpo, olhos) é
extraída dele em tempo de import, de modo que redesenhar o bicho não exige
atualizar constantes espalhadas.

Restrição do meio-bloco: número par de linhas, e cada detalhe começando em
linha par com altura par. Detalhe em linha ímpar é partido entre duas células.
As duas primeiras linhas ficam vazias e servem de área para emotes.
"""

from vivarium.core.mapa import carregar

GATO = """
................
................
..##..##....##..
..##..##....##..
..#######...##..
..##o#o##...##..
..##o#o##..##...
..#######..##...
....###....#....
...#########....
...########.....
...########.....
...########.....
...########.....
...##....##.....
...##....##.....
"""

MAPA = carregar(GATO)
ALTURA, LARGURA = len(MAPA), len(MAPA[0])
LINHA_VAZIA = "." * LARGURA

# Referências de posição usadas pela composição do quadro.
TOPO = 2             # primeira linha do corpo (orelhas)
FIM_DO_CORPO = 13    # última linha do corpo, onde nascem as patas
CHAO = 15            # linha do chão; referência fixa do corpo
COLUNAS_PATAS = (3, 4, 9, 10)
LINHAS_OLHO = (5, 6)
COLUNA_RABO = 10     # limite: à direita é rabo, à esquerda é cabeça
LINHAS_TOPO_RABO = (2, 3, 4, 5)

# Colunas ocupadas pelo corpo na altura da barriga. Usadas para preencher até
# o chão na pose deitada.
COLUNAS_CORPO = tuple(x for x, c in enumerate(MAPA[FIM_DO_CORPO]) if c == "#")


def _blocos(linha, limite):
    """Grupos contíguos de `#` até a coluna `limite`."""
    grupos, atual = [], []
    for x, c in enumerate(linha[:limite]):
        if c == "#":
            atual.append(x)
        elif atual:
            grupos.append(tuple(atual))
            atual = []
    if atual:
        grupos.append(tuple(atual))
    return grupos


# Extraídas do mapa: redesenhar as orelhas não exige ajustar estas constantes.
ORELHA_ESQ, ORELHA_DIR = _blocos(MAPA[TOPO], COLUNA_RABO)


def _sem_olho(linha):
    """Substitui o detalhe por corpo, fechando o olho naquela linha."""
    return linha.replace("o", "#")


OLHO_ABERTO = (MAPA[5], MAPA[6])
OLHO_MEIO = (_sem_olho(MAPA[5]), MAPA[6])
OLHO_FECHADO = (_sem_olho(MAPA[5]), _sem_olho(MAPA[6]))
