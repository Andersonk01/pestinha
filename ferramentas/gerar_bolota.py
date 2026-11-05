#!/usr/bin/env python3
"""
Prepara o corpo do Bolota (pets/bolota/corpo.png) a partir da arte original (ferramentas/arte/bolota.png):
só o pelo, sem os olhos e sem as patinhas, que o pet desenha por código por cima (body/desenho_bola.py)
para piscar, mudar de expressão, acenar, correr e rolar. O mesmo pelo, pequeno, vira o tufo que ele atira
na revolução (pets/bolota/bolinha_papel.png).

    python ferramentas/gerar_bolota.py [arte.png]

- As patinhas saem de trás do pelo, separadas dele por uma frestinha: um polígono por patinha as apaga.
- Os olhos são cobertos pelo pelo de logo abaixo deles, com a borda esfumada.
- O resultado é um quadrado centrado no meio da bola, reduzido para LADO px.

As coordenadas são da arte original (1230 x 1278 px). Roda sem tela (QT_QPA_PLATFORM=offscreen).
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np  # noqa: E402
from PySide6.QtCore import QPointF, Qt  # noqa: E402
from PySide6.QtGui import QColor, QGuiApplication, QImage, QPainter, QPolygonF  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
ARTE = RAIZ / "ferramentas" / "arte" / "bolota.png"
DESTINO = RAIZ / "pets" / "bolota" / "corpo.png"
TUFO = RAIZ / "pets" / "bolota" / "bolinha_papel.png"
LADO_TUFO = 160

CENTRO = (607, 668)          # o meio da bola, sem as patinhas
METADE = 450                 # meio lado do recorte quadrado (cabe o topete e as pontas do pelo)
LADO = 288                   # px do corpo.png (o pet desenha com ~107 px: sobra para telas HiDPI)

# o contorno das patinhas, por fora do pelo (o que sobra é o pelo que passa na frente delas)
PATINHAS = (
    [(108, 892), (108, 780), (150, 752), (200, 727), (238, 713), (252, 722), (252, 760), (249, 790),
     (246, 820), (244, 850), (238, 878), (220, 892)],
    [(1102, 892), (1102, 770), (1060, 748), (1012, 731), (990, 729), (983, 758), (979, 790), (977, 830),
     (979, 868), (992, 892)],
)
# (centro x, centro y, raio com o contorno escuro) de cada olho, e de onde vem o pelo que o cobre
OLHOS = ((515, 620, 118), (758, 616, 116))
DESLOCAMENTO_DO_PELO = 252   # px para baixo: abaixo do contorno de baixo do olho, acima do fim da bola
ESFUMADO = 12                # px da borda do remendo


def como_array(img):
    img = img.convertToFormat(QImage.Format_RGBA8888)
    return np.frombuffer(img.constBits(), np.uint8).reshape(img.height(), img.width(), 4).astype(np.float32)


def como_imagem(arr):
    arr = np.ascontiguousarray(np.clip(arr, 0, 255).astype(np.uint8))
    h, w = arr.shape[:2]
    return QImage(arr.data, w, h, 4 * w, QImage.Format_RGBA8888).copy()


def mascara_dos_poligonos(largura, altura, poligonos):
    """1.0 dentro dos polígonos, 0.0 fora (com antialias na borda)."""
    m = QImage(largura, altura, QImage.Format_Grayscale8)
    m.fill(0)
    p = QPainter(m)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(255, 255, 255))
    for pontos in poligonos:
        p.drawPolygon(QPolygonF([QPointF(x, y) for x, y in pontos]))
    p.end()
    linha = m.bytesPerLine()
    bruto = np.frombuffer(m.constBits(), np.uint8).reshape(altura, linha)[:, :largura]
    return bruto.astype(np.float32) / 255.0


def sem_patinhas(arr):
    h, w = arr.shape[:2]
    dentro = mascara_dos_poligonos(w, h, PATINHAS)
    arr[..., 3] *= 1.0 - dentro
    return arr


def _caixa(a, raio, eixo):
    """Média móvel de 2*raio+1 px ao longo de um eixo (a borda se repete)."""
    pad = [(0, 0)] * a.ndim
    pad[eixo] = (raio + 1, raio)
    soma = np.cumsum(np.pad(a, pad, mode="edge"), axis=eixo)
    n = a.shape[eixo]
    fim = np.take(soma, np.arange(2 * raio + 1, 2 * raio + 1 + n), axis=eixo)
    inicio = np.take(soma, np.arange(0, n), axis=eixo)
    return (fim - inicio) / (2 * raio + 1)


def borrar(a, raio):
    """Três passadas de caixa: quase um gaussiano."""
    for _ in range(3):
        a = _caixa(_caixa(a, raio, 0), raio, 1)
    return a


def sem_olhos(arr):
    """
    Cobre cada olho com pelo. A textura (os fios) vem de logo abaixo do olho; o tom vem do pelo em volta
    dele, borrado e esticado para dentro do buraco. Assim o remendo não fica com a sombra de baixo da bola.
    """
    h, w = arr.shape[:2]
    ys, xs = np.mgrid[0:h, 0:w]
    rgb = arr[..., :3]
    buraco = np.zeros((h, w), bool)
    for cx, cy, raio in OLHOS:
        buraco |= np.hypot(xs - cx, ys - cy) < raio + ESFUMADO
    conhecido = (~buraco & (arr[..., 3] > 250)).astype(np.float32)[..., None]
    tom = borrar(rgb * conhecido, 64) / np.maximum(borrar(conhecido, 64), 1e-3)   # média do pelo em volta
    pelo = np.roll(rgb, -DESLOCAMENTO_DO_PELO, axis=0)              # o pelo de baixo, trazido para cima
    fios = pelo - borrar(pelo, 40)                                  # só a textura, sem o tom
    remendo = np.clip(tom + fios, 0, 255)
    for cx, cy, raio in OLHOS:
        peso = np.clip((raio + ESFUMADO - np.hypot(xs - cx, ys - cy)) / ESFUMADO, 0.0, 1.0)[..., None]
        arr[..., :3] = arr[..., :3] * (1.0 - peso) + remendo * peso
        arr[..., 3:] = np.maximum(arr[..., 3:], 255.0 * peso)
    return arr


def recortar(arr):
    """O quadrado em volta do CENTRO (fora da arte, transparente), reduzido para LADO px."""
    h, w = arr.shape[:2]
    cx, cy = CENTRO
    quadro = np.zeros((2 * METADE, 2 * METADE, 4), np.float32)
    x0, y0 = cx - METADE, cy - METADE
    fx0, fy0 = max(0, x0), max(0, y0)
    fx1, fy1 = min(w, cx + METADE), min(h, cy + METADE)
    quadro[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0] = arr[fy0:fy1, fx0:fx1]
    # reduz com o alfa pré-multiplicado, para a borda não escurecer nem clarear
    img = como_imagem(quadro).convertToFormat(QImage.Format_RGBA8888_Premultiplied)
    img = img.scaled(LADO, LADO, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    return img.convertToFormat(QImage.Format_ARGB32)


def preparar(arte):
    img = QImage(str(arte))
    if img.isNull():
        sys.exit(f"não consegui abrir {arte}")
    return recortar(sem_olhos(sem_patinhas(como_array(img))))


def main():
    QGuiApplication.instance() or QGuiApplication(sys.argv[:1])
    arte = Path(sys.argv[1]) if len(sys.argv) > 1 else ARTE
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    corpo = preparar(arte)
    tufo = corpo.scaled(LADO_TUFO, LADO_TUFO, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    for img, destino in ((corpo, DESTINO), (tufo, TUFO)):
        if not img.save(str(destino)):
            sys.exit(f"não consegui gravar {destino}")
    print(f"corpo e tufo gravados em {DESTINO.parent.relative_to(RAIZ)}", file=sys.stderr)


if __name__ == "__main__":
    main()
