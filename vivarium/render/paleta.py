"""Nomes de cor.

Único ponto do projeto que define cor. Nomes são os do Rich; `python -m
rich.color` lista o conjunto disponível.

Preto puro é indistinguível do fundo em terminal escuro, por isso o corpo usa
cinza escuro.
"""

CORPO = "grey42"       # pixel `#`
DETALHE = "white"      # pixel `o`
RODAPE = "grey35"      # linha de instrumentação

# --- HUD ---
CORACAO = "red"
CORACAO_VAZIO = "grey30"
ROTULO = "grey50"
ALERTA = "bright_red"

# A cor da barra comunica a faixa mais rápido que o valor numérico.
BARRA_BOA = "green"
BARRA_MEDIA = "yellow"
BARRA_RUIM = "red"


def cor_da_barra(pct, alto_e_bom=True):
    """Faixa de cor a partir da proporção preenchida.

    `alto_e_bom=False` inverte a escala, para stats em que o valor alto é o
    estado ruim (tédio).
    """
    bom = pct if alto_e_bom else 1.0 - pct
    if bom > 0.6:
        return BARRA_BOA
    if bom > 0.3:
        return BARRA_MEDIA
    return BARRA_RUIM

_POR_PIXEL = {"#": CORPO, "o": DETALHE}


def cor(pixel):
    """Cor de um pixel, ou None se transparente."""
    return _POR_PIXEL.get(pixel)
