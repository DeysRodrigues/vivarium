"""Indicadores de vitais.

Devolve células `(caractere, estilo)`, mesmo formato produzido por `pixels`,
de modo que `tela` desenhe HUD e mundo pelo mesmo caminho.
"""

from vivarium.pet.vitais import CORACOES, POR_CORACAO
from vivarium.render import paleta

CHEIO, MEIO, VAZIO = "♥", "♥", "♡"
BLOCO, FALTA = "█", "░"
LARGURA_BARRA = 10
ROTULO = 6          # largura do rótulo, para alinhar as barras


def _texto(texto, estilo):
    return [(c, estilo) for c in texto]


def coracoes(vida):
    """Sequência de corações, com meio coração.

    A escala interna de vida (0 a 700) existe para isto: 100 pontos por
    coração, e resto a partir de 50 rende meio coração.
    """
    celulas = []
    for i in range(CORACOES):
        restante = vida.valor - i * POR_CORACAO
        if restante >= POR_CORACAO:
            celulas.append((CHEIO, paleta.CORACAO))
        elif restante >= POR_CORACAO / 2:
            celulas.append((MEIO, paleta.CORACAO_VAZIO + " on " + paleta.CORACAO))
        else:
            celulas.append((VAZIO, paleta.CORACAO_VAZIO))
    return celulas


def barra(rotulo, stat, alto_e_bom=True):
    cor = paleta.cor_da_barra(stat.pct, alto_e_bom)
    cheias = round(stat.pct * LARGURA_BARRA)
    return (_texto(rotulo.ljust(ROTULO), paleta.ROTULO)
            + _texto(BLOCO * cheias, cor)
            + _texto(FALTA * (LARGURA_BARRA - cheias), paleta.CORACAO_VAZIO))


def linhas(vitais):
    """Linhas do HUD, de cima para baixo."""
    saida = [
        coracoes(vitais.vida),
        barra("fome", vitais.fome, alto_e_bom=True),
        barra("tédio", vitais.tedio, alto_e_bom=False),
    ]
    if vitais.morto:
        saida.append(_texto("ele morreu.", paleta.ALERTA))
    elif vitais.sofrendo:
        saida.append(_texto(" / ".join(vitais.sofrendo) + "!", paleta.ALERTA))
    else:
        saida.append([])
    return saida
