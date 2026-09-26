# 06. Roadmap

## Implementado

| Área | Estado |
|------|--------|
| Loop de passo fixo | `Relogio` com `tiques()`, fps por instância, injeção de tempo |
| Animação | `Ritmo` com ciclos em segundos convertidos para quadros |
| Arte | mapa de pixels em meio-bloco, anatomia derivada do mapa |
| Poses | `em pé`, `andando`, `deitado`, com custo de vitais por pose |
| Deslocamento | movimento horizontal, inversão na borda, espelhamento do sprite |
| Grade | buffer de pixels do mundo com estampagem |
| Vitais | vida, fome, tédio, riscos com carência e dano contínuo |
| Render | Rich `Live`, duas cores por célula, descarte de quadro idêntico |
| HUD | corações com meio coração, barras coloridas por faixa, alerta |
| Instrumentação | tick, fps, custo medido por quadro e percentual do orçamento |

## Próximo

### Entrada de teclado

Bloqueia todas as ações do jogador. Requer leitura não bloqueante de `stdin`
em modo raw, ou `curses` restrito à camada de entrada. Decisão pendente.

### Ações

`alimentar`, `acariciar`, `brincar`. Primeira versão embutida, migrada para
plugin na fase de extensão. Escrever a ação duas vezes é deliberado: a versão
embutida revela o que a API precisa expor.

### Partículas

Entidade com posição em float, velocidade, tempo de vida e callback de
colisão. Base para coração, `zZ`, chuva e respingo.

### Personalidade e cérebro

Traços contínuos derivados de seed, e seleção de comportamento por utilidade
com histerese, piso e duração mínima, substituindo o sorteio de pose atual.

### Plugins e recarga a quente

Contrato em [05. API de plugin](05-api-de-plugin.md). Marco da arquitetura:
clima e espécie devem caber em um arquivo de plugin sem alterar `core/`.

### Segunda espécie

Planta, com vitais próprios (`agua`, `luz`), poses próprias e reação distinta
ao clima. Valida a abstração de espécie.

### Persistência

`json` em `$XDG_STATE_HOME/vivarium/pet.json`. Decaimento retroativo a partir
de `last_seen`, com teto de aproximadamente 12 horas.

### Autômato celular de ambiente

Camada de cenário com regra por célula, atualizada em buffer separado. Grama,
poça e propagação.

## Decisões registradas

| Decisão | Escolha | Motivo |
|---------|---------|--------|
| Plataforma | terminal | grade nativa, ciclo de edição curto |
| Dependências | apenas Rich | duas cores por meia célula sem gerência manual de pares |
| Unidade de animação | quadro | discreto, exato, alinhado ao render |
| Unidade de simulação | segundo | independente do fps |
| Fps | por instância | sem global, testável |
| Vida | escala 0..700 | meio coração sem float na apresentação |
| Dano | extremo sustentado | janela de recuperação |
| Estado global | ausente | injeção de dependência em lugar de singleton |

## Questões abertas

* Múltiplos bichos. A grade suporta, a API de plugin assume um.
* Morte permanente e política de save após morte.
* Dimensão do mundo: fixa ou derivada do tamanho do terminal.
* Terceira espécie como teste da abstração.
