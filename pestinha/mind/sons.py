"""
SONS - quando o pet faz barulho. A voz (body/voz.py) toca; aqui só se decide.

- cutucada: um bip. Carinho: o bip feliz. Batida forte: "batida". Fogos: "fogos". Acordar ou aparecer: "liga".
- emoção nova: bravo, triste, assustado e curioso têm som, cada um com o próprio intervalo mínimo,
  para não virar uma sirene. Entre dois sons desses há sempre um respiro (ESPACO_MINIMO).
- sentado no notebook: um trecho de digitação ("digitando_1", "_2"...), uma pausa, outro trecho...
  Levantou, sumiu da tela ou dormiu: a digitação para na hora.
"""

import random

# emoção -> (som, intervalo mínimo em segundos entre dois iguais)
SOM_DA_EMOCAO = {
    "bravo": ("bravo", 25.0),
    "triste": ("triste", 45.0),
    "assustado": ("susto", 8.0),
    "curioso": ("curioso", 40.0),
}
INTERVALO = {"bip": 0.2, "feliz": 3.0, "batida": 0.8, "fogos": 1.0, "liga": 5.0}
ESPACO_MINIMO = 0.9                  # s entre dois sons de reação
INICIO_DIGITACAO = (0.5, 1.6)        # s depois de sentar até o primeiro trecho
PAUSA_DIGITACAO = (1.5, 6.0)         # s de silêncio entre um trecho e outro
CANAL_DIGITACAO = "digitacao"


class SonsController:
    """Decide os sons a partir do que acontece com o pet; quem toca é a Voz."""

    def __init__(self, voz, rng=None):
        """Começa sem emoção conhecida (a primeira não faz som) e sem digitar."""
        self.voz = voz
        self.rng = rng or random.Random()
        self.digitacao = True
        self._ultimo = {}                # som -> quando tocou
        self._ultimo_qualquer = -1e9
        self._emocao = None
        self._digitando_ate = 0.0
        self._proxima_digitacao = None   # None: não está digitando nem esperando para digitar

    def configurar(self, digitacao):
        """Liga ou desliga o barulho da digitação."""
        self.digitacao = bool(digitacao)
        if not self.digitacao:
            self._parar_digitacao()

    def _tocar(self, nome, now, intervalo=None, respiro=True):
        """Toca `nome` se já passou o intervalo dele (e o respiro entre sons). Devolve True se tocou."""
        intervalo = INTERVALO.get(nome, 0.0) if intervalo is None else intervalo
        if now - self._ultimo.get(nome, -1e9) < intervalo:
            return False
        if respiro and now - self._ultimo_qualquer < ESPACO_MINIMO:
            return False
        if self.voz.tocar(nome) <= 0:
            return False
        self._ultimo[nome] = now
        self._ultimo_qualquer = now
        return True

    # ---------------- eventos ----------------

    def cutucada(self, now):
        """Você cutucou: bip."""
        return self._tocar("bip", now, respiro=False)

    def carinho(self, now):
        """Começou um carinho: o bip feliz."""
        return self._tocar("feliz", now)

    def batida(self, now):
        """Bateu forte em algum lugar."""
        return self._tocar("batida", now, respiro=False)

    def fogos(self, now):
        """Soltou um fogo de artifício."""
        return self._tocar("fogos", now, respiro=False)

    def liga(self, now):
        """Apareceu na tela ou acordou."""
        return self._tocar("liga", now, respiro=False)

    # ---------------- a cada passo da rede ----------------

    def tick(self, now, emocao, sentado, visivel, dormindo):
        """Som da emoção nova e a digitação no notebook. Fora da tela ou dormindo, silêncio."""
        if not visivel or dormindo:
            self._emocao = emocao                # ao voltar, a emoção de agora não conta como nova
            self._parar_digitacao()
            return
        if emocao != self._emocao:
            anterior, self._emocao = self._emocao, emocao
            if anterior is not None and emocao in SOM_DA_EMOCAO:
                nome, intervalo = SOM_DA_EMOCAO[emocao]
                self._tocar(nome, now, intervalo)
        self._digitar(now, sentado)

    def _digitar(self, now, sentado):
        """Sentado (e com a digitação ligada): trechos de digitação com pausas sorteadas no meio."""
        if not (sentado and self.digitacao):
            self._parar_digitacao()
            return
        if self._proxima_digitacao is None:
            self._proxima_digitacao = now + self.rng.uniform(*INICIO_DIGITACAO)
        if now >= self._proxima_digitacao and now >= self._digitando_ate:
            dura = self.voz.tocar_um_de("digitando", canal=CANAL_DIGITACAO)
            self._digitando_ate = now + dura
            self._proxima_digitacao = now + max(dura, 0.5) + self.rng.uniform(*PAUSA_DIGITACAO)

    def _parar_digitacao(self):
        """Para a digitação na hora (levantou, sumiu ou dormiu)."""
        if self._proxima_digitacao is not None or self._digitando_ate:
            self.voz.parar(CANAL_DIGITACAO)
        self._proxima_digitacao = None
        self._digitando_ate = 0.0

    def silenciar(self):
        """Pausa, pânico, esconder ou sair: para tudo."""
        self._parar_digitacao()
        self.voz.parar_tudo()
