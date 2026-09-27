# Documentação

Vivarium é um bicho de terminal com vida própria, cuidado por código que a
jogadora escreve. O bicho é interessante de olhar sem nenhum plugin; o plugin é a
rotina em volta dele.

Escrito em Python, com o mundo renderizado em meio-blocos Unicode e um loop de
simulação de passo fixo.

## Índice

| Doc | Conteúdo |
|-----|----------|
| [01. Requisitos](01-requisitos.md) | O que é, os dois objetivos, escopo e o que ficou fora |
| [02. Stack](02-tecnologias.md) | Dependências, o motivo de cada uma e as alternativas descartadas |
| [03. Arquitetura](03-arquitetura.md) | Camadas, regra de dependência, módulos e fluxo de um quadro |
| [04. Simulação](04-simulacao.md) | Modelo de tempo, ritmos, poses, vitais e regras de dano |
| [05. API de plugin](05-api-de-plugin.md) | A superfície onde se escreve código |
| [06. Roadmap](06-roadmap.md) | Estado atual e as fases, na ordem em que se destravam |
| [07. Testes](07-testes.md) | Estratégia de teste e pontos de injeção |
| [08. Persistência](08-persistencia.md) | Save, os três relógios e a ausência (projetado) |
| [Ideias](ideias.md) | Backlog de intenção: o que ainda não é fase |

Comece por [01](01-requisitos.md) para o que o projeto é, e por
[06](06-roadmap.md) para o que está feito.

## Princípio de projeto

O núcleo não conhece domínio. `core/` expõe tempo, ritmo, grade de pixels, stats e
teclado; `pet/` e `render/` constroem o jogo em cima disso. Qualquer comportamento
novo que exija alterar `core/` indica um vazamento de camada.

A camada de cima é `api.py`: a única superfície que um plugin importa. Um plugin
que precise alcançar `core/` indica lacuna na API, e a correção é estender a API.

## Convenções

* Durações de animação em **quadros** (inteiro, exato, alinhado ao render).
* Durações de simulação em **segundos** (float, multiplicadas por `relogio.dt`).
* Agendamento de plugin em **idade do bicho**, não em hora de parede.
* Cores por nome, resolvidas apenas em `render/paleta.py`.
* Mapas de pixel usam `.` transparente, `#` corpo, `o` detalhe.
* Nomes em português, incluindo a API pública.

## Estado dos documentos

| Doc | Descreve código que existe? |
|-----|------------------------------|
| 01, 02, 03, 04, 05, 06 | sim, com as partes previstas marcadas |
| 08 | não. Contrato alvo, marcado no topo |
| 07 | estratégia escrita, `tests/` vazio |
