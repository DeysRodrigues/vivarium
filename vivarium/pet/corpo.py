"""Composição do quadro: pose e movimentos para mapa de pixels."""

from vivarium.pet import arte


def compor(pose, mov, espelhado=False):
    """Combina pose e valores correntes dos movimentos em um mapa de pixels.

    `mov` é um dicionário em vez de parâmetros posicionais: adicionar um
    movimento novo não altera a assinatura.
    """
    dy = pose.deslocar + mov["respirar"]
    tela = [list(arte.LINHA_VAZIA) for _ in range(arte.ALTURA)]

    def dentro(y):
        return 0 <= y < arte.ALTURA

    for y in range(arte.TOPO, arte.FIM_DO_CORPO + 1):        # corpo
        if dentro(y + dy):
            tela[y + dy] = list(arte.MAPA[y])

    for i, y in enumerate(arte.LINHAS_OLHO):                 # olhos
        if dentro(y + dy):
            tela[y + dy] = list(mov["piscar"][i])

    for orelha, chave in ((arte.ORELHA_ESQ, "orelha_esq"),
                          (arte.ORELHA_DIR, "orelha_dir")):
        if mov[chave] and dentro(arte.TOPO + dy):            # orelha abaixada
            for x in orelha:
                tela[arte.TOPO + dy][x] = "."

    if mov["rabo"]:                                          # rabo balançando
        for y in arte.LINHAS_TOPO_RABO:
            if dentro(y + dy):
                _empurrar_rabo(tela[y + dy])

    # O corpo se deslocou mas os pés são fixos. O vão entre a base do corpo e
    # o chão é preenchido aqui: em pé estica as patas, deitado engrossa o corpo.
    for y in range(arte.FIM_DO_CORPO + dy + 1, arte.CHAO + 1):
        if dentro(y):
            for x in mov["patas"]:
                if 0 <= x < arte.LARGURA:
                    tela[y][x] = "#"

    linhas = ["".join(linha) for linha in tela]
    if espelhado:
        linhas = [linha[::-1] for linha in linhas]
    return linhas


def _empurrar_rabo(celulas):
    """Desloca o rabo uma coluna à direita, no próprio buffer."""
    ocupadas = [x for x in range(arte.COLUNA_RABO, arte.LARGURA)
                if celulas[x] == "#"]
    for x in reversed(ocupadas):
        celulas[x] = "."
        if x + 1 < arte.LARGURA:
            celulas[x + 1] = "#"
