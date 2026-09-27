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
        self.idade = 0.0
        self._emote = ""
        self._emote_ate = 0
        self._antes = {}
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

    def reagir(self, emote, segundos=1.6):
        """Emote temporário, que se sobrepõe ao da pose.

        É o retorno visível de uma ação do jogador: sem ele, alimentar um bicho
        de fome cheia não tem efeito nenhum na tela.
        """
        self._emote = emote
        self._emote_ate = self.relogio.quadros(segundos)

    # -- o que o mundo precisa saber -----------------------------------

    def _eventos(self):
        """Eventos ocorridos neste quadro, por transição de estado.

        Devolvidos em vez de disparados: `pet/` não conhece o registro de
        plugins, então quem monta o jogo é que emite. Mantém esta camada
        testável sem registro nenhum.

        Transição e não condição: `fome_vazia` dispara uma vez ao esvaziar, não
        a cada quadro em que está vazia.
        """
        agora = {
            "fome_vazia": self.vitais.fome.vazio,
            "tedio_cheio": self.vitais.tedio.cheio,
            "dormiu": self.pose is poses.DEITADO,
            "morreu": self.vitais.morto,
        }
        saiu = []
        for nome, ligado in agora.items():
            if ligado and not self._antes.get(nome):
                saiu.append(nome)
        if self._antes.get("dormiu") and not agora["dormiu"]:
            saiu.append("acordou")
        self._antes = agora
        return saiu

    # -- ações, chamáveis por código ou por tecla ----------------------

    def alimentar(self, quanto=30):
        self.vitais.fome.add(quanto)

    def acariciar(self):
        self.vitais.tedio.add(-8)
        # Único ponto que recupera vida. Ver pet/acoes.py.
        self.vitais.vida.add(10)

    def brincar(self):
        self.vitais.tedio.add(-25)
        self.vitais.fome.add(-6)     # brincar dá fome

    @property
    def fome(self):
        return self.vitais.fome.valor

    @fome.setter
    def fome(self, valor):
        self.vitais.fome.add(valor - self.vitais.fome.valor)

    @property
    def tedio(self):
        return self.vitais.tedio.valor

    @tedio.setter
    def tedio(self, valor):
        self.vitais.tedio.add(valor - self.vitais.tedio.valor)

    @property
    def vida(self):
        return self.vitais.vida.valor

    @vida.setter
    def vida(self, valor):
        self.vitais.vida.add(valor - self.vitais.vida.valor)

    @property
    def especie(self):
        return "gato"

    def atualizar(self):
        """Avança um quadro. Devolve os eventos ocorridos."""
        self.idade += self.relogio.dt
        self.vitais.atualizar(self.pose)
        # Antes da troca de pose, que sai da função mais abaixo.
        if self._emote_ate > 0:
            self._emote_ate -= 1

        self.ate_trocar -= 1
        if self.ate_trocar <= 0:
            self._escolher_pose()
            return self._eventos()

        self.mov = {nome: r.atualizar() for nome, r in self.ritmos.items()}
        if self.pose.velocidade:
            self._andar()
        return self._eventos()

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
        """`(texto, coluna, linha)` a sobrepor, ou None.

        A reação a uma ação tem precedência sobre o emote da pose: o bicho
        dormindo que recebe carinho mostra o coração, não o `zZ`.
        """
        texto = self._emote if self._emote_ate > 0 else self.pose.emote
        if not texto:
            return None
        # Célula imediatamente acima do topo do corpo. Ancorar no corpo e não
        # em linha fixa é o que mantém o emote fora do bicho em qualquer pose:
        # deitado o corpo desce uma célula e o emote acompanha.
        dy = self.pose.deslocar + self.mov["respirar"]
        linha = max(0, (arte.TOPO + dy) // 2 - 1)
        return texto, self.coluna + arte.LARGURA // 2, linha
