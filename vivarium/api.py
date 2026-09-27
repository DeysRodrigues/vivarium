"""A superfície que um plugin importa. Nada mais é público.

    from vivarium.api import cada, quando, acao, log

Os decoradores **marcam** a função em vez de registrá-la na hora. O carregador
varre o módulo depois de importar e registra o que estiver marcado. É o que
permite não ter registro global: um `@cada` num arquivo não precisa saber qual
jogo vai carregá-lo, e o mesmo arquivo pode ser carregado por dois jogos no
mesmo processo.

`core/`, `pet/` e `render/` são internos. Um plugin que precise importar de lá
indica lacuna aqui: a correção é estender esta API, não importar direto.
"""

from collections import deque

MARCA = "_vivarium"

# Buffer de log. É o único estado de módulo da API, e existe porque `log()` é
# chamado em tempo de execução por código que não recebe o painel como
# parâmetro. `deque` com teto: um plugin em laço não consome memória.
_LINHAS = deque(maxlen=200)


def _marcar(fn, tipo, dados):
    """Anexa uma marca à função. Várias marcas na mesma função são somadas."""
    marcas = getattr(fn, MARCA, None)
    if marcas is None:
        marcas = []
        setattr(fn, MARCA, marcas)
    marcas.append((tipo, dados))
    return fn


def cada(horas=0, minutos=0, segundos=0, agora=False):
    """Roda a cada tanto de **idade do bicho**, somada entre sessões.

        @cada(horas=4)
        def cafe(pet):
            pet.alimentar(30)

    Não é hora de parede: o bicho não vive com o terminal fechado, então parede
    nunca dispararia. `agora=True` dispara também na primeira vez que o plugin
    é visto, em vez de esperar o primeiro intervalo — serve para testar o que
    você acabou de escrever sem esperar quatro horas.
    """
    intervalo = horas * 3600 + minutos * 60 + segundos
    if intervalo <= 0:
        raise ValueError("@cada precisa de um intervalo maior que zero")
    return lambda fn: _marcar(fn, "cada", {"intervalo": intervalo,
                                           "agora": agora})


def quando(evento, se=None):
    """Roda em um evento.

        @quando("fome_vazia")
        def emergencia(pet):
            pet.alimentar(50)

    Eventos: `tique`, `fome_vazia`, `tedio_cheio`, `dormiu`, `acordou`,
    `morreu`, e qualquer um que você mesmo disparar com `emitir()`.

    `se` é um filtro que recebe os mesmos argumentos do handler e devolve bool.
    """
    return lambda fn: _marcar(fn, "quando", {"evento": evento, "se": se})


def acao(nome, tecla="", rotulo="", espera=0.0, emote=""):
    """Ação manual, exposta no rodapé e ligada a uma tecla.

        @acao("banho", tecla="h", rotulo="dar banho", espera=60.0)
        def banho(pet):
            pet.tedio -= 30
    """
    return lambda fn: _marcar(fn, "acao", {
        "nome": nome, "tecla": tecla, "rotulo": rotulo or nome,
        "espera": espera, "emote": emote})


def log(texto):
    """Escreve no painel de log."""
    _LINHAS.append(str(texto))


def linhas_de_log(quantas=None):
    """Últimas linhas escritas. Usado pelo painel; plugin não precisa disso."""
    todas = list(_LINHAS)
    return todas if quantas is None else todas[-quantas:]


def limpar_log():
    _LINHAS.clear()


def marcas(fn):
    """Marcas de uma função, ou lista vazia. Usado pelo carregador."""
    return list(getattr(fn, MARCA, ()))
