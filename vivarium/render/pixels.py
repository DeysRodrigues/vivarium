"""Conversão de mapa de pixels em células de terminal.

Sem conhecimento de domínio.

Uma célula de terminal tem aproximadamente o dobro da altura da largura e
carrega dois pixels verticais. `▀` pinta a metade superior com a cor de frente
e a inferior com a cor de fundo, o que permite duas cores por célula. Quando um
dos pixels é transparente, usa-se `▀` ou `▄` apenas com a cor de frente,
deixando o fundo do terminal visível.
"""

from vivarium.render import paleta

CIMA, BAIXO, VAZIO = "▀", "▄", " "


def _celula(cima, baixo):
    """Par de pixels verticais para `(caractere, estilo)`."""
    c, b = paleta.cor(cima), paleta.cor(baixo)
    if c is None and b is None:
        return VAZIO, ""
    if c is None:
        return BAIXO, b
    if b is None:
        return CIMA, c
    return CIMA, f"{c} on {b}"


def para_celulas(mapa):
    """Mapa de pixels para grade de `(caractere, estilo)`."""
    return [
        [_celula(mapa[y][x], mapa[y + 1][x]) for x in range(len(mapa[y]))]
        for y in range(0, len(mapa), 2)
    ]


def sobrepor(celulas, texto, coluna, linha, estilo=paleta.DETALHE):
    """Escreve texto sobre a grade já convertida.

    Emotes e partículas são caracteres, não pixels, e por isso são aplicados
    após a conversão.
    """
    if not 0 <= linha < len(celulas):
        return
    alvo = celulas[linha]
    for i, c in enumerate(texto):
        if 0 <= coluna + i < len(alvo):
            alvo[coluna + i] = (c, estilo)
