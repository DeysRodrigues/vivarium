"""Descoberta, importação e recarga dos plugins.

O núcleo nunca importa um plugin: este módulo varre a pasta, importa cada
arquivo e registra o que estiver marcado pelos decoradores de `api`. A
dependência tem sentido único.
"""

import importlib.util
import os
import sys
from pathlib import Path

from vivarium import api
from vivarium.core.registro import resumo_do_erro
from vivarium.pet.acoes import Acao


def pasta_padrao():
    """`$XDG_CONFIG_HOME/vivarium/plugins`, ou `./plugins` se existir.

    A pasta local tem precedência para que clonar o repositório e rodar já
    encontre os exemplos, sem passo de instalação.
    """
    local = Path("plugins")
    if local.is_dir():
        return local
    base = os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config"
    return Path(base) / "vivarium" / "plugins"


class Carregador:
    """Mantém o registro em sincronia com os arquivos da pasta.

    Recarga por `mtime`: mais barato que uma dependência de observador de
    arquivos para uma dezena de arquivos. `verificar()` é chamado uma vez por
    segundo, não por quadro.
    """

    def __init__(self, registro, pasta=None, ao_avisar=api.log):
        self.registro = registro
        self.pasta = Path(pasta) if pasta else pasta_padrao()
        self.avisar = ao_avisar
        self._mtimes = {}
        self.historico = {}      # nome -> {"erro": str|None}

    # -- varredura -----------------------------------------------------

    def arquivos(self):
        if not self.pasta.is_dir():
            return []
        return sorted(p for p in self.pasta.glob("*.py")
                      if not p.name.startswith("_"))

    def carregar_tudo(self, idade=0.0):
        for caminho in self.arquivos():
            self.carregar(caminho, idade)

    def verificar(self, idade=0.0):
        """Recarrega o que mudou e carrega o que apareceu.

        Arquivo apagado é esquecido do registro, mas permanece no histórico: o
        registro é do que já foi escrito, e apagar o arquivo não apaga o fato.
        """
        atuais = {p.name: p for p in self.arquivos()}
        for nome, caminho in atuais.items():
            mtime = caminho.stat().st_mtime
            if self._mtimes.get(nome) != mtime:
                self.carregar(caminho, idade)
        for nome in list(self._mtimes):
            if nome not in atuais:
                self.registro.esquecer(nome)
                del self._mtimes[nome]
                self.avisar(f"{nome} saiu da pasta")

    # -- um arquivo ----------------------------------------------------

    def carregar(self, caminho, idade=0.0):
        """Importa um arquivo e registra suas marcas.

        Em erro de importação, a versão anterior **permanece ativa**: o registro
        só é esquecido depois de o módulo novo importar sem exceção. Ficar sem
        rotina por causa de um parêntese seria pior que rodar a versão antiga.
        """
        nome = caminho.name
        primeira_vez = nome not in self._mtimes
        try:
            modulo = self._importar(caminho)
        except Exception as exc:
            self._mtimes[nome] = caminho.stat().st_mtime
            resumo = resumo_do_erro(exc)
            self.historico.setdefault(nome, {})["erro"] = resumo
            self.avisar(f"! {resumo}")
            self.avisar(f"! {nome} não carregou, versão anterior mantida")
            return False

        self.registro.esquecer(nome)
        quantas = self._registrar(modulo, nome, idade)
        self._mtimes[nome] = caminho.stat().st_mtime
        self.historico.setdefault(nome, {})["erro"] = None
        verbo = "carregado" if primeira_vez else "recarregado"
        self.avisar(f"{nome} {verbo}: {quantas} registro(s)")
        return True

    def _importar(self, caminho):
        """Importa por caminho, sem depender de `sys.path`.

        O módulo é removido de `sys.modules` antes, para que a importação seja
        de verdade e não devolva a versão em cache.
        """
        nome_mod = f"vivarium_plugin_{caminho.stem}"
        sys.modules.pop(nome_mod, None)
        spec = importlib.util.spec_from_file_location(nome_mod, caminho)
        modulo = importlib.util.module_from_spec(spec)
        sys.modules[nome_mod] = modulo
        try:
            spec.loader.exec_module(modulo)
        except Exception:
            sys.modules.pop(nome_mod, None)
            raise
        return modulo

    def _registrar(self, modulo, nome, idade):
        """Traduz as marcas de `api` em inscrições no registro."""
        quantas = 0
        for objeto in vars(modulo).values():
            if not callable(objeto):
                continue
            for tipo, dados in api.marcas(objeto):
                if tipo == "cada":
                    self.registro.agendar(objeto, nome, dados["intervalo"],
                                          idade, agora=dados["agora"])
                elif tipo == "quando":
                    self.registro.inscrever(dados["evento"], objeto, nome,
                                            se=dados["se"])
                elif tipo == "acao":
                    self.registro.registrar_acao(
                        Acao(nome=dados["nome"], tecla=dados["tecla"],
                             rotulo=dados["rotulo"], efeito=objeto,
                             emote=dados["emote"], espera=dados["espera"]),
                        nome)
                quantas += 1
        return quantas
