"""Buffer de pixels do mundo."""


class Grade:
    """Grade de pixels onde todos os elementos do mundo são desenhados.

    É o único canvas: bicho, partículas e cenário escrevem aqui, e apenas a
    camada `render` traduz o resultado para o terminal.
    """

    VAZIO = "."

    def __init__(self, largura, altura):
        self.largura = largura
        self.altura = altura
        self.limpar()

    def limpar(self):
        self._celulas = [[self.VAZIO] * self.largura for _ in range(self.altura)]

    def dentro(self, x, y):
        return 0 <= x < self.largura and 0 <= y < self.altura

    def pintar(self, x, y, pixel):
        """Escreve um pixel. Coordenada fora da grade é ignorada.

        Ignorar em vez de levantar exceção é intencional: partícula saindo da
        tela é situação normal e quem desenha não deve verificar limites.
        """
        if self.dentro(x, y):
            self._celulas[y][x] = pixel

    def estampa(self, mapa, x=0, y=0):
        """Sobrepõe um mapa de pixels em (x, y). `VAZIO` é transparente."""
        for dy, linha in enumerate(mapa):
            for dx, pixel in enumerate(linha):
                if pixel != self.VAZIO:
                    self.pintar(x + dx, y + dy, pixel)

    # Alias mantido para compatibilidade com chamadas existentes.
    estampar = estampa

    def linhas(self):
        return ["".join(linha) for linha in self._celulas]
