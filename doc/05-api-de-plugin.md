# 05. API de plugin

> **Status: implementado**, menos o que está marcado *previsto* nas tabelas.
> `vivarium/api.py` é a superfície, `vivarium/carregador.py` descobre e recarrega,
> `vivarium/core/registro.py` guarda e dispara.
>
> Falta a persistência ([08](08-persistencia.md)): hoje a idade zera ao fechar, e
> o histórico de plugins vive só na sessão.

## O que é

A superfície onde a jogadora escreve código. O bicho tem vida própria sem
nenhum plugin; o plugin é a **rotina** em volta dele — o que acontece a cada
tantas horas, o que fazer quando a fome esvazia, que espécie nova existe.

Um plugin é um arquivo `.py` em `$XDG_CONFIG_HOME/vivarium/plugins/`. Salvar o
arquivo aplica o efeito ao bicho em execução, sem reiniciar e sem perder estado.

## Exemplo completo

```python
# plugins/minha_rotina.py
from vivarium.api import cada, quando, acao, log

@cada(horas=4)
def cafe(pet):
    pet.alimentar(30)
    log("servi o café")

@cada(minutos=20)
def carinho_periodico(pet):
    if pet.tedio > 50:
        pet.acariciar()

@quando("fome_vazia")
def emergencia(pet):
    pet.alimentar(50)
    log("socorro, ele tava sem comer")

@acao("banho", tecla="h", rotulo="dar banho", espera=60.0)
def banho(pet):
    pet.tedio -= 30
    pet.reagir("~~")
```

Nada aqui importa de `core/`, `pet/` ou `render/`. É o critério de aceitação da
arquitetura: se este arquivo precisa alcançar um módulo interno, falta API.

## Superfície

### Decoradores

| Decorador | Efeito |
|-----------|--------|
| `@cada(horas=, minutos=, segundos=, agora=False)` | roda a cada tanto de **idade do bicho** |
| `@quando(evento, se=None)` | roda em um evento (`tique`, `fome_vazia`, `dormiu`, `acordou`, `morreu`) |
| `@acao(nome, tecla=, rotulo=, espera=)` | ação manual, exposta no rodapé |
| `@comportamento(nome)` | *previsto* — comportamento pontuável pelo cérebro |
| `@especie(nome)` | *previsto* — espécie com vitais e arte próprios |
| `@automato(camada, cada=)` | *previsto* — autômato celular sobre uma camada |

`@cada` conta **idade**, não hora de parede — o bicho não vive com o terminal
fechado, então parede nunca dispararia. Detalhes em
[08](08-persistencia.md#os-três-relógios).

`agora=True` dispara também na primeira vez que o plugin é visto, em vez de
esperar o primeiro intervalo. Serve para testar o que se acabou de escrever sem
esperar quatro horas.

### Funções

| Função | Efeito |
|--------|--------|
| `log(texto)` | escreve no painel de log. Linha começando com `!` sai em vermelho |
| `emitir(evento, **dados)` | *previsto* — dispara evento próprio |
| `soltar(entidade)` | *previsto* — insere entidade no mundo |
| `particula(char, ...)` | *previsto* — partícula com posição, velocidade e vida |

### `pet`

| Membro | O que é |
|--------|---------|
| `.alimentar(quanto=30)`, `.acariciar()`, `.brincar()` | as ações, chamáveis por código |
| `.vida`, `.fome`, `.tedio` | leitura e escrita direta, com limites aplicados |
| `.idade` | segundos de vida acumulados |
| `.especie`, `.pose`, `.x` | identidade e estado |
| `.reagir(emote, segundos=1.6)` | emote temporário |
| `.idade` | segundos de vida (hoje só da sessão, até a Fase 1) |
| `.traits`, `.cerebro` | *previsto* |

Uma ação é definida **uma vez** e alcançável por dois caminhos: `pet.alimentar()`
no plugin e a tecla `a` na mão. O teclado é atalho, não uma segunda
implementação.

### `mundo`

> *Previsto.* Hoje o handler recebe só `pet`. O `mundo` entra quando houver
> partículas e clima para ele carregar (Fases 7 e 9).

| Membro | O que é |
|--------|---------|
| `.memoria` | dicionário livre que sobrevive à recarga e ao save |
| `.grade`, `.chao` | canvas e referência de piso |
| `.entidades` | partículas e afins |
| `.clima`, `.hora` | previsto |
| `.rand_x()` | coluna aleatória dentro do mundo |

## Invariantes

### 1. O núcleo nunca importa um plugin

O carregador varre a pasta e importa; os decoradores se registram. A dependência
tem sentido único. Um `import` de plugin dentro de `core/` inverteria isso e é o
primeiro sinal de que a arquitetura cedeu.

### 2. Estado não reside no plugin

Módulo recarregado perde globais. Estado compartilhado vive em `mundo.memoria`,
que é salvo junto com o bicho.

```python
contador = 0                        # zera a cada recarga
mundo.memoria["pingos"] += 1        # sobrevive à recarga e ao fechar
```

### 3. O registro esquece por módulo

Antes de reimportar, o registro remove tudo associado àquele `__module__`. Sem
isso, cada salvamento duplica os handlers e o efeito se multiplica sem erro
visível — dois cafés, depois quatro, e nada na tela dizendo por quê.

### 4. Exceção de plugin não derruba o processo

Todo handler executa sob `try/except Exception`. O erro vai para o painel de log
em uma linha, e o handler é **desativado até o arquivo mudar**. Sem desativar, um
handler de `tique` que quebra reporta o mesmo erro cinco vezes por segundo e o
painel fica ilegível.

O erro é resumido em `arquivo:linha Tipo: mensagem`, e **não** com
`traceback.format_exc()`. O formatador lê o arquivo do disco no momento de
formatar, e com recarga a quente o arquivo já mudou: o traceback sai apontando a
linha nova com o erro antigo, que é pior que não mostrar linha nenhuma.

Isto é requisito do objetivo de treinar Python: errar tem que ser barato.

```
! exemplo.py.refeicao: exemplo.py:12 AttributeError: 'Gato' object has no attribute 'fomee'
! desativado até você salvar o arquivo
```

### 5. Um agendamento vencido dispara uma vez

Se `@cada(horas=4)` venceu três vezes durante uma ausência longa, roda uma. Três
cafés de uma vez é bug, não recuperação.

## Recarga

`os.stat` de `mtime` sobre os arquivos da pasta, uma verificação por segundo e
não por quadro. Arquivo novo é detectado; arquivo apagado é esquecido do registro.

O registro só é esquecido **depois** de o módulo novo importar sem exceção. Então
erro de sintaxe deixa a versão anterior ativa, em vez de deixar o bicho sem rotina
por causa de um parêntese.

A pasta é `./plugins` quando existe (para o repositório clonado já achar os
exemplos), senão `$XDG_CONFIG_HOME/vivarium/plugins`.

### Por que os decoradores só marcam

`@cada` e `@quando` anexam um atributo à função em vez de registrá-la na hora. O
carregador varre o módulo depois de importar e registra o que estiver marcado.

É o que permite não ter registro global: um arquivo de plugin não precisa saber
qual jogo vai carregá-lo, e o mesmo arquivo pode ser carregado por dois jogos no
mesmo processo — o que é exatamente o que um teste faz.

## Histórico

Cada inscrição conta as próprias execuções e guarda o último erro. Hoje isso vive
só na sessão; a Fase 1 ([08](08-persistencia.md)) leva para o save, com primeira
vez visto e execuções acumuladas, e é o que a abertura vai mostrar.

Plugin apagado da pasta sai do registro mas continuará no histórico: o registro é
do que já foi escrito, e apagar o arquivo não apaga o fato de ter escrito.

## Console

> *Previsto.* Tecla `:` abre uma linha de entrada com `mundo` e `pet` em escopo. Avalia com
`eval`, e com `exec` em caso de `SyntaxError`. Mesmo isolamento de exceção dos
handlers. É o caminho mais curto entre uma dúvida de Python e a resposta.

## O que não é

Não há sandbox de segurança. O plugin é código da própria jogadora, importado com
os privilégios dela. O isolamento existente é contra **erro**, não contra
código malicioso, e tratar como se fosse as duas coisas daria falsa garantia.

## Estabilidade

O que está neste documento é contrato. `core/`, `pet/` e `render/` são internos e
podem mudar de forma. Um plugin que precise importar de `core/` indica lacuna na
API: a correção é estender a API, não importar direto.
