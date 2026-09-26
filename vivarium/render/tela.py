"""Saída para o terminal, via Rich."""

from rich.console import Console
from rich.live import Live
from rich.text import Text

from vivarium.render import paleta


class Tela:
    """Região viva no terminal.

    `auto_refresh=False` é deliberado: a cadência é do `Relogio`. Deixar o Rich
    atualizar por conta própria criaria dois relógios concorrentes.

    Quadro idêntico ao anterior é descartado antes da montagem do texto.
    """

    def __init__(self, console=None):
        self.console = console or Console()
        self._live = None
        self._ultimo = None

    def __enter__(self):
        self._live = Live(Text(""), console=self.console,
                          auto_refresh=False, transient=False)
        self._live.__enter__()
        return self

    def __exit__(self, *erro):
        self._live.__exit__(*erro)

    def mostrar(self, celulas, rodape=None):
        chave = (celulas, rodape)
        if chave == self._ultimo:
            return
        self._live.update(_montar(celulas, rodape), refresh=True)
        self._ultimo = chave


def _montar(celulas, rodape):
    """Grade de `(caractere, estilo)` para `rich.Text`.

    Agrupa caracteres consecutivos de mesmo estilo em um span, reduzindo o
    trabalho do Rich e o volume enviado ao terminal.
    """
    texto = Text()
    for linha in celulas:
        pedaco, estilo_atual = "", None
        for caractere, estilo in linha:
            if estilo != estilo_atual:
                if pedaco:
                    texto.append(pedaco, style=estilo_atual or None)
                pedaco, estilo_atual = "", estilo
            pedaco += caractere
        if pedaco:
            texto.append(pedaco, style=estilo_atual or None)
        texto.append("\n")
    if rodape:
        texto.append(rodape, style=paleta.RODAPE)
    return texto
