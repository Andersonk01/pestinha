"""
DESENHO DA BOLA - o corpo redondo de pelo (o Bolota). O pelo vem de uma imagem (`pets/<pet>/corpo.png`, sem
olhos e sem patinhas, feita por ferramentas/gerar_bolota.py) e o resto é desenhado por código por cima:
olhos com pálpebras, patinhas, pezinhos e as linhas de velocidade.

A imagem não tem olhos: uma pálpebra é só a parte do olho que não se pinta, e ali aparece o próprio pelo.
O jeito de se mexer (rolar, correr, acenar, achatar no pouso) é decidido por `AnimacaoBola`, a partir do
movimento do corpo; o desenho só lê a `Pose`.

Cores (as do pets/<pet>.json ou as do estilo): tela = branco do olho, olho = pupila, brilho = reflexo,
casca = contornos, moldura = patinhas e pezinhos. Um estilo tinge o pelo com a cor dele (`Aparencia.tinta`).
"""

import math
from dataclasses import dataclass

import numpy as np
from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPainterPath, QPen, QPixmap, QPolygonF, QRadialGradient

from .desenho_rosto import GLITCH_A, GLITCH_B, _chuva, _scanlines, glitch_ativo

# medidas tiradas da arte (ferramentas/gerar_bolota.py), em px da tela, com a origem no centro do corpo
ESCALA = 50 / 422                    # a bola tem ~844 px de largura na arte e ~100 px na tela
LADO = 900 * ESCALA                  # o corpo.png cobre 900 x 900 px da arte
BAIXO = 389 * ESCALA                 # do centro da bola até a ponta de baixo do pelo
BOLA_Y = 43.0 - BAIXO                # o centro da bola: o pelo acaba 2 px acima do chão (45) e os pés tocam nele
RAIO = 46.0                          # raio de rolagem: a distância andada vira giro
OLHO_DX, OLHO_Y, OLHO_R = 15.4, -5.9, 13.4    # um pouco maiores que na arte: lê melhor pequeno
OMBRO_X, OMBRO_Y = 41.0, 8.0         # onde a patinha sai, por trás do pelo
BRACO_REPOUSO, BRACO_COMPRIMENTO = 36.0, 13.0     # graus abaixo da horizontal, px até o meio da pata
PE_X, PE_Y = 13.0, 45.0 - BOLA_Y - 4.5
PALPEBRA_LIVRE = 0.12                # o tanto de pálpebra (inner/outer) que ele ignora
RAIO_DA_AREA = 44.0                  # onde ficam os efeitos de tela (chuva, scanlines): dentro do pelo

VEL_ANDANDO = 8.0                    # px/s: abaixo disso ele está parado
VEL_CORRIDA = 120.0                  # px/s: feliz e mais rápido que isso, corre com os pezinhos em vez de rolar
DURACAO_ACENO = 1.8                  # s


@dataclass
class Pose:
    """Como o corpo está agora (escrito por AnimacaoBola, lido pelo desenho)."""
    rolagem: float = 0.0     # graus, no sentido do relógio (rolando para a direita)
    achatar: float = 0.0     # 0 normal; mais que 0, amassado (acabou de pousar)
    corrida: float = -1.0    # menos que 0: não está correndo; senão, a fase dos passos (radianos)
    direcao: int = 1         # 1 indo para a direita, -1 para a esquerda
    aceno: float = 0.0       # 0 sem aceno ... 1 acenando de todo
    velocidade: float = 0.0  # px/s andando no chão

    def rolando(self):
        """Diz se ele está fora de pé (no meio de uma volta)."""
        return abs(_falta_para_ficar_em_pe(self.rolagem)) > 12.0

    def correndo(self):
        return self.corrida >= 0.0

    def patinhas(self):
        """De 0 (recolhidas no pelo, rolando) a 1 (para fora, em pé)."""
        return max(0.0, 1.0 - abs(_falta_para_ficar_em_pe(self.rolagem)) / 25.0)


def _falta_para_ficar_em_pe(graus):
    """De -180 a 180: quanto a rolagem está fora de pé."""
    return (graus + 180.0) % 360.0 - 180.0


class AnimacaoBola:
    """
    Decide a pose a cada quadro, a partir do movimento do corpo: andando no chão, ele rola (a distância
    vira giro); feliz e rápido, corre com os pezinhos; parado, termina a volta e fica em pé. Achata ao pousar
    de uma queda e acena ao acordar e quando fica feliz.
    """

    def __init__(self):
        self.pose = Pose()
        self._t = None
        self._x = None
        self._vel = 0.0
        self._passos = 0.0
        self._no_chao = True
        self._vy = 0.0
        self._emocao = None
        self._aceno_desde = -100.0

    def acenar(self, agora):
        """Começa um aceno (com a patinha direita)."""
        self._aceno_desde = agora

    def passo(self, agora, x, vy, no_chao, segurado, emocao, sentado=False):
        pose = self.pose
        dt = 0.0 if self._t is None else max(0.0, min(0.1, agora - self._t))
        dx = 0.0 if self._x is None else x - self._x
        self._t, self._x = agora, x
        if dt > 0:
            self._vel += (abs(dx) / dt - self._vel) * min(1.0, dt * 10.0)   # o movimento chega aos trancos
        andando = no_chao and not segurado and not sentado and self._vel > VEL_ANDANDO
        if dx:
            pose.direcao = 1 if dx > 0 else -1
        correndo = andando and emocao in ("feliz", "contente") and self._vel > VEL_CORRIDA
        if correndo:
            self._passos += abs(dx) / 9.0
            pose.corrida = self._passos
        else:
            pose.corrida = -1.0
        if andando and not correndo:
            pose.rolagem = (pose.rolagem + math.degrees(dx / RAIO)) % 360.0
        else:                                           # termina a volta: fica em pé pelo lado mais perto
            falta = _falta_para_ficar_em_pe(pose.rolagem)
            pose.rolagem = (pose.rolagem - falta * min(1.0, dt * (14.0 if correndo else 7.0))) % 360.0
        pose.velocidade = self._vel if andando else 0.0

        if not no_chao:
            self._vy = vy
        elif not self._no_chao and self._vy > 250.0:  # pousou de uma queda
            pose.achatar = min(0.24, self._vy / 2600.0)
        self._no_chao = no_chao
        pose.achatar *= math.exp(-dt * 9.0)

        if emocao != self._emocao:
            acordou = self._emocao == "dormindo"
            ficou_feliz = emocao == "feliz" and self._emocao not in ("feliz", "contente")
            if self._emocao is not None and not andando and (acordou or ficou_feliz):
                self.acenar(agora)
            self._emocao = emocao
        t = agora - self._aceno_desde
        if andando or not 0.0 <= t < DURACAO_ACENO:
            pose.aceno = 0.0
        else:
            pose.aceno = max(0.0, min(1.0, t / 0.2, (DURACAO_ACENO - t) / 0.3))
        return pose


# ---------------- o pelo ----------------

def tingir(imagem, cor):
    """O pelo na cor `cor`: guarda o claro e escuro dos fios (a luminância) e troca o marrom pela cor."""
    img = imagem.convertToFormat(QImage.Format_RGBA8888)
    w, h = img.width(), img.height()
    a = np.frombuffer(img.constBits(), np.uint8).reshape(h, w, 4).astype(np.float32)
    lum = a[..., 0] * 0.299 + a[..., 1] * 0.587 + a[..., 2] * 0.114
    opaco = a[..., 3] > 128
    media = float(lum[opaco].mean()) if opaco.any() else 1.0
    fator = (lum / max(media, 1.0)) * 0.62
    saida = a.copy()
    saida[..., :3] = np.array([cor.red(), cor.green(), cor.blue()], np.float32) * fator[..., None]
    saida = np.ascontiguousarray(np.clip(saida, 0, 255).astype(np.uint8))
    return QImage(saida.data, w, h, 4 * w, QImage.Format_RGBA8888).copy()


def pelo_simples(lado=288):
    """Um pelo desenhado por código, para quando o corpo.png falta: o pet nunca fica sem corpo."""
    img = QImage(lado, lado, QImage.Format_ARGB32_Premultiplied)
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    c = lado / 2
    raio = lado * 422 / 900
    caminho = QPainterPath()
    pontas = 46
    for i in range(pontas * 2):
        ang = math.pi * i / pontas
        r = raio if i % 2 == 0 else raio * 0.9
        ponto = QPointF(c + r * math.cos(ang), c + 0.92 * r * math.sin(ang) + lado * 0.02)
        if i:
            caminho.lineTo(ponto)
        else:
            caminho.moveTo(ponto)
    caminho.closeSubpath()
    grad = QRadialGradient(QPointF(c - raio * 0.3, c - raio * 0.35), raio * 1.4)
    grad.setColorAt(0.0, QColor("#a8673a"))
    grad.setColorAt(1.0, QColor("#4a2914"))
    p.setPen(QPen(QColor("#2b170c"), lado / 120))
    p.setBrush(grad)
    p.drawPath(caminho)
    p.end()
    return img


class CorpoBola:
    """
    O pelo do pet (a imagem) e as versões tingidas pelos estilos, feitas uma vez e guardadas. Também mede,
    para cada ângulo de rolagem, até onde o pelo desce: a bola não é redonda de verdade (é mais larga que
    alta e tem o topete), e rolando ela precisa encostar no chão sem passar dele.
    """

    PASSO_DO_ANGULO = 5

    def __init__(self, imagem=None):
        self.imagem = imagem if imagem is not None and not imagem.isNull() else pelo_simples()
        self._prontos = {}
        self._baixo = self._medir_baixo()

    def _medir_baixo(self):
        img = self.imagem.convertToFormat(QImage.Format_RGBA8888)
        w, h = img.width(), img.height()
        alfa = np.frombuffer(img.constBits(), np.uint8).reshape(h, w, 4)[::2, ::2, 3]
        ys, xs = np.nonzero(alfa > 128)
        escala = LADO / w
        x = (xs * 2 - w / 2) * escala
        y = (ys * 2 - h / 2) * escala
        angulos = np.radians(np.arange(0, 360, self.PASSO_DO_ANGULO))
        return [float((x * math.sin(a) + y * math.cos(a)).max()) if len(x) else BAIXO for a in angulos]

    def baixo(self, graus):
        """Do centro da bola até o ponto mais baixo do pelo, com ela girada `graus` (sentido do relógio)."""
        pos = (graus % 360.0) / self.PASSO_DO_ANGULO
        i = int(pos)
        k = pos - i
        return self._baixo[i % len(self._baixo)] * (1 - k) + self._baixo[(i + 1) % len(self._baixo)] * k

    def pixmap(self, tinta=None):
        chave = None if tinta is None else tinta.rgb()
        if chave not in self._prontos:
            img = self.imagem if tinta is None else tingir(self.imagem, tinta)
            self._prontos[chave] = QPixmap.fromImage(img)
        return self._prontos[chave]


def cor_das_patas(a):
    """As patinhas e os pezinhos: a cor do pet ou, com um estilo, a tinta um pouco mais escura que o pelo."""
    if a.tinta is None:
        return QColor(a.moldura)
    return QColor.fromRgbF(a.tinta.redF() * 0.5, a.tinta.greenF() * 0.5, a.tinta.blueF() * 0.5)


def cor_dos_textos(a):
    """Cor dos Zzz e do rótulo da emoção: a pupila escura sumiria no fundo; vai a das patinhas, mais clara."""
    return cor_das_patas(a).lighter(170)


# ---------------- o desenho ----------------

def desenhar_bola(p, corpo, pose, shape, gaze=(0.0, 0.0), blink=1.0, emotion="observando", carinho=False,
                  aparencia=None, agora=0.0):
    """Desenha a bola com o centro do corpo físico na origem do painter: pés, patinhas, pelo, efeitos e olhos."""
    a = aparencia
    p.save()
    p.setRenderHint(QPainter.SmoothPixmapTransform)
    correndo, rolando = pose.correndo(), pose.rolando()
    if correndo:
        _linhas_de_velocidade(p, pose, a, agora)
    fase = pose.corrida if correndo else 0.0
    pulo = abs(math.sin(fase)) * 2.5 if correndo else 0.0
    respira = 0.0 if (correndo or rolando or emotion == "dormindo") else 0.012 * math.sin(agora * 2.4)
    # rolando, o pelo encosta no chão (45) seja qual for o lado de baixo; em pé, quem encosta são os pés
    encosta = (corpo.baixo(pose.rolagem) - (45.0 - BOLA_Y)) * (1.0 - pose.patinhas())
    p.translate(0.0, BOLA_Y - pulo - encosta)
    # amassa no pouso e respira parado, sempre com a base no chão
    p.translate(0.0, BAIXO)
    p.scale(1.0 + pose.achatar * 0.9 - respira * 0.5, 1.0 - pose.achatar + respira)
    p.translate(0.0, -BAIXO)
    p.rotate(pose.rolagem)
    if not rolando:
        _pes(p, a, pose, fase)
    _bracos(p, a, pose, fase, agora)
    pelo = corpo.pixmap(a.tinta)
    p.drawPixmap(QRectF(-LADO / 2, -LADO / 2, LADO, LADO), pelo, QRectF(pelo.rect()))
    area = QPainterPath()
    area.addEllipse(QPointF(0.0, 0.0), RAIO_DA_AREA, RAIO_DA_AREA)
    if "chuva" in a.efeitos:
        _chuva(p, a, agora, area)
    fechados = carinho or (correndo and emotion == "feliz")
    _olhos(p, shape, gaze, blink, emotion, fechados, a, agora)
    if "scanlines" in a.efeitos:
        _scanlines(p, area)
    p.restore()


def _olhos(p, shape, gaze, blink, emotion, fechados, a, agora):
    """
    Os dois olhos: branco, pupila e reflexo. As emoções vêm da mesma forma de olho dos outros personagens:
    `inner` e `outer` baixam a pálpebra de cima (no canto de dentro e no de fora), `smile` sobe a bochecha,
    `h` abre ou fecha e `dy` desce o olhar.
    """
    gx, gy = gaze
    for side in (-1, 1):
        rx = OLHO_R * min(1.25, max(0.8, shape["w"] / 30.0))
        ry = OLHO_R * min(1.3, max(0.0, shape["h"] / 40.0))
        if emotion == "curioso" and side == 1:
            ry *= 1.12
        cx = side * OLHO_DX + gx * 1.2
        cy = OLHO_Y + shape["dy"] * 0.45 + gy * 0.8
        if fechados or emotion == "dormindo" or blink < 0.5 or ry < 4.0:
            _olho_fechado(p, cx, cy, rx, a.casca, feliz=fechados)
            continue
        olho = QPainterPath()
        olho.addEllipse(QPointF(cx, cy), rx, ry)
        topo = cy - ry
        externo, interno = cx + side * rx, cx - side * rx
        # olhos redondos e bem abertos como na arte: a pálpebra só desce de verdade nas emoções fortes
        dentro, fora = (max(0.0, shape[k] - PALPEBRA_LIVRE) * 1.1 for k in ("inner", "outer"))
        palpebra = QPainterPath()
        palpebra.addPolygon(QPolygonF([
            QPointF(externo + side * 3, topo - 20),
            QPointF(interno - side * 3, topo - 20),
            QPointF(interno - side * 3, topo + dentro * 2 * ry),
            QPointF(externo + side * 3, topo + fora * 2 * ry),
        ]))
        aberto = olho.subtracted(palpebra)
        if shape["smile"] > 0.02:
            bochecha = QPainterPath()
            altura = 2 * ry * shape["smile"] * 1.1
            bochecha.addEllipse(QRectF(cx - rx * 1.5, topo + 2 * ry - altura * 0.45, rx * 3, altura))
            aberto = aberto.subtracted(bochecha)
        p.setPen(Qt.NoPen)
        p.setBrush(a.tela)
        p.drawPath(aberto)

        p.save()
        p.setClipPath(aberto, Qt.IntersectClip)
        tamanho = 0.72 if emotion == "assustado" else 1.12 if emotion in ("feliz", "dramatico") else 1.0
        px, py = cx + gx * rx * 0.42, cy + gy * ry * 0.3 + ry * 0.06
        prx, pry = OLHO_R * 0.42 * tamanho, OLHO_R * 0.52 * tamanho
        if "glitch" in a.efeitos and glitch_ativo(agora):
            for cor, dx in ((GLITCH_A, -1.8), (GLITCH_B, 1.8)):
                c = QColor(cor)
                c.setAlpha(170)
                p.setBrush(c)
                p.drawEllipse(QPointF(px + dx, py), prx, pry)
        p.setBrush(a.olho)
        p.drawEllipse(QPointF(px, py), prx, pry)
        p.setBrush(a.brilho)
        reflexo = max(1.3, prx * 0.32)
        p.drawEllipse(QPointF(px + prx * 0.35, py - pry * 0.45), reflexo, reflexo)
        p.restore()

        p.setBrush(Qt.NoBrush)
        p.setPen(QPen(a.casca, 1.6))
        p.drawPath(aberto)


def _olho_fechado(p, cx, cy, rx, cor, feliz):
    """Olho fechado: um arco para cima de felicidade (^ ^) ou para baixo, dormindo ou piscando."""
    risco = QPainterPath(QPointF(cx - rx * 0.78, cy + (2.5 if feliz else 0.0)))
    if feliz:
        risco.quadTo(QPointF(cx, cy - 6.0), QPointF(cx + rx * 0.78, cy + 2.5))
    else:
        risco.quadTo(QPointF(cx, cy + 4.5), QPointF(cx + rx * 0.78, cy))
    p.setBrush(Qt.NoBrush)
    p.setPen(QPen(QColor(cor).darker(160), 2.8, Qt.SolidLine, Qt.RoundCap))     # escuro: o pelo também é
    p.drawPath(risco)


def _bracos(p, a, pose, fase, agora):
    """As duas patinhas: paradas meio para baixo, balançando na corrida; a direita acena. Rolando, recolhem."""
    fora = pose.patinhas()
    if fora <= 0.05:
        return
    for side in (-1, 1):
        angulo, comprimento = BRACO_REPOUSO, BRACO_COMPRIMENTO * fora - 10.0 * (1.0 - fora)
        if pose.correndo():
            angulo += 28.0 * math.sin(fase + (0.0 if side > 0 else math.pi))
        if side == 1 and pose.aceno > 0.0:
            alvo = -62.0 + 20.0 * math.sin(agora * 10.0)
            angulo += (alvo - angulo) * pose.aceno
            comprimento += 5.0 * pose.aceno
        _braco(p, a, side, angulo, comprimento)


def _braco(p, a, side, angulo, comprimento):
    """Uma patinha saindo de trás do pelo: o braço, a pata e três dedinhos, com contorno escuro."""
    p.save()
    p.translate(side * OMBRO_X, OMBRO_Y)
    p.scale(side, 1.0)                # a esquerda é a direita espelhada
    p.rotate(angulo)                  # o eixo x aponta para fora, `angulo` graus abaixo da horizontal
    forma = QPainterPath()
    forma.addPolygon(QPolygonF([QPointF(-6, -3.6), QPointF(comprimento, -4.4), QPointF(comprimento, 4.4),
                                QPointF(-6, 3.6)]))
    pata = QPainterPath()
    pata.addEllipse(QPointF(comprimento + 2.0, 0.6), 8.0, 5.6)
    forma = forma.united(pata)
    for dx in (-4.0, 0.0, 4.0):
        dedo = QPainterPath()
        dedo.addEllipse(QPointF(comprimento + 2.5 + dx, 4.4), 2.9, 2.6)
        forma = forma.united(dedo)
    cor = cor_das_patas(a)
    p.setPen(QPen(a.casca, 1.5))
    p.setBrush(cor)
    p.drawPath(forma)
    p.setPen(QPen(a.casca, 1.0, Qt.SolidLine, Qt.RoundCap))
    for dx in (-2.0, 2.0):                                  # o vão entre os dedinhos
        p.drawLine(QPointF(comprimento + 2.5 + dx, 3.6), QPointF(comprimento + 2.5 + dx, 5.9))
    p.restore()


def _pes(p, a, pose, fase):
    """Os pezinhos, quase todos escondidos pelo pelo; na corrida, um de cada vez sobe e vai para a frente."""
    cor = cor_das_patas(a)
    for side in (-1, 1):
        oposto = 0.0 if side > 0 else math.pi
        sobe = max(0.0, math.sin(fase + oposto)) * 3.5 if pose.correndo() else 0.0
        frente = math.cos(fase + oposto) * 3.0 * pose.direcao if pose.correndo() else 0.0
        p.setPen(QPen(a.casca, 1.4))
        p.setBrush(cor)
        p.drawEllipse(QPointF(side * PE_X + frente, PE_Y - sobe), 7.0, 4.5)


def _linhas_de_velocidade(p, pose, a, agora):
    """Três riscos atrás dele na corrida, que vão ficando para trás e somem."""
    forca = max(0.35, min(1.0, (pose.velocidade - VEL_CORRIDA) / 200.0 + 0.4))
    atras = -pose.direcao
    for i, (y, comprimento) in enumerate(((-14.0, 18.0), (0.0, 24.0), (14.0, 15.0))):
        fase = (agora * 3.0 + i * 0.37) % 1.0
        x0 = atras * (50.0 + fase * 18.0)
        cor = cor_das_patas(a).lighter(150)
        cor.setAlpha(int(150 * forca * (1.0 - fase)))
        p.setPen(QPen(cor, 2.0, Qt.SolidLine, Qt.RoundCap))
        p.drawLine(QPointF(x0, BOLA_Y + y), QPointF(x0 + atras * comprimento * (1.0 - fase * 0.5), BOLA_Y + y))
