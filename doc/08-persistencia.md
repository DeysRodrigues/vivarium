# 08. Persistência

> **Status: projetado, não implementado.** Nada em `vivarium/` grava arquivo
> ainda.

## Por que é a primeira fase

O bicho vive só enquanto o terminal está aberto. Sem save, cada sessão começa do
zero: a idade não acumula, o agendamento por idade não tem como contar, e o
histórico de plugins não existe. Metade do que a API de plugin promete depende
deste arquivo.

## Os três relógios

O projeto passa a ter três noções de tempo, e confundi-las é a fonte de bug mais
provável desta fase.

| Relógio | Fonte | Para quê | Sobrevive ao fechar |
|---------|-------|----------|---------------------|
| quadro | `Relogio`, `time.monotonic` | animação e ritmos | não |
| idade | acumulador em segundos | agendamento e maturidade | sim, no save |
| parede | `time.time` | medir a ausência entre sessões | sim, no save |

`Relogio` continua com `monotonic` e isso está certo: dentro da sessão, imune a
ajuste de relógio do sistema. Mas `monotonic` zera no boot, então **não serve**
para medir tempo entre execuções. O `last_seen` usa `time.time`, que é a única
coisa no projeto que o usa.

`idade` é o relógio que o jogador programa contra:

```python
@cada(horas=4)           # 4 horas de convivência, somadas entre sessões
```

Não é hora de parede. Como o bicho não vive com o terminal fechado, `@cada` em
parede nunca dispararia — ninguém deixa o terminal aberto quatro horas seguidas.
Contra a idade, as 4 horas se acumulam ao longo de dias e o disparo acontece.

Efeito colateral bom: agendamento fica determinístico. Um relógio falso avança a
idade em milissegundos e o teste verifica o disparo sem esperar.

## Local

```
$XDG_STATE_HOME/vivarium/pet.json      (default: ~/.local/state/vivarium/)
$XDG_CONFIG_HOME/vivarium/plugins/*.py (default: ~/.config/vivarium/)
```

Estado em `STATE` e não em `CONFIG` porque é dado gerado, não configuração.
Plugin em `CONFIG` porque é escrito à mão e o jogador vai querer versionar.

`json` e não `pickle`: `pickle` quebra ao renomear uma classe e o save tem que
ser abrível num editor. Ver um save à mão é parte do valor didático.

## Formato

```json
{
  "versao": 1,
  "last_seen": 1759000000.0,
  "pet": {
    "especie": "gato",
    "idade": 14822.4,
    "vida": 700.0,
    "fome": 62.1,
    "tedio": 18.0,
    "x": 21.4,
    "direcao": 1,
    "pose": "em pé",
    "sofrendo_ha": {"faminto": 0.0, "entediado": 0.0}
  },
  "esperas": {"alimentar": 3.2},
  "agendamentos": {"minha_rotina.cafe": 28800.0},
  "memoria": {"pingos": 114},
  "plugins": {
    "minha_rotina.py": {
      "visto_em": 1758900000.0,
      "execucoes": 37,
      "ultimo_erro": null
    }
  }
}
```

### O que fica de fora, e por quê

| Não salvo | Motivo |
|-----------|--------|
| passo e restante dos ritmos | ninguém percebe uma piscada reiniciada |
| emote temporário | dura 1,6 s |
| tick do relógio | é contador de sessão |
| mapa de pixels | derivado da arte |

A regra: salvar o que é decisão acumulada, não o que é quadro em andamento.

## Abertura

```
1. ler pet.json           ausente ou inválido -> bicho novo, com aviso no log
2. migrar esquema         versao < atual -> migração por passo
3. aplicar ausência       agora - last_seen, limitado por teto_ausencia
4. carregar plugins       registrar, e comparar com o histórico do save
5. painel de abertura     idade, e os plugins escritos até aqui
```

### Ausência

```python
ausente = min(agora - last_seen, teto_ausencia)
```

`teto_ausencia = 0` por padrão: o bicho volta exatamente como estava. É a
escolha declarada do projeto — voltar depois de uma semana e encontrar um bicho
morto não é o jogo que se quer.

O teto é um número no config, não uma decisão de código. Quem quiser que a
ausência pese põe `teto_ausencia = 7200` e a ausência passa a valer até duas
horas. A mecânica é a mesma; muda o número.

Com o teto acima de zero, a ausência **não** avança quadro nem ritmo. Ela
aplica: decaimento de vitais pelo tempo ausente na pose salva, avanço da idade,
e os agendamentos que venceram nesse intervalo — cada um dispara **uma vez**,
por mais que tenha vencido dez, porque dez cafés de uma vez é bug e não recuperação.

### Painel de abertura

É o que responde "mostre os plugins que eu já fiz":

```
vivarium · gato · 4h 07m de vida

  minha_rotina.py      2 rotinas    37 execuções
  chuva.py             1 evento      8 execuções
  planta.py            1 espécie     —          erro na última vez

  [enter] continuar
```

Plugin que existe no save mas não está mais na pasta aparece como histórico, não
como erro: o save é o registro do que já foi escrito, e apagar o arquivo não
apaga o fato.

## Gravação

Ao sair, e a cada 60 s de jogo. O intervalo existe para que `kill -9` ou fechar
a aba custe no máximo um minuto.

Gravação atômica: escreve `pet.json.tmp` e `os.replace`. `os.replace` é atômico
no mesmo sistema de arquivos, então uma queda no meio da escrita deixa o save
anterior intacto em vez de um json truncado.

## Versão de esquema

`"versao": 1` existe desde o primeiro save, antes de haver qualquer migração. O
campo é barato agora e impossível de adicionar retroativamente depois — sem ele,
o primeiro save antigo que não abrir mais vira dado perdido sem como saber o que
era.

Migração é uma função por passo (`_de_1_para_2`), aplicada em sequência. Save de
versão maior que a suportada é recusado e preservado: é jogo de uma pessoa, e
apagar o bicho dela por causa de um downgrade não é aceitável.

## Pontos de teste

| Caso | Verificar |
|------|-----------|
| ida e volta | salvar e carregar devolve os mesmos vitais, pose e idade |
| save ausente | bicho novo, sem exceção |
| json truncado | bicho novo, aviso no log, save anterior não é sobrescrito antes de gravar |
| versão futura | recusa e preserva |
| ausência com teto 0 | nada muda |
| ausência com teto | decai o mínimo entre real e teto |
| agendamento vencido 10x | dispara uma vez |
| plugin removido | histórico permanece, sem erro |

Tudo isso é verificável com `tmp_path` do pytest e um relógio falso, sem terminal
e sem espera real.
