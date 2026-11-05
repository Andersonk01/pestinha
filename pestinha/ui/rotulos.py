"""
RÓTULOS - os nomes que aparecem na tela, no idioma do pet.

Os nomes internos da rede (MOTION, TYPING, FOCUS...) ficam no código como estão.
Aqui fica só o nome que o usuário vê, no monitor neural e nos textos (traduzido por nome_canal).
"""
from ..idioma import N_, tr

CANAIS_SENSORIAIS = {
    "MOTION": N_("movimento"),
    "TYPING": N_("digitação"),
    "NOVELTY": N_("novidade"),
    "SILENCE": N_("silêncio"),
    "WORK": N_("trabalho"),
    "PLAY": N_("jogo"),
    "SOUND": N_("música"),
    "SOCIAL": N_("social"),
    "WEB": N_("navegador"),
    "FATIGUE": N_("cansaço"),
    "POKE": N_("cutucada"),
    "DRAG": N_("arraste"),
    "DISMISS": N_("dispensa"),
    "LONELY": N_("solidão"),
    "CARESS": N_("carinho"),
    "THROW": N_("arremesso"),
    "IMPACT": N_("batida"),
    "ANTICIPATE": N_("antecipação"),
    "TOY_NEAR": N_("bolinha perto"),
    "TOY_TAKEN": N_("bolinha levada"),
    "BOREDOM": N_("tédio"),
    "PEDIDO": N_("pedido de trabalho"),
    "PRESO": N_("preso no canto"),
    "LEMBRA_FUGA": N_("lembra de fugas"),
    "RECUSA": N_("recusou pedido"),
    "PLACA": N_("placa do castigo"),
    "ANTECIPA_PLACA": N_("antecipa o canto"),
    "VISITA": N_("visita no canto"),
    "RECEIO": N_("receio de fugir"),
    "RANCOR": N_("rancor"),
}

INTERNEURONIOS = {
    "ALERT": N_("alerta"),
    "FOCUS": N_("foco"),
    "CURIOUS": N_("curiosidade"),
    "PLAYFUL": N_("brincadeira"),
    "CALM": N_("calma"),
    "TIRED": N_("cansaço"),
    "QUIET": N_("quietude"),
    "INHIB": N_("inibição"),
    "FRUSTRATION": N_("frustração"),
    "GLOOM": N_("desânimo"),
}

MOTORES = {
    "STARTLE": N_("susto"),
    "WATCH": N_("observar"),
    "WANDER": N_("passear"),
    "CHEER": N_("alegria"),
    "SETTLE": N_("sossego"),
    "DROWSE": N_("sonolência"),
    "ANGRY": N_("raiva"),
    "SAD": N_("tristeza"),
    "SENTAR": N_("sentar no notebook"),
    "FUGIR": N_("fugir do canto"),
    "CARTAZ": N_("colar cartaz"),
    "CANTO": N_("ir para o cantinho"),
    "TRAVESSURA": N_("aprontar"),
    "PAPEL": N_("atirar papel"),
    "ACEITAR": N_("aceitar o castigo"),
}

GRUPOS = {"sensory": N_("sentido"), "inter": N_("interneurônio"), "motor": N_("motor")}


def nome_canal(nome):
    """Nome de exibição de qualquer população da rede."""
    rotulo = CANAIS_SENSORIAIS.get(nome) or INTERNEURONIOS.get(nome) or MOTORES.get(nome)
    return tr(rotulo) if rotulo else nome.lower()
