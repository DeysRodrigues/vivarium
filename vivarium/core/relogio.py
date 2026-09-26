"""Tempo do jogo."""

import time


class Relogio:
    """Converte tempo real em ticks de passo fixo. Um tick equivale a um quadro.

        for _ in relogio.tiques():
            ...

    É o único ponto do projeto que consulta o relógio do sistema. O resto conta
    quadros, o que torna a simulação determinística e verificável sem espera
    real.

    `agora` e `dormir` são injetados para permitir substituição em teste.
    """

    def __init__(self, fps=5, agora=time.monotonic, dormir=time.sleep):
        self.fps = fps
        self.dt = 1.0 / fps
        self.tick = 0
        self._agora = agora
        self._dormir = dormir

    def quadros(self, segundos):
        """Converte segundos em quadros.

        Único ponto de conversão do projeto. Toda duração declarada em segundos
        passa por aqui, o que mantém a duração real independente do fps.

        `max(1, ...)` impede duração menor que um quadro, que cairia entre dois
        desenhos e não seria observável.
        """
        return max(1, round(segundos * self.fps))

    def tiques(self):
        """Emite um tique por quadro, indefinidamente, dormindo o intervalo."""
        proximo = self._agora()
        while True:
            self.tick += 1
            yield self.tick

            proximo += self.dt
            espera = proximo - self._agora()
            if espera > 0:
                self._dormir(espera)
            else:
                # Atraso acumulado (terminal lento, processo suspenso). Reancora
                # no instante atual em vez de recuperar o acúmulo em bloco.
                proximo = self._agora()
