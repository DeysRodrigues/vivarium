# Ideias

Backlog de intenção, não de tarefa. O que entra aqui é ideia com o **motivo** e o
**que ela exige**, para não virar lista de desejo solta. Quando uma ideia vira
fase com critério de pronto, ela sai daqui e entra no [06](06-roadmap.md).

---

## 1. Decorar o viveiro

Poder colocar plantas, pedras, vasos, brinquedos no espaço do bicho — e poder
fazer isso por plugin, igual ao resto.

```python
# plugins/minha_decoracao.py
from vivarium.api import decorar

@decorar(x=4, y="chao")
def samambaia():
    return """
    ..##..
    .####.
    ..##..
    ..oo..
    """
```

**Por quê:** é o que transforma "um bicho numa faixa vazia" em lugar. E é o
segundo tipo de plugin, o que testa se a API aguenta mais de uma forma de
extensão — hoje todos os decoradores registram comportamento, nenhum registra
conteúdo.

**O que exige:**

* Camada de cenário na `Grade`, desenhada antes do bicho. Hoje a grade é um
  buffer único limpo a cada quadro; decoração fixa não precisa ser reestampada
  toda vez, então vale um buffer de fundo separado.
* Ordem de desenho explícita (fundo, decoração, bicho, partículas, HUD, log).
  Hoje a ordem está implícita na sequência de chamadas de `app.quadro()`.
* Carregar mapa de pixels de dentro de um plugin — `core/mapa.carregar()` já faz
  o parse e valida paridade, mas não é público. É uma entrada em `api.py`.
* Decidir se decoração ocupa espaço (o bicho desvia) ou é só visual. Visual é
  muito mais barato e provavelmente suficiente na primeira versão.
* Decidir se a decoração é dado no plugin (como acima) ou arquivo de arte
  separado que o plugin aponta.

**Depende de:** viveiro definido (ideia 3) — sem saber onde é o chão e onde é a
parede, não há onde ancorar um vaso.

---

## 2. Abrir os plugins com uma tecla

Uma tecla (`p`, ou `e` de editar) abre `$EDITOR` na pasta de plugins. Ao sair do
editor, o jogo recarrega e volta.

**Por quê:** é o objetivo de treinar Python levado a sério. Hoje o ciclo é
alt-tab até o editor, e o atrito é justamente onde a prática morre. Com a recarga
a quente já funcionando, isso fecha o laço escrever-ver dentro do próprio jogo.

**O que exige:**

* Suspender o `Live` do Rich e restaurar o terminal ao estado normal antes de
  entregar o controle ao editor — o editor precisa do terminal inteiro, em modo
  canônico.
* Restaurar `termios` na volta: o `Teclado` já guarda o estado anterior em
  `__exit__`, então provavelmente é sair e reentrar no context manager.
* `subprocess.call` e não `os.system`, e respeitar `$EDITOR` com fallback.
* O `Relogio` vai ver um atraso enorme ao voltar. Ele já reancora no instante
  atual em vez de recuperar o acúmulo, então isso deve funcionar de graça —
  **verificar**, não assumir.
* Decidir se abre a pasta ou um arquivo. Abrir a pasta serve mais, mas nem todo
  editor lida bem com isso.
* Variante mais simples e talvez melhor: a tecla só *cria* um plugin novo a
  partir de um template e abre esse arquivo. Resolve o pior atrito, que é começar.

---

## 3. Viveiro bem definido

Hoje o mundo é uma faixa de 48×16 pixels sem moldura, sem chão visível, sem
fundo. O bicho anda num vazio e a borda só existe como número em
`Gato._andar()`.

**Por quê:** "vivarium" é o nome do projeto e o viveiro não existe. Além do
visual, isso destrava a decoração (ideia 1) e as partículas (Fase 7): as duas
precisam de um chão para assentar e de uma parede para colidir.

**O que exige, e o que decidir:**

* Chão desenhado, não só implícito. `arte.CHAO` já é a referência do corpo;
  falta ele existir como pixel.
* Moldura, ou não. Uma borda em meio-bloco custa duas linhas e dá muito.
* Fundo: cor de célula ou padrão. Cuidado com o custo — fundo cheio em toda
  célula aumenta o tráfego ao terminal, e o descarte de quadro idêntico só ajuda
  se o fundo não animar.
* Dimensão: fixa (hoje, 48 colunas) ou derivada do tamanho do terminal. A
  questão já está aberta no [06](06-roadmap.md). Derivar é mais bonito e cria o
  problema de redimensionar em tempo de execução.
* Camadas nomeadas na `Grade` em vez de um buffer só, se a decoração entrar.

---

## 4. Idade por segundo, e o que a idade significa

A idade hoje é um float de segundos que só aparece no rodapé de depuração e
serve de relógio para `@cada`. Falta ela **significar** algo.

**Por quê:** um bicho que envelhece é um bicho com história. E é a diferença
entre `@cada(horas=4)` ser um timer e ser "uma vez por dia da vida dele".

**O que decidir:**

* A escala. Quantos segundos reais são um "dia" de vida do bicho? Uma escala
  explícita (`SEGUNDOS_POR_DIA = 600`, por exemplo) deixa `@cada(dias=1)`
  possível e legível.
* Estágios: filhote, adulto, velho. Cada um podendo mudar arte, custo de vitais e
  peso das poses — o que encaixa direto no cérebro por utilidade (Fase 6).
* Se a idade aparece para a jogadora fora do modo de depuração. "3d 4h de vida"
  no HUD é informação de jogo, não instrumentação.
* Se existe fim. A questão de morte permanente já está aberta no
  [06](06-roadmap.md), e idade a torna mais urgente.

**Depende de:** persistência (Fase 1). Idade que zera ao fechar não envelhece
nada.

---

## 5. Melhorar a doc geral

A doc é o ponto forte do projeto e já tem dívida acumulada:

* **`doc/07-testes.md` descreve uma estratégia e `tests/` está vazio.** É a maior
  incoerência entre doc e código hoje.
* **Números sem bench.** `doc/01` afirma 1457 µs por quadro, 7,8 KB/s e ~165 ms
  de startup, e não há script que reproduza. Número afirmado tem que ser
  reproduzível — ou some, ou ganha um `bench/`. Os números também são de antes da
  API de plugin, então estão velhos de qualquer forma.
* **`render/hud.py` importa de `pet/`.** Viola a regra de camada do
  [03](03-arquitetura.md), cujo próprio comando de verificação falha. Ou conserta
  o código, ou a regra escrita está mentindo.
* **Falta `LICENSE`.** O README declara MIT com badge e o arquivo não existe.
* **`doc/02` afirma `slots` em `Stat` e `Pose`.** Nenhum dos dois usa.
* **`Grade.estampa` tem alias `estampar`** "para compatibilidade", e nada chama
  `estampa`. Um nome a mais sem motivo.
* **`core/mapa.py` valida com `assert`,** que desaparece sob `python -O`.
* Um `doc/09-arte.md` faria falta: as restrições de meio-bloco (paridade, detalhe
  em linha par) estão espalhadas entre `04` e o docstring de `arte.py`, e quem
  for desenhar uma planta vai precisar delas num lugar só.

---

## 6. Renomear os arquivos para inglês

Hoje o código é bilíngue: mensagens de commit em inglês, nomes de arquivo, de
classe e de função em português.

**Por quê:** consistência, e porque o projeto é portfólio — quem abre o
repositório lê inglês primeiro.

**O que exige, e a decisão difícil:**

Renomear arquivo é `git mv` e um dia de `sed`. A pergunta de verdade é **até onde
vai**, e são três níveis independentes:

| Nível | Exemplo | Custo |
|-------|---------|-------|
| 1. Arquivos e pastas | `relogio.py` → `clock.py`, `pet/` → `creature/` | baixo |
| 2. Classes e funções internas | `Relogio` → `Clock`, `atualizar()` → `update()` | médio, mecânico |
| 3. API pública | `@cada` → `@every`, `pet.alimentar()` → `pet.feed()` | quebra todo plugin escrito |

O nível 3 contradiz uma decisão já registrada no [06](06-roadmap.md) ("Nomes da
API: português, igual ao resto do código") e é o único que tem custo real: um
plugin escrito hoje para de funcionar. Se for para mudar, é **antes** de haver
plugin que valha a pena manter — ou seja, quanto mais cedo, mais barato.

Meio-termo possível: inglês em tudo, e a API aceitando os dois nomes por um
tempo, com aviso no log. Custa um dicionário de alias e evita quebrar o que já
foi escrito.

**Sugestão:** decidir os três níveis de uma vez e fazer num commit só por nível,
sem misturar com mudança de comportamento — renomeação misturada com feature é
diff impossível de revisar.

---

## Ordem sugerida

Nenhuma destas é fase ainda. Se fossem, a ordem que faz sentido é:

1. **Renomear (ideia 6)**, se for renomear, porque cada dia que passa custa mais.
2. **Persistência** (Fase 1 do [06](06-roadmap.md)), que já está na fila e
   destrava a idade.
3. **Viveiro definido (ideia 3)**, porque decoração e partículas dependem dele.
4. **Decoração (ideia 1)**, que valida a API num segundo tipo de extensão.
5. **Abrir plugin com tecla (ideia 2)**, barato e de retorno alto.
6. **Idade com significado (ideia 4)**.
7. **Dívida de doc (ideia 5)**, continuamente, não como fase.
