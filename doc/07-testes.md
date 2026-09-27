# 07. Testes

## Ferramenta

`pytest`. Testes em `tests/`, fora do pacote, espelhando os nomes dos módulos.
Configuração em `pytest.ini`.

```bash
pytest -q          # suíte
pytest -x --lf     # para no primeiro erro, só os que falharam
pytest -k clock    # por nome
```

```
sudo pacman -S --needed python-pytest
```

Dependência de desenvolvimento, não de runtime.

## Estratégia

O projeto foi construído para ser testável sem terminal e sem espera real.
Três propriedades sustentam isso:

1. **Tempo injetado.** `Relogio(agora=..., dormir=...)` aceita substitutos.
   Minutos de simulação rodam em milissegundos.
2. **Tempo em quadros.** Ritmos avançam por `atualizar()`, sem consultar
   relógio. Determinístico dado o estado inicial.
3. **`pet/` não renderiza.** `Gato.mapa()` devolve pixels. Toda a simulação é
   verificável sem alocar terminal.

## Cobertura por módulo

| Módulo | Prioridade | Alvo |
|--------|-----------|------|
| `core/relogio.py` | alta | conversão de segundos para quadros, cadência, recuperação de atraso |
| `core/ritmo.py` | alta | sequência do ciclo, sorteio de faixa, repetição |
| `core/stat.py` | alta | clamp nos extremos, `pct`, `vazio`, `cheio` |
| `core/grade.py` | alta | índices, estampagem, transparência, fora de limites |
| `core/mapa.py` | alta | validação de paridade e largura |
| `pet/vitais.py` | alta | decaimento por pose, carência, acúmulo de riscos |
| `pet/corpo.py` | média | composição por pose, preenchimento até o chão, espelhamento |
| `pet/gato.py` | média | inversão na borda, troca de pose |
| `render/pixels.py` | média | mapeamento de par de pixels para caractere e estilo |
| `render/hud.py` | média | meio coração, faixas de cor |
| `render/tela.py` | baixa | descarte de quadro idêntico |
| `render/paleta.py` | nenhuma | tabela sem lógica |
| `app.py` | nenhuma | integração, verificada executando |
| `core/teclado.py` | média | degradação fora de tty, descarte do buffer |
| `pet/acoes.py` | alta | espera por ação, tecla sem ação, bicho morto |
| persistência | alta | ida e volta, save corrompido, ausência, migração ([08](08-persistencia.md#pontos-de-teste)) |
| API e carregador | alta | registro, esquecer por módulo, isolamento de exceção, disparo único |

## Padrões de teste

### Tempo

```python
class TempoFalso:
    def __init__(self): self.t = 0.0
    def agora(self): return self.t
    def dormir(self, s): self.t += s

relogio = Relogio(fps=5, agora=falso.agora, dormir=falso.dormir)
```

### Duração independente de fps

```python
assert Relogio(fps=5).quadros(1.4) == 7
assert Relogio(fps=20).quadros(1.4) == 28
```

Propriedade a garantir: a duração real de um ciclo não muda com o fps.

### Vitais

Avance por `dt`, nunca por `sleep`.

```python
for _ in range(60 * 5):            # 60 s a 5 fps
    vitais.atualizar(poses.EM_PE)
```

Carência exige um par de testes. Um sozinho não define a regra:

```python
def test_fome_vazia_por_muito_tempo_tira_vida(): ...
def test_fome_vazia_por_pouco_tempo_nao_tira_vida(): ...
```

### Aleatoriedade

`random.seed` fixo. Preferir asserção sobre relação e faixa a valor absoluto:
constantes de balanceamento mudam, a relação não.

### Render

Dublê no lugar do terminal. Testar a lógica de composição e de descarte, não
a saída do Rich.

```python
console = Console(file=io.StringIO(), force_terminal=True, width=60)
```

### Camadas

```python
def test_core_e_pet_nao_conhecem_render():
    saida = subprocess.run(["grep", "-rn", "vivarium.render",
                            "vivarium/core", "vivarium/pet"],
                           capture_output=True, text=True)
    assert saida.stdout == ""
```

### Plugin

O plugin é testável sem pasta e sem recarga: o carregador aceita um caminho
injetado (`tmp_path`), e o registro é um objeto, não um global. Um plugin de teste
é um arquivo escrito em `tmp_path` no próprio teste.

Os dois casos que um teste sozinho não cobre, e que precisam de par:

```python
def test_recarregar_nao_duplica_handler(): ...
def test_recarregar_aplica_a_versao_nova(): ...
```

O primeiro sem o segundo passa com um carregador que simplesmente não recarrega.

## Fora de alvo

Cobertura total, saída do Rich, comportamento do terminal, e asserção sobre
valores de balanceamento.
