"""Vitais do bicho e regras de dano.

Regra central: nenhum stat reduz vida diretamente. A redução vem de um risco,
isto é, uma condição extrema mantida além de uma carência. A carência existe
para dar janela de recuperação; dano na transição puniria oscilação normal em
torno do limite.
"""

from dataclasses import dataclass
from typing import Callable

from vivarium.core.stat import Stat

CORACOES = 7
POR_CORACAO = 100          # escala centesimal permite meio coração
VIDA_CHEIA = CORACOES * POR_CORACAO


@dataclass(frozen=True)
class Risco:
    """Condição que, mantida além da carência, aplica dano contínuo."""

    nome: str
    quando: Callable        # recebe os vitais, devolve True em situação ruim
    carencia: float         # segundos em risco antes de começar o dano
    segundos_por_coracao: float


RISCOS = (
    Risco("faminto", lambda v: v.fome.vazio,
          carencia=5.0, segundos_por_coracao=15.0),
    Risco("entediado", lambda v: v.tedio.cheio,
          carencia=5.0, segundos_por_coracao=20.0),
)


class Vitais:
    """Estado contínuo do bicho.

    Medido em segundos, não em quadros: vitais são contínuos, animação é
    discreta. O desgaste é multiplicado por `relogio.dt`, o que mantém a
    velocidade da simulação independente do fps.
    """

    def __init__(self, relogio):
        self.relogio = relogio
        self.vida = Stat(VIDA_CHEIA, maximo=VIDA_CHEIA)
        self.fome = Stat(100)      # cheia = alimentado
        self.tedio = Stat(15)      # cheio = entediado
        self._sofrendo_ha = {risco.nome: 0.0 for risco in RISCOS}

    @property
    def morto(self):
        return self.vida.vazio

    @property
    def sofrendo(self):
        """Riscos que já passaram da carência e estão aplicando dano."""
        return [r.nome for r in RISCOS
                if self._sofrendo_ha[r.nome] > r.carencia]

    def atualizar(self, pose):
        """Avança um tick. A pose em curso define o custo."""
        if self.morto:
            return
        dt = self.relogio.dt
        self.fome.add(-pose.gasto_fome * dt)
        self.tedio.add(pose.gasto_tedio * dt)
        self._sofrer(dt)

    def _sofrer(self, dt):
        for risco in RISCOS:
            if not risco.quando(self):
                self._sofrendo_ha[risco.nome] = 0.0     # saiu do risco
                continue
            self._sofrendo_ha[risco.nome] += dt
            if self._sofrendo_ha[risco.nome] > risco.carencia:
                self.vida.add(-POR_CORACAO / risco.segundos_por_coracao * dt)
