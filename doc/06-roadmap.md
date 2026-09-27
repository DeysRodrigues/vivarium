# 06. Roadmap

O alvo é o de [01](01-requisitos.md): um bicho com vida própria, cuidado por
código que a jogadora escreve. As fases estão na ordem em que se destravam — cada
uma depende da anterior, e essa dependência é o que faltava na versão anterior
deste documento.

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
| Entrada | `termios` em cbreak, `select` sem bloquear, degrada fora de tty |
| Ações | `alimentar`, `carinho`, `brincar`, com espera por ação e emote de reação |
| Instrumentação | tick, fps, custo por quadro, idade e contagem de plugins |
| Registro | handlers por evento, esquecer por módulo, isolar e desativar ao falhar |
| API pública | `vivarium/api.py`: `cada`, `quando`, `acao`, `log` |
| Carregador | varredura da pasta, importação por caminho, recarga por `mtime` |
| Painel de log | 5 linhas, erro em vermelho, erro de plugin em uma linha |
| Idade | acumulada na sessão, é o relógio contra o qual `@cada` agenda |

O bicho existe, é olhável, e **é programável**: um `.py` em `plugins/` já muda o
comportamento dele sem reiniciar.

O que falta para fechar o alvo de [01](01-requisitos.md) é a memória — hoje a
idade zera ao fechar o terminal, então `@cada(horas=4)` nunca chega perto de
disparar.

## Fase 1 — Persistência

Contrato em [08](08-persistencia.md). Primeira porque tudo depois dela depende de
a idade acumular entre sessões.

* `json` atômico em `$XDG_STATE_HOME/vivarium/pet.json`, com `"versao"`.
* Três relógios separados: quadro (`monotonic`), idade (acumulada, salva) e
  parede (`time.time`, só para medir ausência).
* Save ao sair e a cada 60 s.
* Save ausente ou corrompido gera bicho novo, com aviso.
* `teto_ausencia = 0` por padrão: volta como estava.

**Pronto quando:** fechar o terminal e reabrir devolve o mesmo bicho, com a idade
maior, e um `json` legível a olho.

## Fase 2 — API, carregador e recarga · **feita**

Contrato em [05](05-api-de-plugin.md). O critério era: o plugin de exemplo roda
sem alterar `core/`. Roda.

Entregue: `api.py` com `cada`, `quando`, `acao` e `log`; registro que esquece por
módulo, isola exceção e desativa o handler até o arquivo mudar; carregador com
recarga por `mtime`; agendador por idade com disparo único; eventos `tique`,
`fome_vazia`, `tedio_cheio`, `dormiu`, `acordou`, `morreu`; painel de log com o
erro resumido em uma linha; ação de plugin ganhando tecla no rodapé.

Ficou de fora, e volta nas fases que o habilitam: `mundo` como parâmetro (Fases 7
e 9), `emitir()` de evento próprio, `@comportamento` (Fase 6), `@especie`
(Fase 8), `@automato` (Fase 9), e o console na tecla `:`.

## Fase 3 — Painel de abertura

Depende da Fase 1: sem save não há o que mostrar.

* Idade do bicho e os plugins escritos até aqui, com execuções acumuladas e
  último erro.
* Plugin que saiu da pasta aparece como histórico, não como erro.

**Pronto quando:** abrir mostra "4h 07m de vida" e a lista do que já foi escrito.

## Fase 4 — Console

Tecla `:` com `pet` em escopo, `eval` e `exec` em `SyntaxError`, mesmo isolamento
dos handlers. É o caminho mais curto entre uma dúvida de Python e a resposta.

## Fase 5 — Balanceamento e morte

Dois furos conhecidos, que só valem consertar depois de a API existir, porque a
API muda os números.

**Risco de tédio nunca dispara.** `andando` tem tédio negativo e é sorteado com
peso igual às outras poses. Medido em 30 minutos de simulação: o risco
`entediado` não dispara uma vez. A auto-regulação funciona demais e metade do
sistema de risco não executa. A correção real é a Fase 6: com escolha por
utilidade, o bicho só anda quando o tédio justifica.

**Morte não é estado.** `Vitais.atualizar` para de decair quando morto, mas
`Gato.atualizar` não consulta isso: o bicho morto continua trocando de pose e
andando. As ações já são ignoradas nesse caso (`Acoes.executar`), falta o mesmo no
tick, e falta decidir a política de save depois da morte.

## Fase 6 — Personalidade e cérebro

* Traços contínuos `0..1` derivados de seed, modulando decaimento e escolha.
* Seleção por utilidade com histerese, piso e duração mínima, substituindo o
  `random.choice` de pose.
* `@comportamento` passa a valer: o plugin pontua opções em vez de forçar poses.

## Fase 7 — Partículas

Entidade com posição em float, velocidade, tempo de vida e callback de colisão.
Base para coração, `zZ`, chuva e respingo. Habilita `soltar()` e `particula()` na
API.

## Fase 8 — Segunda espécie

Planta, com vitais próprios (`agua`, `luz`), poses próprias e reação distinta ao
clima. Valida `@especie` e a abstração de espécie.

## Fase 9 — Ambiente

Ciclo dia/noite com hora própria do mundo, clima como estado global, e autômato
celular de cenário em buffer separado (grama, poça, propagação). Habilita
`@automato`.

## Fora da fila

* **Testes.** `doc/07` descreve a estratégia e `tests/` está vazio. Não é fase, é
  débito: cada fase acima entra com os seus.
* **Bench.** Os números de [01](01-requisitos.md) não têm script que os
  reproduza. Número afirmado tem que ser reproduzível.
* **`render/hud.py` importa de `pet/`.** Viola a regra de camada do
  [03](03-arquitetura.md), cujo próprio comando de verificação falha hoje.
* **`LICENSE`.** O README declara MIT e o arquivo não existe.

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
| Entrada | `termios` em cbreak | tecla sem tomar a tela do `Live`, e Ctrl+C intacto |
| Repetir ação | espera por ação | sem ela, segurar a tecla anula o modelo de vitais |
| Onde o bicho vive | só com o terminal aberto | sem daemon, sem IPC, sem unit de systemd |
| Agendamento | por idade do bicho | parede nunca dispararia sem daemon |
| Ausência | teto 0 por padrão | volta como estava; o teto é um número no config |
| Save | `json` com versão | inspecionável, e `pickle` quebra ao renomear classe |
| Nomes da API | português | igual ao resto do código |
| Decorador | marca a função, não registra | sem registro global; dois jogos no mesmo processo |
| Handler que falha | desativado até salvar | senão o mesmo erro sai 5x por segundo |
| Resumo de erro | `arquivo:linha Tipo: msg` | `format_exc` lê o disco já alterado pela recarga |
| Erro de importação | mantém versão anterior | sem rotina por causa de um parêntese é pior |
| Eventos do pet | devolvidos, não disparados | `pet/` não conhece o registro |
| Sandbox de plugin | ausente | é código da própria jogadora; isolar erro, não malícia |

## Questões abertas

* Múltiplos bichos. A grade suporta, a API assume um.
* Política de save depois da morte.
* Dimensão do mundo: fixa ou derivada do tamanho do terminal.
* Como o plugin declara config própria (uma constante no módulo? um dict?).
* Se `@cada` deve aceitar hora de parede como opção explícita, para quem quiser.
