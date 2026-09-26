# Documentação

Vivarium é um bichinho virtual de terminal escrito em Python, com o mundo
renderizado em meio-blocos Unicode e um loop de simulação de passo fixo.

## Índice

| Doc | Conteúdo |
|-----|----------|
| [01. Requisitos](01-requisitos.md) | Escopo funcional e não funcional, e o que ficou fora |
| [02. Stack](02-tecnologias.md) | Dependências, o motivo de cada uma e as alternativas descartadas |
| [03. Arquitetura](03-arquitetura.md) | Camadas, regra de dependência, módulos e fluxo de um quadro |
| [04. Simulação](04-simulacao.md) | Modelo de tempo, ritmos, poses, vitais e regras de dano |
| [05. API de plugin](05-api-de-plugin.md) | Extensão em tempo de execução (projetado, não implementado) |
| [06. Roadmap](06-roadmap.md) | Estado atual e fases seguintes |
| [07. Testes](07-testes.md) | Estratégia de teste e pontos de injeção |

## Princípio de projeto

O núcleo não conhece domínio. `core/` expõe tempo, ritmo, grade de pixels e
stats; `pet/` e `render/` constroem o jogo em cima disso. Qualquer
comportamento novo que exija alterar `core/` indica um vazamento de camada.

## Convenções

* Durações de animação em **quadros** (inteiro, exato, alinhado ao render).
* Durações de simulação em **segundos** (float, multiplicadas por `relogio.dt`).
* Cores por nome, resolvidas apenas em `render/paleta.py`.
* Mapas de pixel usam `.` transparente, `#` corpo, `o` detalhe.
