"""Composição das peças e laço principal."""

import time

from vivarium import api
from vivarium.carregador import Carregador
from vivarium.core.grade import Grade
from vivarium.core.registro import Registro
from vivarium.core.relogio import Relogio
from vivarium.core.teclado import Teclado
from vivarium.pet import arte
from vivarium.pet.acoes import Acoes
from vivarium.pet.gato import Gato
from vivarium.render import hud, painel, paleta, pixels
from vivarium.render.tela import Tela

VERIFICAR_CADA = 1.0        # segundos entre verificações de mtime


class Jogo:
    """Fachada do subsistema.

        1. o relógio emite um tique
        2. a tecla pendente vira ação
        3. o mundo avança um quadro e devolve eventos
        4. plugins reagem: eventos, agendamentos vencidos
        5. o quadro é composto e enviado à tela
    """

    def __init__(self, fps=5, largura=48, altura=arte.ALTURA, depuracao=True,
                 plugins=None):
        self.relogio = Relogio(fps=fps)
        self.grade = Grade(largura, altura)
        self.largura = largura
        self.gato = Gato(self.relogio, mundo_largura=largura)
        self.acoes = Acoes(self.relogio)
        self.teclado = Teclado()
        self.tela = Tela()
        self.depuracao = depuracao

        self.registro = Registro(ao_falhar=self._plugin_falhou)
        self.carregador = Carregador(self.registro, pasta=plugins)
        self._custo_ms = 0.0
        self._ate_verificar = 0

    # -- plugins -------------------------------------------------------

    def _plugin_falhou(self, inscricao, exc):
        """Erro do plugin no painel, em uma linha, e desativado até salvar."""
        api.log(f"! {inscricao.nome}: {inscricao.ultimo_erro}")
        api.log("! desativado até você salvar o arquivo")

    def carregar_plugins(self):
        api.log(f"plugins em {self.carregador.pasta}")
        self.carregador.carregar_tudo(self.gato.idade)
        self._sincronizar_acoes()
        if not self.registro.modulos():
            api.log("nenhum plugin ainda. crie um .py nessa pasta")

    def _sincronizar_acoes(self):
        self.acoes.sincronizar([a for a, _ in self.registro.acoes])

    def _plugins(self):
        """Recarga por mtime, uma vez por segundo e não por quadro."""
        self._ate_verificar -= 1
        if self._ate_verificar > 0:
            return
        self._ate_verificar = self.relogio.quadros(VERIFICAR_CADA)
        antes = len(self.registro.acoes)
        self.carregador.verificar(self.gato.idade)
        if len(self.registro.acoes) != antes:
            self._sincronizar_acoes()

    # -- o quadro ------------------------------------------------------

    def entrada(self):
        """Consome a tecla pendente e aplica a ação correspondente."""
        self.acoes.atualizar()
        tecla = self.teclado.tecla()
        if tecla is None:
            return
        acao = self.acoes.executar(tecla, self.gato)
        if acao and acao.emote:
            self.gato.reagir(acao.emote)

    def quadro(self):
        """Estampa o mundo na grade e converte em células."""
        self.grade.limpar()
        self.grade.estampar(self.gato.mapa(),
                            x=self.gato.coluna,
                            y=self.grade.altura - arte.ALTURA)

        celulas = pixels.para_celulas(self.grade.linhas())

        emote = self.gato.emote()
        if emote:
            pixels.sobrepor(celulas, *emote,
                            estilo=paleta.cor_do_emote(emote[0]))
        # Ordem de cima para baixo: HUD é informação e não pode ser coberta
        # pelo bicho; o log fica embaixo, onde cresce sem empurrar o resto.
        return (hud.linhas(self.gato.vitais)
                + celulas
                + painel.linhas(api.linhas_de_log(), largura=self.largura))

    def rodape(self):
        """Teclas do jogador e, quando ligada, a instrumentação.

        A linha de teclas aparece sempre: é a interface, não depuração. Ação em
        espera troca o colchete por parêntese, o que evita apertar a tecla sem
        efeito. Sem markup do Rich: o rodapé é escrito com `Text.append`, que
        não o interpreta, e `[ctrl+c]` quebraria `from_markup`.
        """
        teclas = []
        for acao in self.acoes.acoes:
            if not acao.tecla:
                continue
            abre, fecha = ("[", "]") if self.acoes.pronta(acao) else ("(", ")")
            teclas.append(f"{abre}{acao.tecla}{fecha} {acao.rotulo}")
        linha = "  ".join(teclas) + "  [ctrl+c] sair"
        if not self.depuracao:
            return linha

        orcamento = self.relogio.dt * 1000
        seta = "→" if self.gato.direcao > 0 else "←"
        return (linha + "\n"
                f"tick {self.relogio.tick}  {self.relogio.fps} fps  "
                f"{self._custo_ms:.2f} ms ({self._custo_ms / orcamento:.2%})  "
                f"{self.gato.pose.nome} {seta}  "
                f"idade {self.gato.idade:.0f}s  "
                f"{len(self.registro.modulos())} plugin(s)")

    def passo(self):
        """Um quadro completo. Separado de `rodar` para ser testável."""
        self.entrada()
        eventos = self.gato.atualizar()
        self.registro.emitir("tique", self.gato)
        for evento in eventos:
            self.registro.emitir(evento, self.gato)
        self.registro.vencidos(self.gato.idade, self.gato)
        self._plugins()
        return self.quadro()

    def rodar(self):
        self.carregar_plugins()
        with self.teclado, self.tela:
            try:
                for _ in self.relogio.tiques():
                    inicio = time.perf_counter()
                    celulas = self.passo()
                    medido = (time.perf_counter() - inicio) * 1000
                    # Média móvel: a leitura instantânea oscila demais.
                    self._custo_ms = 0.8 * self._custo_ms + 0.2 * medido

                    self.tela.mostrar(celulas, self.rodape())
            except KeyboardInterrupt:
                pass
