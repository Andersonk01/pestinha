#!/usr/bin/env python3
"""
Sintetiza os sons do Pestinha do zero (sem gravação nenhuma, então sem licença de terceiros):

    assets/comum/sons/   a voz padrão, de robozinho: bip, feliz, triste, bravo, susto, curioso, batida,
                         fogos, liga e os trechos de digitação digitando_1..3
    pets/cypher/sons/    a voz do Cypher, digital e glitchada (o que faltar vem do comum)

    python ferramentas/gerar_sons.py

Mono, 16 bits, 24 kHz. A saída é sempre a mesma (semente fixa): rodar de novo reproduz os arquivos.
O volume de verdade é aplicado na hora de tocar (pestinha/body/voz.py); aqui tudo sai perto do máximo,
com a digitação mais baixa que as reações.
"""

import math
import sys
import wave
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
SR = 24000
rng = np.random.default_rng(0x9E571)


def n_of(dur):
    return int(round(dur * SR))


def t_axis(n):
    return np.arange(n) / SR


def decay(n, tau, at=0.0):
    t = t_axis(n) - at
    e = np.exp(-np.maximum(t, 0.0) / tau)
    e[t < 0] = 0.0
    return e


def fade(x, entrada_ms=0.5, saida_ms=3.0):
    k = max(1, n_of(entrada_ms / 1000))
    x[:k] *= np.linspace(0, 1, k)
    k = max(1, n_of(saida_ms / 1000))
    x[-k:] *= np.linspace(1, 0, k)
    return x


def biquad(x, kind, f0, q=0.707):
    """Filtro biquad (RBJ), causal: o ataque continua limpo."""
    w0 = 2 * math.pi * f0 / SR
    c, s = math.cos(w0), math.sin(w0)
    a = s / (2 * q)
    if kind == "lp":
        b0, b1, b2 = (1 - c) / 2, 1 - c, (1 - c) / 2
    elif kind == "hp":
        b0, b1, b2 = (1 + c) / 2, -(1 + c), (1 + c) / 2
    else:  # passa-faixa, 0 dB no pico
        b0, b1, b2 = a, 0.0, -a
    a0, a1, a2 = 1 + a, -2 * c, 1 - a
    b0, b1, b2, a1, a2 = b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0
    out = np.empty(len(x))
    x1 = x2 = y1 = y2 = 0.0
    for i, xi in enumerate(x.tolist()):
        yi = b0 * xi + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        x2, x1, y2, y1 = x1, xi, y1, yi
        out[i] = yi
    return out


def osc(freq, n, forma="sine"):
    f = np.broadcast_to(np.asarray(freq, dtype=float), (n,))
    fase = 2 * np.pi * np.cumsum(f) / SR
    if forma == "sine":
        return np.sin(fase)
    if forma == "square":
        return np.sign(np.sin(fase))
    if forma == "tri":
        return 2 / np.pi * np.arcsin(np.sin(fase))
    raise ValueError(forma)


def place(dst, src, at):
    i = n_of(at)
    j = min(len(dst), i + len(src))
    if j > i:
        dst[i:j] += src[: j - i]


def crush(x, bits):
    q = 2 ** (bits - 1)
    return np.round(x * q) / q


def hold(x, fator):
    return x[(np.arange(len(x)) // fator) * fator]


def norm(x, pico=0.85):
    m = np.max(np.abs(x))
    return x if m == 0 else x * (pico / m)


def gravar(pasta, nome, x):
    pasta.mkdir(parents=True, exist_ok=True)
    pcm = (np.clip(x, -1, 1) * 32767).astype("<i2").tobytes()
    with wave.open(str(pasta / f"{nome}.wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm)


def nota(f, dur, tau, forma="tri", vibrato=0.0, brilho=0.25):
    """Uma notinha de robô: triangular com um pouco de harmônico e vibrato opcional."""
    n = n_of(dur)
    t = t_axis(n)
    f = f * (1 + vibrato * np.sin(2 * np.pi * 9 * t))
    s = osc(f, n, forma) + brilho * osc(f * 2, n) + 0.08 * osc(f * 3, n)
    return fade(s * decay(n, tau), 0.6, 4)


# ---------------- a voz padrão (robozinho) ----------------

def bip():
    x = np.zeros(n_of(0.13))
    place(x, nota(880, 0.05, 0.03), 0.0)
    place(x, nota(1320, 0.07, 0.04), 0.055)
    return norm(biquad(x, "lp", 7000))


def feliz():
    x = np.zeros(n_of(0.5))
    for i, f in enumerate((1047, 1319, 1568, 2093)):          # dó-mi-sol-dó, subindo
        place(x, nota(f, 0.16, 0.07, vibrato=0.01) * (1 - 0.1 * i), 0.065 * i)
    place(x, nota(2093, 0.22, 0.1, vibrato=0.025) * 0.6, 0.27)
    return norm(biquad(x, "lp", 8000))


def triste():
    n = n_of(0.62)
    t = t_axis(n)
    f = 880 * np.exp(-t * 1.25) * (1 + 0.02 * np.sin(2 * np.pi * 5.5 * t))   # escorrega para baixo
    x = (osc(f, n) + 0.3 * osc(f * 2, n, "tri")) * (1 - np.exp(-t / 0.02)) * np.exp(-t / 0.42)
    return norm(fade(biquad(x, "lp", 4000), 2, 40), 0.75)


def bravo():
    x = np.zeros(n_of(0.34))
    for at, f in ((0.0, 190), (0.17, 160)):                   # "brr-brr"
        n = n_of(0.14)
        t = t_axis(n)
        s = osc(f * (1 + 0.04 * np.sin(2 * np.pi * 32 * t)), n, "square")
        place(x, fade(biquad(s, "lp", 1400) * decay(n, 0.09), 1, 8), at)
    return norm(biquad(x, "hp", 90))


def susto():
    n = n_of(0.2)
    t = t_axis(n)
    f = 600 * np.exp(t * math.log(4) / 0.11)                 # sobe duas oitavas, rápido: "uíp!"
    f = np.minimum(f, 2400) * (1 + 0.03 * np.sin(2 * np.pi * 40 * t))
    x = (osc(f, n, "tri") + 0.2 * osc(f * 2, n)) * decay(n, 0.08)
    return norm(fade(x, 0.5, 10))


def curioso():
    n = n_of(0.3)
    t = t_axis(n)
    f = 720 + 120 * np.sin(np.minimum(t / 0.3, 1) * np.pi * 0.5) + 380 * np.maximum(0, (t - 0.18) / 0.12) ** 2
    x = (osc(f, n, "tri") + 0.25 * osc(f * 2, n)) * (1 - np.exp(-t / 0.015)) * np.exp(-t / 0.22)
    return norm(fade(x, 1, 20), 0.8)


def batida():
    n = n_of(0.22)
    t = t_axis(n)
    surdo = osc(95 * (1 + 0.6 * np.exp(-t / 0.01)), n) * decay(n, 0.05)
    ruido = biquad(rng.standard_normal(n), "lp", 900) * decay(n, 0.02)
    tim = osc(2600, n) * decay(n, 0.03, 0.012) * 0.25        # o "tim" da telinha
    return norm(fade(surdo + 0.6 * ruido + tim, 0.3, 20))


def fogos():
    x = np.zeros(n_of(1.0))
    n = n_of(0.36)
    t = t_axis(n)
    apito = osc(1200 * np.exp(t * math.log(2.2) / 0.36), n) * (0.25 + 0.75 * t / 0.36) * 0.45
    place(x, fade(apito, 4, 20), 0.0)
    n = n_of(0.5)
    estouro = biquad(rng.standard_normal(n), "lp", 2200) * decay(n, 0.06)
    estouro += osc(70, n) * decay(n, 0.09)
    place(x, fade(estouro, 0.3, 30), 0.36)
    for _ in range(14):                                      # estalinhos
        k = n_of(0.012)
        estalo = biquad(rng.standard_normal(k), "hp", 3000) * decay(k, 0.003)
        place(x, estalo * rng.uniform(0.2, 0.5), 0.42 + rng.uniform(0, 0.5))
    return norm(x)


def liga():
    x = np.zeros(n_of(0.5))
    for i, f in enumerate((784, 1175, 1568)):
        place(x, nota(f, 0.09, 0.05), 0.05 * i)
    n = n_of(0.25)
    t = t_axis(n)
    blup = osc(520 * (1 + 0.8 * np.exp(-t / 0.03)), n) * decay(n, 0.08) * 0.6
    place(x, blup, 0.16)
    return norm(biquad(x, "lp", 7500))


# ---------------- digitação ----------------

def tecla(click_f, body_f, thock_f, bottom_at, dur=0.07):
    """Uma tecla de notebook: clique, corpo e o fundo batendo (mais leve que a mecânica da intro)."""
    n = n_of(dur)
    t = t_axis(n)
    clique = biquad(rng.standard_normal(n), "bp", click_f, 1.3) * decay(n, 0.0010)
    corpo = biquad(rng.standard_normal(n), "bp", body_f, 0.9) * decay(n, 0.0040)
    thock = osc(thock_f * (1 + 0.5 * np.exp(-t / 0.004)), n) * decay(n, 0.007)
    fundo = biquad(rng.standard_normal(n), "bp", click_f * 1.2, 1.6) * decay(n, 0.0007, bottom_at)
    x = clique + 0.45 * corpo + 0.35 * thock + 0.3 * fundo
    return fade(norm(biquad(x, "hp", 120), 1.0), 0.3, 2)


def espaco():
    return tecla(2600, 900, 210, 0.03, dur=0.11) * 0.95


TECLAS = None


def digitando(duracao, enter=False):
    """Um trecho de digitação: palavras de 2 a 7 teclas, espaço entre elas, às vezes um enter no fim."""
    global TECLAS
    if TECLAS is None:
        TECLAS = [tecla(*a) for a in ((4300, 1900, 320, 0.022), (4900, 2200, 350, 0.019),
                                      (3900, 1700, 300, 0.026), (5300, 2400, 370, 0.020),
                                      (4600, 2000, 335, 0.024))]
    x = np.zeros(n_of(duracao + 0.3))
    pos = 0.02
    while pos < duracao - 0.25:
        for _ in range(int(rng.integers(2, 8))):
            k = TECLAS[int(rng.integers(len(TECLAS)))]
            place(x, k * rng.uniform(0.55, 1.0), pos)
            pos += rng.uniform(0.075, 0.16)
        place(x, espaco() * rng.uniform(0.6, 0.85), pos)
        pos += rng.uniform(0.16, 0.34)
        if rng.random() < 0.12:
            pos += rng.uniform(0.3, 0.7)                     # pensou um pouquinho
    if enter:
        place(x, espaco() * 1.0, pos + 0.08)
        pos += 0.25
    return norm(x[: n_of(pos + 0.12)], 0.6)


# ---------------- a voz do Cypher (digital, glitchada) ----------------

def bloco(f, dur, bits=6):
    n = n_of(dur)
    s = osc(f, n, "square") * 0.6 + osc(f * 2.01, n) * 0.2
    return fade(crush(s * decay(n, dur * 0.6), bits), 0.6, 2)


def cypher_bip():
    x = np.zeros(n_of(0.09))
    place(x, bloco(1568, 0.025), 0.0)
    place(x, bloco(2093, 0.035), 0.03)
    return norm(biquad(x, "lp", 6500))


def cypher_feliz():
    """Um "access granted" curtinho: mi-lá-mi, subindo."""
    x = np.zeros(n_of(0.55))
    for f, at, dur in ((1318.5, 0.0, 0.07), (1760, 0.06, 0.07), (2637, 0.12, 0.3)):
        n = n_of(dur)
        s = osc(f, n) + 0.3 * osc(f * 2, n, "tri")
        place(x, fade(crush(s * decay(n, dur * 0.5), 8), 0.6, 6), at)
    eco = x.copy()
    place(eco, x * 0.3, 0.1)
    return norm(biquad(eco, "lp", 8000))


def cypher_glitch(segmentos=((0.0, 0.06), (0.07, 0.11), (0.12, 0.16))):
    x = np.zeros(n_of(segmentos[-1][1] + 0.01))
    for a, b in segmentos:
        k = n_of(b - a)
        passo = n_of(0.008)
        f = np.repeat(rng.uniform(90, 720, size=k // passo + 1), passo)[:k]
        s = osc(f, k, "square") * 0.6 + rng.standard_normal(k) * 0.35
        s = crush(hold(s, int(rng.integers(3, 9))), 4)
        place(x, fade(s * rng.uniform(0.6, 1.0), 1, 1), a)
    return norm(biquad(biquad(x, "hp", 140), "lp", 8000))


def cypher_liga():
    x = np.zeros(n_of(0.7))
    place(x, cypher_glitch() * 0.7, 0.0)
    for i, f in enumerate((2349, 2637, 3136, 3951)):
        n = n_of(0.3)
        place(x, fade((osc(f, n) + 0.2 * osc(f * 2, n)) * decay(n, 0.06) * (1 - 0.15 * i), 0.6, 10),
              0.2 + 0.045 * i)
    return norm(biquad(x, "lp", 9000))


def cypher_triste():
    x = np.zeros(n_of(0.75))
    for i, f in enumerate((784, 740, 698, 587)):             # desce em degraus, como um 8 bits
        dur = 0.15 if i < 3 else 0.32
        place(x, bloco(f, dur, 5) * (1 - 0.1 * i), 0.17 * i)
    return norm(biquad(x, "lp", 3500), 0.75)


def cypher_curioso():
    x = np.zeros(n_of(0.32))
    pos = 0.0
    freqs = (1175, 1397, 1568, 1760, 2093, 2349)
    while pos < 0.26:
        dur = rng.uniform(0.012, 0.03)
        place(x, bloco(float(rng.choice(freqs)), dur) * rng.uniform(0.4, 1.0), pos)
        pos += dur + rng.uniform(0.005, 0.025)
    place(x, bloco(2637, 0.05), pos)                         # termina subindo: "?"
    return norm(biquad(x, "lp", 7000), 0.8)


def cypher_susto():
    n = n_of(0.16)
    t = t_axis(n)
    f = 500 * np.exp(t * math.log(5) / 0.12)
    s = crush(hold(osc(np.minimum(f, 2500), n, "square"), 3), 5) * decay(n, 0.07)
    return norm(fade(biquad(s, "lp", 7000), 0.5, 8))


def main():
    comum = RAIZ / "assets" / "comum" / "sons"
    for nome, fazer in (("bip", bip), ("feliz", feliz), ("triste", triste), ("bravo", bravo),
                        ("susto", susto), ("curioso", curioso), ("batida", batida), ("fogos", fogos),
                        ("liga", liga)):
        gravar(comum, nome, fazer())
    for i, (duracao, enter) in enumerate(((2.2, False), (3.0, True), (2.6, False)), 1):
        gravar(comum, f"digitando_{i}", digitando(duracao, enter))
    cypher = RAIZ / "pets" / "cypher" / "sons"
    for nome, fazer in (("bip", cypher_bip), ("feliz", cypher_feliz), ("liga", cypher_liga),
                        ("bravo", cypher_glitch), ("triste", cypher_triste), ("curioso", cypher_curioso),
                        ("susto", cypher_susto)):
        gravar(cypher, nome, fazer())
    print(f"sons gravados em {comum.relative_to(RAIZ)} e {cypher.relative_to(RAIZ)}", file=sys.stderr)


if __name__ == "__main__":
    main()
