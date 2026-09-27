"""Leitura de teclado sem bloquear o laço."""

import os
import select
import sys
import termios
import tty


class Teclado:
    """`stdin` em modo cbreak, lido sem bloquear.

    Rich não lê teclado, e `curses` tomaria a tela inteira, o que brigaria com
    o `Live`. `termios` resolve só a entrada e mantém a dependência única.

    `cbreak` e não `raw`: preserva `ISIG`, então Ctrl+C continua virando
    `KeyboardInterrupt` e o laço sai pelo caminho que já existia.

    Fora de um terminal (pipe, teste, CI) degrada para "nunca há tecla" em vez
    de falhar.
    """

    def __init__(self, entrada=None):
        self.entrada = entrada or sys.stdin
        self.ativo = hasattr(self.entrada, "isatty") and self.entrada.isatty()
        self._antes = None

    def __enter__(self):
        if self.ativo:
            self._antes = termios.tcgetattr(self.entrada)
            tty.setcbreak(self.entrada.fileno())
        return self

    def __exit__(self, *erro):
        if self._antes is not None:
            termios.tcsetattr(self.entrada, termios.TCSADRAIN, self._antes)
            self._antes = None

    def tecla(self):
        """Primeira tecla pendente, ou None. O resto do buffer é descartado.

        Descartar é intencional: segurar a tecla enfileiraria dezenas de ações
        para os quadros seguintes, e o bicho continuaria reagindo depois de o
        jogador ter parado.

        Lê por `os.read` em vez de `entrada.read(1)`, que pode bloquear
        tentando encher o buffer de texto mesmo com o descritor pronto.
        """
        if not self.ativo:
            return None
        fd = self.entrada.fileno()
        primeira = None
        while select.select([self.entrada], [], [], 0)[0]:
            dados = os.read(fd, 1024)
            if not dados:
                break
            if primeira is None:
                primeira = dados[:1].decode(errors="ignore")
        return primeira or None
