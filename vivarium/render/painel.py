"""Painel de log.

Devolve células `(caractere, estilo)`, mesmo formato de `pixels` e `hud`, para
que `tela` desenhe tudo pelo mesmo caminho.

Existe porque um plugin que roda sem deixar rastro não dá para depurar, e um
traceback sem lugar onde aparecer é um erro perdido.
"""

from vivarium.render import paleta

ALTURA = 5          # linhas visíveis


def _linha(texto, estilo, largura):
    """Corta no fim em vez de quebrar: o painel tem altura fixa."""
    texto = texto[:largura]
    return [(c, estilo) for c in texto]


def linhas(textos, largura=48, altura=ALTURA):
    """Últimas `altura` linhas, ajustadas à largura.

    Linha que começa com `!` é erro e sai em cor de alerta. É a convenção mais
    barata que evita o painel ter que conhecer tipos de mensagem.
    """
    visiveis = list(textos)[-altura:]
    saida = []
    for texto in visiveis:
        erro = texto.startswith("!")
        saida.append(_linha(texto, paleta.ALERTA if erro else paleta.ROTULO,
                            largura))
    while len(saida) < altura:
        saida.append([])
    return saida
