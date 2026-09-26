"""Movimento cíclico com relógio próprio."""

import random


class Ritmo:
    """Ciclo de `(valor, duracao)` percorrido em tempo próprio.

    A duração é declarada em segundos e aceita duas formas:

        0.2           duração fixa
        (1.5, 5.0)    sorteada na faixa a cada repetição

    A faixa unifica movimento contínuo e esporádico: um movimento raro é um
    ciclo cujo estado de repouso tem duração sorteada.

        RESPIRAR = [(0, 1.4), (-1, 0.2), (-2, 0.8), (-1, 0.4)]
        PISCAR   = [(ABERTO, (1.5, 5.0)), (MEIO, 0.2), (FECHADO, 0.2)]

    Internamente conta quadros, não segundos: inteiro é exato e não acumula
    erro de ponto flutuante ao longo de uma sessão.
    """

    def __init__(self, relogio, ciclo):
        assert ciclo, "um ritmo precisa de pelo menos um passo"
        self.relogio = relogio
        self.ciclo = ciclo
        self.passo = 0
        self.restante = self._duracao()

    @property
    def valor(self):
        return self.ciclo[self.passo][0]

    def _duracao(self):
        """Quantos quadros dura o passo atual."""
        duracao = self.ciclo[self.passo][1]
        if isinstance(duracao, tuple):
            duracao = random.uniform(*duracao)
        return self.relogio.quadros(duracao)

    def atualizar(self):
        """Avança um quadro e devolve o valor corrente."""
        self.restante -= 1
        while self.restante <= 0:
            self.passo = (self.passo + 1) % len(self.ciclo)
            self.restante += self._duracao()
        return self.valor
