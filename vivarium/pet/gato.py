"""Estado do bicho: posição, pose ativa e composição do quadro.

Não conhece o terminal. Devolve mapa de pixels; a conversão para caracteres é
responsabilidade de `render`. Isso mantém a simulação verificável sem terminal
alocado e permite trocar o backend de saída sem alterar esta camada.
"""

import random

from vivarium.core.ritmo import Ritmo
from vivarium.pet import arte, poses
from vivarium.pet.corpo import compor
from vivarium.pet.vitais import Vitais

DIREITA, ESQUERDA = 1, -1


class Gato:
    def __init__(self, relogio, mundo_largura, x=None):
        self.relogio = relogio
        self.mundo_largura = mundo_largura
        self.x = (mundo_largura - arte.LARGURA) / 2 if x is None else x
        self.direcao = DIREITA
        self.vitais = Vitais(relogio)
        self.pose = poses.EM_PE
        self._entrar_na_pose(poses.EM_PE)

    # -- pose ---------------------------------------------------------

    def _entrar_na_pose(self, pose):
        """Entra em uma pose, substituindo o conjunto de ritmos ativos."""
        self.pose = pose
        self.ritmos = {nome: Ritmo(self.relogio, ciclo)
                       for nome, ciclo in pose.ciclos.items()}
        self.mov = {nome: r.valor for nome, r in self.ritmos.items()}
        self.ate_trocar = random.randint(self.relogio.quadros(5.0),
                                         self.relogio.quadros(12.0))

    def _escolher_pose(self):
        """Sorteia a próxima pose, sem repetir a atual.

        Placeholder: previsto substituir por seleção por utilidade
        (doc/04-simulacao.md, seção Previsto).
        """
        opcoes = [p for p in poses.TODAS if p is not self.pose]
        nova = random.choice(opcoes)
        if nova is poses.ANDANDO and random.random() < 0.5:
            self.direcao = -self.direcao
        self._entrar_na_pose(nova)

    # -- o tick -------------------------------------------------------

    def atualizar(self):
        """Avança um quadro."""
        self.vitais.atualizar(self.pose)

        self.ate_trocar -= 1
        if self.ate_trocar <= 0:
            self._escolher_pose()
            return

        self.mov = {nome: r.atualizar() for nome, r in self.ritmos.items()}
        if self.pose.velocidade:
            self._andar()

    def _andar(self):
        # Velocidade em pixels por segundo: deslocamento é contínuo. A
        # animação é contada em quadros; são unidades distintas por projeto.
        self.x += self.direcao * self.pose.velocidade * self.relogio.dt
        limite = self.mundo_largura - arte.LARGURA
        if self.x <= 0 or self.x >= limite:
            self.x = min(max(self.x, 0), limite)
            self.direcao = -self.direcao

    # -- o que desenhar -----------------------------------------------

    def mapa(self):
        """Mapa de pixels do bicho com a pose e os movimentos correntes."""
        return compor(self.pose, self.mov, espelhado=self.direcao == ESQUERDA)

    @property
    def coluna(self):
        return round(self.x)

    def emote(self):
        """`(texto, coluna, linha)` a sobrepor, ou None."""
        if not self.pose.emote:
            return None
        sobe = max(0, 1 + self.mov["respirar"])
        return self.pose.emote, self.coluna + arte.LARGURA // 2, sobe
