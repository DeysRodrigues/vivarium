"""Composição das peças e laço principal."""

import time

from vivarium.core.grade import Grade
from vivarium.core.relogio import Relogio
from vivarium.pet import arte
from vivarium.pet.gato import Gato
from vivarium.render import hud, pixels
from vivarium.render.tela import Tela


class Jogo:
    """Fachada do subsistema.

        1. o relógio emite um tique
        2. o mundo avança um quadro
        3. o quadro é composto e enviado à tela
    """

    def __init__(self, fps=5, largura=48, altura=arte.ALTURA, depuracao=True):
        self.relogio = Relogio(fps=fps)
        self.grade = Grade(largura, altura)
        self.gato = Gato(self.relogio, mundo_largura=largura)
        self.tela = Tela()
        self.depuracao = depuracao
        self._custo_ms = 0.0

    def quadro(self):
        """Estampa o mundo na grade e converte em células."""
        self.grade.limpar()
        self.grade.estampar(self.gato.mapa(),
                            x=self.gato.coluna,
                            y=self.grade.altura - arte.ALTURA)

        celulas = pixels.para_celulas(self.grade.linhas())

        emote = self.gato.emote()
        if emote:
            pixels.sobrepor(celulas, *emote)
        # HUD acima do mundo: é informação e não pode ser coberta pelo bicho.
        return hud.linhas(self.gato.vitais) + celulas

    def rodape(self):
        """Instrumentação: custo medido por quadro e fração do orçamento."""
        if not self.depuracao:
            return None
        orcamento = self.relogio.dt * 1000
        seta = "→" if self.gato.direcao > 0 else "←"
        return (f"tick {self.relogio.tick}  {self.relogio.fps} fps  "
                f"{self._custo_ms:.2f} ms ({self._custo_ms / orcamento:.2%})  "
                f"{self.gato.pose.nome} {seta} x={self.gato.coluna}")

    def rodar(self):
        with self.tela:
            try:
                for _ in self.relogio.tiques():
                    inicio = time.perf_counter()
                    self.gato.atualizar()
                    celulas = self.quadro()
                    medido = (time.perf_counter() - inicio) * 1000
                    # Média móvel: a leitura instantânea oscila demais.
                    self._custo_ms = 0.8 * self._custo_ms + 0.2 * medido

                    self.tela.mostrar(celulas, self.rodape())
            except KeyboardInterrupt:
                pass
