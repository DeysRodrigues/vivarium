"""Leitura de mapa de pixels em texto.

Convenção de pixel:

    .  transparente
    #  corpo
    o  detalhe
"""


def carregar(texto):
    """Converte o texto em lista de linhas, validando a geometria.

    Paridade e largura são verificadas aqui porque a renderização em meio-bloco
    consome as linhas em pares. Um mapa ímpar ou irregular produziria recorte
    silencioso em vez de erro.
    """
    linhas = texto.strip("\n").split("\n")
    assert len(linhas) % 2 == 0, "o mapa precisa ter número par de linhas"
    for i, linha in enumerate(linhas):
        assert len(linha) == len(linhas[0]), (
            f"linha {i} tem {len(linha)} caracteres, "
            f"as outras têm {len(linhas[0])}"
        )
    return linhas
