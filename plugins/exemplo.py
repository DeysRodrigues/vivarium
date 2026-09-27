"""Plugin de exemplo. Copie, mude, salve — o efeito aparece sem reiniciar.

Só `vivarium.api` é público. `core/`, `pet/` e `render/` são internos.
"""

from vivarium.api import acao, cada, quando, log


@cada(minutos=3)
def refeicao(pet):
    """Roda a cada 3 minutos de idade do bicho, somados entre sessões."""
    if pet.fome < 70:
        pet.alimentar(30)
        log(f"servi comida, fome agora {pet.fome:.0f}")


@cada(segundos=30)
def cafune_periodico(pet):
    if pet.tedio > 50:
        pet.acariciar()
        log("cafuné de rotina")


@quando("fome_vazia")
def emergencia(pet):
    pet.alimentar(50)
    log("! ele tava sem comer, corri com a ração")


@quando("dormiu")
def boa_noite(pet):
    log(f"dormiu com {pet.fome:.0f} de fome")


@acao("banho", tecla="h", rotulo="banho", espera=45.0, emote="~~")
def banho(pet):
    pet.tedio -= 30
    log("banho dado")
