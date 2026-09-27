"""Ações do jogador.

Dado, como as poses: uma ação é tecla, rótulo, efeito e espera. Adicionar
"dar água" para a planta é uma entrada na tupla, não um `if` novo no laço.

Versão embutida. A fase de plugin (doc/05) expõe isto como `@action`, e
escrever a ação duas vezes é deliberado: esta versão é que revela o que a API
precisa entregar ao plugin.

Não conhece terminal: a tecla chega como caractere e o efeito mexe em vitais.
"""

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Acao:
    """Uma ação do jogador.

    `espera` existe para que a ação não anule o modelo de vitais: sem ela,
    segurar a tecla mantém qualquer stat no máximo e o sistema de risco nunca
    dispara.
    """

    nome: str
    tecla: str
    rotulo: str
    efeito: Callable        # recebe o pet
    emote: str = ""
    espera: float = 0.0     # segundos antes de poder repetir


# O efeito delega ao método do pet. Os números vivem num lugar só, e a tecla `a`
# e o `pet.alimentar()` de um plugin são literalmente a mesma coisa.
TODAS = (
    Acao("alimentar", "a", "alimentar",
         lambda pet: pet.alimentar(), emote="ñam", espera=8.0),
    Acao("acariciar", "c", "carinho",
         lambda pet: pet.acariciar(), emote="♥", espera=3.0),
    Acao("brincar", "b", "brincar",
         lambda pet: pet.brincar(), emote="!!", espera=12.0),
)


class Acoes:
    """Traduz tecla em ação e controla a espera de cada uma.

    A espera é contada em quadros, como os ritmos: é contagem discreta e não
    acumula erro. Testável sem terminal, já que a tecla entra como caractere.
    """

    def __init__(self, relogio, acoes=TODAS):
        self.relogio = relogio
        self.embutidas = tuple(acoes)
        self.acoes = list(acoes)
        self._por_tecla = {}
        self._espera = {}
        self._reindexar()

    def _reindexar(self):
        self._por_tecla = {a.tecla: a for a in self.acoes if a.tecla}
        # Espera preservada: recarregar um plugin não deve zerar o cooldown de
        # uma ação que acabou de rodar.
        self._espera = {a.nome: self._espera.get(a.nome, 0) for a in self.acoes}

    def sincronizar(self, de_plugin):
        """Substitui as ações vindas de plugin, mantendo as embutidas."""
        self.acoes = list(self.embutidas) + list(de_plugin)
        self._reindexar()

    def atualizar(self):
        """Avança um quadro em todas as esperas."""
        for nome, restante in self._espera.items():
            if restante > 0:
                self._espera[nome] = restante - 1

    def executar(self, tecla, pet):
        """Aplica a ação da tecla. Devolve a `Acao` aplicada, ou None.

        Devolve None também para tecla sem ação, ação em espera e bicho morto,
        porque quem chama trata os três do mesmo jeito: não houve reação.
        """
        acao = self._por_tecla.get(tecla)
        if acao is None or self._espera[acao.nome] > 0 or pet.vitais.morto:
            return None
        acao.efeito(pet)
        self._espera[acao.nome] = self.relogio.quadros(acao.espera)
        return acao

    def pronta(self, acao):
        return self._espera[acao.nome] == 0
