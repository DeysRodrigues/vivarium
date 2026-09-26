"""Valor numérico com limites."""

from dataclasses import dataclass


@dataclass
class Stat:
    """Número que não ultrapassa os limites definidos.

    Não carrega significado. A interpretação fica em quem usa, o que permite
    reaproveitar a mesma estrutura para vida, fome, tédio e vitais de outras
    espécies.
    """

    valor: float
    minimo: float = 0.0
    maximo: float = 100.0

    def add(self, quanto):
        """Soma respeitando os limites e devolve o novo valor."""
        self.valor = min(self.maximo, max(self.minimo, self.valor + quanto))
        return self.valor

    def encher(self):
        self.valor = self.maximo

    @property
    def pct(self):
        """Posição entre os limites, de 0.0 a 1.0. É o que a barra desenha."""
        return (self.valor - self.minimo) / (self.maximo - self.minimo)

    @property
    def vazio(self):
        return self.valor <= self.minimo

    @property
    def cheio(self):
        return self.valor >= self.maximo
