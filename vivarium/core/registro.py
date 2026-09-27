"""Registro de handlers: eventos, agendamentos e ações.

Sem domínio. Não sabe o que é um pet nem o que significa `fome_vazia`; guarda
funções por chave, dispara e isola exceção.

Duas invariantes vivem aqui, e as duas são difíceis de perceber quando quebram:

* **Esquecer por módulo.** Sem isso, recarregar um plugin duplica os handlers e
  o efeito se multiplica sem erro visível.
* **Isolar exceção por handler.** Um `TypeError` num plugin não pode derrubar o
  processo nem impedir os outros handlers de rodar.
"""

import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable


def resumo_do_erro(exc):
    """Uma linha: onde e o quê.

    Não usa `traceback.format_exc()` para mostrar o código-fonte: o formatador
    lê o arquivo do disco no momento da formatação, e num projeto com recarga a
    quente o arquivo já mudou — o traceback sai apontando a linha nova com o
    erro antigo, que é pior que não mostrar linha nenhuma.
    """
    if isinstance(exc, SyntaxError) and exc.lineno:
        onde = f"{Path(exc.filename or '?').name}:{exc.lineno}"
        return f"{onde} SyntaxError: {exc.msg}"
    quadros = traceback.extract_tb(exc.__traceback__)
    if quadros:
        ultimo = quadros[-1]
        onde = f"{Path(ultimo.filename).name}:{ultimo.lineno}"
    else:
        onde = "?"
    return f"{onde} {type(exc).__name__}: {exc}"


@dataclass
class Inscricao:
    """Um handler registrado, com a origem que permite esquecê-lo."""

    fn: Callable
    modulo: str
    se: Callable = None          # filtro opcional, recebe os mesmos dados
    execucoes: int = 0
    ultimo_erro: str = None
    # Desativado ao falhar, e só volta quando o arquivo muda (o carregador
    # recria a inscrição). Sem isso, um handler de `tique` que quebra reporta o
    # mesmo erro cinco vezes por segundo e o painel fica inútil.
    ativo: bool = True

    @property
    def nome(self):
        return f"{self.modulo}.{self.fn.__name__}"


@dataclass
class Agendado(Inscricao):
    """Handler que roda a cada `intervalo` segundos de idade do bicho."""

    intervalo: float = 60.0
    proximo: float = 0.0


@dataclass
class Registro:
    """Onde os plugins ficam registrados.

    É um objeto e não um módulo com globais: o teste cria um registro limpo, e
    dois jogos no mesmo processo não compartilham handler.
    """

    eventos: dict = field(default_factory=dict)
    agendados: list = field(default_factory=list)
    acoes: list = field(default_factory=list)
    ao_falhar: Callable = None       # recebe (inscricao, texto do traceback)

    # -- registrar -----------------------------------------------------

    def inscrever(self, evento, fn, modulo, se=None):
        inscricao = Inscricao(fn=fn, modulo=modulo, se=se)
        self.eventos.setdefault(evento, []).append(inscricao)
        return inscricao

    def agendar(self, fn, modulo, intervalo, idade, agora=False):
        agendado = Agendado(fn=fn, modulo=modulo, intervalo=intervalo,
                            proximo=idade if agora else idade + intervalo)
        self.agendados.append(agendado)
        return agendado

    def registrar_acao(self, acao, modulo):
        self.acoes.append((acao, modulo))
        return acao

    def esquecer(self, modulo):
        """Remove tudo que veio de um módulo, antes de reimportá-lo."""
        for evento, lista in self.eventos.items():
            self.eventos[evento] = [i for i in lista if i.modulo != modulo]
        self.agendados = [a for a in self.agendados if a.modulo != modulo]
        self.acoes = [(a, m) for a, m in self.acoes if m != modulo]

    def modulos(self):
        nomes = {i.modulo for lista in self.eventos.values() for i in lista}
        nomes |= {a.modulo for a in self.agendados}
        nomes |= {m for _, m in self.acoes}
        return sorted(nomes)

    def inscricoes_de(self, modulo):
        """Tudo que um módulo registrou. Usado pelo painel de abertura."""
        de_evento = [i for lista in self.eventos.values() for i in lista
                     if i.modulo == modulo]
        return de_evento + [a for a in self.agendados if a.modulo == modulo]

    # -- disparar ------------------------------------------------------

    def _chamar(self, inscricao, *args):
        """Executa um handler. Exceção fica contida nele.

        Ao falhar, o handler é **desativado** e só volta quando o arquivo muda,
        porque o carregador recria a inscrição. Reportar o mesmo erro a cada
        quadro deixaria o painel ilegível.
        """
        if not inscricao.ativo:
            return False
        try:
            inscricao.fn(*args)
            inscricao.execucoes += 1
            return True
        except Exception as exc:
            inscricao.ultimo_erro = resumo_do_erro(exc)
            inscricao.ativo = False
            if self.ao_falhar:
                self.ao_falhar(inscricao, exc)
            return False

    def emitir(self, evento, *args):
        """Dispara um evento. Devolve quantos handlers rodaram sem erro."""
        rodaram = 0
        for inscricao in list(self.eventos.get(evento, ())):
            if not inscricao.ativo:
                continue
            if inscricao.se is not None:
                try:
                    if not inscricao.se(*args):
                        continue
                except Exception as exc:
                    inscricao.ultimo_erro = resumo_do_erro(exc)
                    inscricao.ativo = False
                    if self.ao_falhar:
                        self.ao_falhar(inscricao, exc)
                    continue
            rodaram += self._chamar(inscricao, *args)
        return rodaram

    def vencidos(self, idade, *args):
        """Dispara os agendamentos vencidos. Devolve quantos rodaram.

        Um agendamento vencido várias vezes roda **uma**: `proximo` é
        recolocado a partir da idade atual, não somado repetidamente. Dez cafés
        de uma vez é bug, não recuperação.
        """
        rodaram = 0
        for agendado in list(self.agendados):
            if not agendado.ativo or idade < agendado.proximo:
                continue
            agendado.proximo = idade + agendado.intervalo
            rodaram += self._chamar(agendado, *args)
        return rodaram
