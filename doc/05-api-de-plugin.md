# 05. API de plugin

> **Status: projetado, não implementado.** Este documento define o contrato
> alvo. Nada em `vivarium/` implementa isto ainda.

## Objetivo

Permitir adicionar ações, clima, comportamentos e espécies em arquivos
separados, aplicados ao processo em execução sem reiniciar e sem perder o
estado do bicho.

## Forma

Um plugin declara por decorador. O carregador varre `plugins/`, importa cada
arquivo e os decoradores se registram. O núcleo nunca importa um plugin: a
dependência tem sentido único.

```python
# plugins/chuva.py
from vivarium.api import action, on, spawn, particle, log

@action("chuva", key="k", label="fazer chover")
def chover(mundo, pet):
    mundo.clima.definir("chuva", duracao=30)

@on("tick", when="clima == chuva")
def pingos(mundo, pet, dt):
    for _ in range(3):
        spawn(particle(char="│", cor="azul", x=mundo.rand_x(), y=0,
                       vy=18, vida=2.0))

@on("tick", when="clima == chuva")
def reacao(mundo, pet, dt):
    if pet.especie == "planta":
        pet.vitais.agua.add(4 * dt)
    elif pet.especie == "gato":
        pet.brain.quer("esconder", peso=0.9)
```

O critério de aceitação da arquitetura é que este arquivo funcione sem
alteração em `core/`.

## Superfície

### Decoradores

| Decorador | Efeito |
|-----------|--------|
| `@action(nome, key=, label=)` | ação de teclado, exposta no rodapé |
| `@on(evento, when=)` | handler de evento (`tick`, `fome_vazia`, `dormiu`) |
| `@behavior(nome)` | comportamento pontuável pelo cérebro |
| `@automaton(camada, cada=)` | regra de autômato celular sobre uma camada |
| `@species(nome)` | espécie com vitais e arte próprios |

### Funções

| Função | Efeito |
|--------|--------|
| `spawn(entidade)` | insere entidade no mundo |
| `particle(char, ...)` | constrói partícula com posição, velocidade e tempo de vida |
| `log(texto)` | escreve no painel de log |
| `emit(evento, **dados)` | dispara evento próprio |

### Objetos recebidos

| Objeto | Superfície |
|--------|-----------|
| `mundo` | `.grade`, `.clima`, `.hora`, `.chao`, `.entidades`, `.memoria`, `.rand_x()` |
| `pet` | `.vitais`, `.traits`, `.especie`, `.x`, `.y`, `.brain`, `.emote()` |
| `dt` | segundos desde o último tick, apenas em handlers de `tick` |

## Invariantes

### 1. Estado não reside no plugin

Módulo recarregado perde globais. Estado compartilhado vive em
`mundo.memoria`, um dicionário livre exposto para esse fim.

```python
contador = 0                        # zera a cada recarga
mundo.memoria["pingos"] += 1        # sobrevive
```

### 2. O registro esquece por módulo

Antes de reimportar, o registro remove tudo associado àquele `__module__`.
Sem isso, cada salvamento duplica handlers e o efeito se multiplica sem erro
visível.

### 3. Exceção de plugin não derruba o processo

Todo handler executa sob `try/except Exception`. O traceback vai para o painel
de log e o handler é desativado até a próxima alteração do arquivo.

## Recarga

Detecção por `os.stat` de `mtime`, uma verificação por segundo sobre os
arquivos de `plugins/`. Arquivos novos são detectados. Erro de sintaxe é
registrado e a versão anterior permanece ativa.

## Console

Tecla `:` abre uma linha de entrada com `mundo` e `pet` em escopo. Avalia com
`eval`, e com `exec` em caso de `SyntaxError`. Mesmo isolamento de exceção do
sandbox.

## Estabilidade

O que está neste documento é contrato. `core/`, `pet/` e `render/` são
internos. Um plugin que precise importar de `core/` indica lacuna na API: a
correção é estender a API, não importar diretamente.
