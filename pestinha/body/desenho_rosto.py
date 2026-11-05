"""
DESENHO DO ROSTO - só o que se desenha do pet: moldura, olhos, brilho, acessórios, efeitos de tela e os Zzz.

Não tem estado nem decisão: recebe a forma dos olhos, a direção do olhar e a aparência do pet
(cores, acessórios e efeitos, de pets/<pet>.json e do estilo escolhido) e pinta. Os acessórios são
uma camada por cima (o capuz, por trás) do rosto: não mudam os olhos nem as expressões. Os efeitos
(chuva de código, scanlines, glitch) ficam dentro da tela e andam com o relógio `agora`.
"""

import math
import re
from dataclasses import dataclass, field

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainterPath, QPen, QPolygonF

from ..ajustes import ZZZ_PERIODO as ZZZ_PERIOD, ZZZ_QUANTIDADE as ZZZ_COUNT

BODY_W, BODY_H = 120, 90
FRAME = QColor("#63e56f")
SHELL = QColor("#101512")
SCREEN = QColor("#171e19")
EYE = QColor("#3ee877")
SHINE = QColor("#c8ffd8")

# ordem em que aparecem no pets/<pet>.json; a ordem do desenho fica em draw_face
ACESSORIOS = ("capuz", "fones", "oculos", "gravata")
COR_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
COR_PADRAO_ACESSORIO = {"capuz": "#26324a", "fones": "moldura", "oculos": "#e8e8e8", "gravata": "#b3261e"}
# um acessório pode ter a cor de uma parte do corpo: assim ele acompanha o estilo escolhido
CORES_DO_CORPO = ("moldura", "olho", "brilho")
EFEITOS = ("chuva", "scanlines", "glitch")

TELA = QRectF(-BODY_W / 2 + 11, -BODY_H / 2 + 11, BODY_W - 22, BODY_H - 22)
RAIO_TELA = 12
GLITCH_A, GLITCH_B = QColor("#FF2BD6"), QColor("#00E5FF")    # as cores do glitch da intro do Ryoku
SIMBOLOS_CHUVA = "01<>/{}[]#$%&*+=;:ABCDEF"


@dataclass(frozen=True)
class Aparencia:
    """Cores do corpo, acessórios e efeitos de um pet. O padrão é o visual original (o do pet)."""
    moldura: QColor = field(default_factory=lambda: QColor(FRAME))
    casca: QColor = field(default_factory=lambda: QColor(SHELL))
    tela: QColor = field(default_factory=lambda: QColor(SCREEN))
    olho: QColor = field(default_factory=lambda: QColor(EYE))
    brilho: QColor = field(default_factory=lambda: QColor(SHINE))
    acessorios: tuple = ()             # ((nome, QColor ou "moldura"/"olho"/"brilho"), ...)
    efeitos: frozenset = frozenset()   # de EFEITOS
    codigo: QColor = None              # cor da chuva de código; sem ela, a do olho


CAMPOS_DE_COR = ("moldura", "casca", "tela", "olho", "brilho")


def _cor_valida(valor):
    return isinstance(valor, str) and bool(COR_HEX.match(valor))


def aparencia_de(dados):
    """
    Monta a Aparencia a partir do "aparencia" do pet.json. Cor fora do formato #rrggbb, acessório
    e efeito desconhecidos são ignorados (ficam com o padrão), como os outros campos do pet.
    """
    if not isinstance(dados, dict):
        return Aparencia()
    cores = {k: QColor(dados[k]) for k in CAMPOS_DE_COR if _cor_valida(dados.get(k))}
    pedidos = dados.get("acessorios")
    acessorios = []
    if isinstance(pedidos, dict):
        for nome in ACESSORIOS:
            if nome in pedidos:
                cor = pedidos[nome]
                if not (_cor_valida(cor) or cor in CORES_DO_CORPO):
                    cor = COR_PADRAO_ACESSORIO[nome]
                acessorios.append((nome, cor if cor in CORES_DO_CORPO else QColor(cor)))
    efeitos = dados.get("efeitos")
    efeitos = frozenset(e for e in efeitos if e in EFEITOS) if isinstance(efeitos, list) else frozenset()
    codigo = QColor(dados["codigo"]) if _cor_valida(dados.get("codigo")) else None
    return Aparencia(**cores, acessorios=tuple(acessorios), efeitos=efeitos, codigo=codigo)


PADRAO = Aparencia()


def cor_do_acessorio(a, cor):
    """A cor de verdade: a própria, ou a da parte do corpo que ele acompanha."""
    return QColor(getattr(a, cor)) if isinstance(cor, str) else cor


def lerp_shape(current, target, k):
    """Interpola duas formas de olho: `k` entre 0 (atual) e 1 (alvo), para a transição ser suave."""
    return {key: current[key] + (target[key] - current[key]) * k for key in target}


def glitch_ativo(agora):
    """O glitch pisca duas vezes a cada ~5 s, rapidinho (como o da intro)."""
    t = agora % 5.3
    return t < 0.09 or 0.22 < t < 0.27


def draw_face(p, shape, gaze=(0.0, 0.0), blink=1.0, emotion="observando", carinho=False, aparencia=PADRAO,
              agora=0.0):
    """Desenha (capuz +) moldura + tela + efeitos + olhos (+ acessórios) com centro na origem do painter."""
    a = aparencia
    acessorios = [(nome, cor_do_acessorio(a, cor)) for nome, cor in a.acessorios]
    for nome, cor in acessorios:
        if nome == "capuz":                            # por trás do corpo: o rosto fica "dentro" dele
            _capuz(p, cor)
    p.setPen(QPen(a.moldura, 5))
    p.setBrush(a.casca)
    p.drawRoundedRect(QRectF(-BODY_W / 2, -BODY_H / 2, BODY_W, BODY_H), 20, 20)
    p.setPen(Qt.NoPen)
    p.setBrush(a.tela)
    p.drawRoundedRect(TELA, RAIO_TELA, RAIO_TELA)
    if "chuva" in a.efeitos:
        _chuva(p, a, agora)
    for nome, cor in acessorios:
        if nome == "capuz":
            _cordinhas(p, cor)                         # as cordinhas caem na frente, na faixa abaixo da tela
        if nome == "gravata":                          # por cima da tela, sempre dentro do contorno do corpo
            _gravata(p, cor)

    if carinho:
        # carinho: olhinhos fechados de felicidade, em arco para cima (^ ^)
        p.setPen(QPen(a.olho, 5, Qt.SolidLine, Qt.RoundCap))
        p.setBrush(Qt.NoBrush)
        for side in (-1, 1):
            cx, cy = side * 24, shape["dy"]
            p.drawArc(QRectF(cx - 15, cy - 8, 30, 22), 0, 180 * 16)
        p.setPen(Qt.NoPen)
    else:
        if "glitch" in a.efeitos and glitch_ativo(agora):
            _glitch(p, shape, gaze, blink, emotion, a, agora)
        _olhos(p, shape, gaze, blink, emotion, a)
    if "scanlines" in a.efeitos:
        _scanlines(p)
    for nome, cor in acessorios:
        if nome == "fones":
            _fones(p, cor)
    for nome, cor in acessorios:
        if nome == "oculos":
            _oculos(p, cor)


def _olhos(p, shape, gaze, blink, emotion, a, cor=None, dx=0.0, brilho=True):
    """Desenha os dois olhos: forma, piscada, brilho e direção do olhar (`cor`/`dx`: cópias do glitch)."""
    gx, gy = gaze
    for side in (-1, 1):
        w = shape["w"]
        h = shape["h"] * blink
        if emotion == "curioso" and side == 1:
            h *= 1.15
        h = max(h, 3.0)
        cx = side * 24 + gx * 4 + dx
        cy = shape["dy"] + gy * 3
        top = cy - h / 2

        eye = QPainterPath()
        eye.addRoundedRect(QRectF(cx - w / 2, top, w, h), min(w, h) * 0.38, min(w, h) * 0.38)

        if blink > 0.5:
            outer_x = cx + side * w / 2
            inner_x = cx - side * w / 2
            lid = QPainterPath()
            lid.addPolygon(QPolygonF([
                QPointF(outer_x + side * 4, top - 40),
                QPointF(inner_x - side * 4, top - 40),
                QPointF(inner_x - side * 4, top + shape["inner"] * h),
                QPointF(outer_x + side * 4, top + shape["outer"] * h),
            ]))
            eye = eye.subtracted(lid)
            if shape["smile"] > 0.02:
                cut = QPainterPath()
                ch = h * shape["smile"] * 1.6
                cut.addEllipse(QRectF(cx - w * 0.75, top + h - ch * 0.45, w * 1.5, ch))
                eye = eye.subtracted(cut)

        p.setBrush(a.olho if cor is None else cor)
        p.drawPath(eye)

        if brilho and blink > 0.5 and h >= 8:      # olho fechado não tem brilho
            p.save()
            p.setClipPath(eye)
            p.setBrush(a.brilho)
            sx = cx - w * 0.18 + gx * 3
            sy = top + h * (0.24 + max(shape["inner"], shape["outer"]) * 0.6) + gy * 2
            p.drawEllipse(QPointF(sx, sy), 3.6, 3.6)
            p.restore()


def _clip_tela(p):
    """Recorta o pincel na tela do pet (os efeitos nunca saem dela), somando com o recorte do notebook."""
    tela = QPainterPath()
    tela.addRoundedRect(TELA, RAIO_TELA, RAIO_TELA)
    p.setClipPath(tela, Qt.IntersectClip)


def _chuva(p, a, agora):
    """Chuva de código bem fraquinha atrás dos olhos: colunas que descem em velocidades diferentes."""
    p.save()
    _clip_tela(p)
    fonte = QFont("monospace")
    fonte.setStyleHint(QFont.Monospace)
    fonte.setPixelSize(7)
    p.setFont(fonte)
    base = QColor(a.codigo if a.codigo is not None else a.olho)
    passo, linhas = 7, int(TELA.height() // 7) + 1
    for coluna in range(12):
        semente = (coluna * 2654435761) & 0xFFFFFFFF
        velocidade = 5 + semente % 9                    # linhas por segundo
        fase = (semente >> 9) % 37
        cabeca = int(agora * velocidade + fase) % (linhas + 9)
        x = TELA.left() + 3 + coluna * 8
        for rastro in range(5):
            linha = cabeca - rastro
            if not 0 <= linha < linhas:
                continue
            cor = QColor(base)
            cor.setAlpha(165 if rastro == 0 else 105 - rastro * 18)
            p.setPen(cor)
            indice = (semente + linha * 31 + (int(agora * 6) if rastro == 0 else 0)) % len(SIMBOLOS_CHUVA)
            p.drawText(QPointF(x, TELA.top() + linha * passo + 6), SIMBOLOS_CHUVA[indice])
    p.restore()


def _scanlines(p):
    """Linhas finas de monitor antigo, por cima dos olhos."""
    p.save()
    _clip_tela(p)
    p.setPen(QPen(QColor(0, 0, 0, 58), 1))
    y = TELA.top() + 1
    while y < TELA.bottom():
        p.drawLine(QPointF(TELA.left(), y), QPointF(TELA.right(), y))
        y += 3
    p.restore()


def _glitch(p, shape, gaze, blink, emotion, a, agora):
    """Separação de cores nos olhos e duas faixas tortas na tela, por um instante."""
    p.save()
    _clip_tela(p)
    for cor, dx in ((GLITCH_A, -2.5), (GLITCH_B, 2.5)):
        c = QColor(cor)
        c.setAlpha(150)
        _olhos(p, shape, gaze, blink, emotion, a, cor=c, dx=dx, brilho=False)
    quadro = int(agora * 30)
    faixa = QColor(a.olho)
    faixa.setAlpha(90)
    p.setBrush(faixa)
    for i in range(2):
        semente = (quadro * 7 + i * 13) % 97
        y = TELA.top() + 6 + semente % int(TELA.height() - 12)
        largura = 30 + (semente * 3) % 60
        p.drawRect(QRectF(TELA.left() + semente % 40, y, largura, 2 + i))
    p.restore()


def _capuz(p, cor):
    """Capuz de moletom por trás do corpo: sobe numa ponta acima da moldura e desce pelos lados."""
    p.save()
    escura = cor.darker(135)
    borda = cor.lighter(175)                          # luz de recorte: o capuz aparece até em fundo escuro
    capuz = QPainterPath(QPointF(-64, 36))
    capuz.cubicTo(QPointF(-78, -8), QPointF(-60, -60), QPointF(0, -64))
    capuz.cubicTo(QPointF(60, -60), QPointF(78, -8), QPointF(64, 36))
    capuz.closeSubpath()
    p.setPen(QPen(borda, 2))
    p.setBrush(cor)
    p.drawPath(capuz)
    # a sombra para onde o capuz acaba (nada embaixo do corpo); soma com o recorte do notebook, se houver
    p.setClipRect(QRectF(-90, -90, 180, 126), Qt.IntersectClip)
    p.setPen(QPen(escura.darker(150), 4))              # a sombra da abertura, em volta do rosto
    p.setBrush(Qt.NoBrush)
    p.drawRoundedRect(QRectF(-BODY_W / 2 - 4, -BODY_H / 2 - 4, BODY_W + 8, BODY_H + 8), 23, 23)
    p.setPen(QPen(escura, 1.5))
    p.drawLine(QPointF(0, -63), QPointF(0, -51))      # costura
    p.restore()


def _cordinhas(p, cor):
    """As cordinhas do capuz, curtas, na faixa entre a tela e a borda de baixo (não passam do chão)."""
    p.save()
    clara = cor.lighter(230)
    p.setPen(QPen(clara, 1.6, Qt.SolidLine, Qt.RoundCap))
    for side in (-1, 1):
        p.drawLine(QPointF(side * 15, 35), QPointF(side * 17, 41))
    p.setPen(Qt.NoPen)
    p.setBrush(clara)
    for side in (-1, 1):
        p.drawRoundedRect(QRectF(side * 17 - 1.5, 40, 3, 3.5), 1, 1)
    p.restore()


def _fones(p, cor):
    """Headset: arco por cima da cabeça, conchas com uma luzinha nos lados e o microfone perto da boca."""
    p.save()
    escura = cor.darker(170)
    arco = QRectF(-62, -66, 124, 120)
    p.setBrush(Qt.NoBrush)
    p.setPen(QPen(escura, 6, Qt.SolidLine, Qt.RoundCap))
    p.drawArc(arco, 12 * 16, 156 * 16)
    p.setPen(QPen(cor, 2.5, Qt.SolidLine, Qt.RoundCap))
    p.drawArc(arco, 14 * 16, 152 * 16)
    microfone = QPainterPath(QPointF(-58, 10))
    microfone.quadTo(QPointF(-56, 32), QPointF(-35, 31))
    p.setPen(QPen(escura, 3, Qt.SolidLine, Qt.RoundCap))
    p.drawPath(microfone)
    for side in (-1, 1):
        p.setPen(QPen(escura, 1.5))
        p.setBrush(QColor("#151a22"))
        p.drawRoundedRect(QRectF(side * 61 - 8, -16, 16, 32), 6, 6)
        p.setPen(Qt.NoPen)
        p.setBrush(cor)
        p.drawRoundedRect(QRectF(side * 61 - 2.5, -9, 5, 18), 2.5, 2.5)
    p.setBrush(cor)
    p.drawEllipse(QPointF(-33, 31), 3.5, 3)
    p.restore()


def _oculos(p, cor):
    """Armação por cima dos olhos: aro grosso em cima, fino embaixo, e a ponte no meio."""
    p.save()
    p.setBrush(Qt.NoBrush)
    for side in (-1, 1):
        lente = QRectF(side * 24 - 21, -25, 42, 52)
        vidro = QColor(cor)
        vidro.setAlpha(22)                              # um reflexo leve: o olho continua aparecendo
        p.setPen(Qt.NoPen)
        p.setBrush(vidro)
        p.drawRoundedRect(lente, 10, 10)
        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(cor, 2))
        p.drawRoundedRect(lente, 10, 10)
        p.setPen(QPen(cor, 5, Qt.SolidLine, Qt.RoundCap))
        p.drawLine(QPointF(lente.left() + 4, lente.top()), QPointF(lente.right() - 4, lente.top()))
    p.setPen(QPen(cor, 3, Qt.SolidLine, Qt.RoundCap))
    p.drawLine(QPointF(-3, -18), QPointF(3, -18))       # ponte
    p.restore()


def _gravata(p, cor):
    """
    Gravata na frente do peito, dentro do contorno do corpo. Termina antes da borda de baixo para
    não cair na barra de tarefas quando ele anda sobre ela.
    """
    p.save()
    topo = BODY_H / 2 - 24                              # nó logo abaixo da tela, cola no contorno
    escura = cor.darker(140)
    p.setPen(QPen(escura, 1.2))
    p.setBrush(cor)
    p.drawPolygon(QPolygonF([QPointF(-4, topo), QPointF(4, topo), QPointF(3.5, topo + 6),
                             QPointF(-3.5, topo + 6)]))          # nó
    p.drawPolygon(QPolygonF([QPointF(-3, topo + 5), QPointF(3, topo + 5), QPointF(5.5, topo + 17),
                             QPointF(0, topo + 21), QPointF(-5.5, topo + 17)]))   # ponta
    p.setPen(QPen(escura, 1.5))
    p.drawLine(QPointF(-4, topo + 10), QPointF(4, topo + 8))                   # listra
    p.restore()


def draw_zzz(p, cx, cy, now, cor=EYE):
    """Zs subindo do canto de cima do corpo, crescendo, balançando e sumindo."""
    for i in range(ZZZ_COUNT):
        t = ((now / ZZZ_PERIOD) + i / ZZZ_COUNT) % 1.0     # 0 nasce ... 1 some
        x = cx + BODY_W * 0.32 + 34 * t + 5 * math.sin(t * math.tau * 1.5)
        y = cy - BODY_H * 0.42 - 44 * t       # sobe até ~12 px do topo da janela
        size = 8 + 9 * t
        alpha = int(255 * min(1.0, t * 5) * (1.0 - t) ** 0.6)
        color = QColor(cor)
        color.setAlpha(alpha)
        p.save()
        p.translate(x, y)
        p.rotate(-12 + 10 * math.sin(t * math.tau))
        p.setPen(color)
        p.setFont(QFont("Consolas", int(size), QFont.Bold))
        p.drawText(QRectF(-20, -20, 40, 40), Qt.AlignCenter, "Z")
        p.restore()
