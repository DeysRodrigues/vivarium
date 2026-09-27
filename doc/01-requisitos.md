# 01. Requisitos

## O que é

Um bicho de terminal que se cuida sozinho até certo ponto, e que o resto do
cuidado é código que o jogador escreve.

O bicho tem vida própria: respira, pisca, anda, dorme, tem fome e tédio, e
nenhum desses movimentos é comandado — cada um tem relógio próprio e o
comportamento emerge do custo de cada pose. O que o jogador programa é a
**rotina** em volta disso: o que acontece a cada tantas horas de convivência, o
que fazer quando a fome esvazia, que espécie nova existe, como o clima age.

```python
# plugins/minha_rotina.py
from vivarium.api import cada, quando, log

@cada(horas=4)
def cafe(pet):
    pet.alimentar(30)
    log("servi o café")

@quando("fome_vazia")
def emergencia(pet):
    pet.alimentar(50)
    log("socorro")
```

Isso é o produto, não um extra. O jogo é o par bicho + código do jogador.

## Os dois objetivos

Declarados porque decidem empates de projeto:

1. **Ter um bicho divertido com vida própria.** Ele precisa ser interessante de
   olhar mesmo sem nenhum plugin escrito.
2. **Ser um lugar para treinar Python sempre.** A API é a superfície onde se
   escreve código de verdade, em sessões curtas, sem montar projeto novo.

Consequências do objetivo 2, que não seriam óbvias sem ele:

* Erro de plugin é mensagem didática no painel de log, com traceback, e nunca
  derruba o processo. Errar tem que ser barato.
* Recarga a quente: salvar o arquivo mostra o efeito no bicho vivo. O ciclo
  escrever-ver precisa ser de segundos.
* A API é pequena e nomeada em português, igual ao resto do código.
* Um plugin escrito hoje continua valendo depois, e o jogo mostra o que já foi
  escrito. O histórico é parte do jogo.

## Sessão

O bicho vive **enquanto o terminal está aberto**. Fechar o terminal encerra o
processo; não há daemon nem serviço em background.

Ao abrir de novo, ele volta como estava: vitais, posição, pose, idade, esperas
e agendamentos saem do save. A abertura mostra o que já existe — idade do bicho
e os plugins escritos até aqui, com quantas vezes cada um rodou.

Tempo ausente **não** conta por padrão (`teto_ausencia = 0`). Volta como estava.
A mecânica de decaimento retroativo existe e é um número no config, para quem
quiser que a ausência pese.

## Requisitos funcionais

### Bicho

| Item | Especificação |
|------|---------------|
| Vida | 7 corações. Internamente `0..700` para permitir meio coração em inteiro |
| Fome | `0..100`. Cheia significa alimentado, vazia significa faminto |
| Tédio | `0..100`. Cheio significa entediado |
| Idade | segundos de vida acumulados entre todas as sessões. Salva |
| Poses | `em pé`, `andando`, `deitado`. Cada uma define custo de vitais e conjunto de ritmos |
| Espécies | Gato implementado. Planta prevista, com vitais próprios (`agua`, `luz`) |
| Personalidade | Previsto: vetor de traços contínuos, não enumeração |

### Simulação

* Loop de passo fixo, um tick por quadro, taxa configurável por instância.
* Animação composta por ritmos independentes, cada um com relógio próprio e
  intervalos não harmônicos entre si.
* Vitais decaem em função da pose ativa.
* Dano por extremo sustentado com carência, nunca por transição instantânea.

### API de plugin

Detalhada em [05](05-api-de-plugin.md). Requisitos de nível:

* Diretório de plugins varrido na abertura e recarregado a quente por `mtime`.
* Registro por decorador. O núcleo nunca importa um plugin.
* Agendamento por **idade do bicho**, não por hora de parede: `@cada(horas=4)`
  são 4 horas de convivência, somadas entre sessões.
* Exceção de plugin isolada por handler, com traceback no painel de log.
* Estado compartilhado em `mundo.memoria`, que sobrevive à recarga.
* Histórico de plugins persistido: nome, primeira vez visto, execuções, último
  erro.

### Persistência

Detalhada em [08](08-persistencia.md). Requisitos de nível:

* `json` inspecionável em `$XDG_STATE_HOME/vivarium/pet.json`, com versão de
  esquema.
* Save ao sair e periodicamente, para que um `kill -9` custe pouco.
* Save ausente ou corrompido gera bicho novo, com aviso, sem travar.
* Plugin desaparecido não invalida o save.

### Interação manual

Teclado é atalho, não a interface principal. Uma ação é definida uma vez e
alcançável por dois caminhos: `pet.alimentar()` no plugin e a tecla `a` na mão.

### Renderização

* Grade de pixels convertida em células de terminal a dois pixels por célula.
* Duas cores por célula via caractere de meio-bloco (frente e fundo).
* HUD com corações e barras coloridas por faixa.
* Painel de log, onde plugin e jogo escrevem.
* Escrita no terminal apenas quando o quadro muda.

## Requisitos não funcionais

| Requisito | Alvo | Medido |
|-----------|------|--------|
| Custo de CPU por quadro | < 5% do orçamento | 0,73% a 5 fps |
| Tráfego para o terminal | irrelevante | 7,8 KB/s a 5 fps |
| Memória residente do estado | < 100 KB | 1,8 KB |
| Startup | < 500 ms | ~165 ms |
| Dependências de runtime | mínimas | 1 (Rich) |
| Recarga de plugin | imperceptível | não medido |
| Tamanho do save | inspecionável a olho | não medido |

As linhas medidas são de antes da API de plugin e precisam ser refeitas. Não há
script de bench no repositório, o que é uma lacuna: número afirmado tem que ser
reproduzível.

## Fora de escopo

Daemon ou serviço em background. Rede e multiplayer. Áudio. Janela gráfica no
compositor. Reprodução. Múltiplos bichos simultâneos. Economia de itens.
Sandbox de segurança do plugin: o plugin é código da própria jogadora e roda com
os privilégios dela.
