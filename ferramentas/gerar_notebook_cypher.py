#!/usr/bin/env python3
"""
Desenha o notebook do Cypher (pets/cypher/notebook.png): o verso da tampa, escuro, com um cadeado ciano
brilhando no meio e adesivos de hacker. Mesma proporção da foto de assets/comum/notebook.png, para ele
sentar atrás do mesmo jeito.

    python ferramentas/gerar_notebook_cypher.py

Roda sem tela (QT_QPA_PLATFORM=offscreen). Sem fonte nenhuma de terceiros: só as do sistema.
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPointF, QRectF, Qt  # noqa: E402
from PySide6.QtGui import (  # noqa: E402
    QColor, QFont, QGuiApplication, QImage, QLinearGradient, QPainter, QPen, QRadialGradient,
)

RAIZ = Path(__file__).resolve().parent.parent
LARGURA, ALTURA = 600, 442                       # 1154 x 850 da foto comum, reduzido
CIANO, VERDE, MAGENTA = QColor("#6EE7F9"), QColor("#34D399"), QColor("#FF2BD6")


def fonte(px, peso=QFont.Bold):
    f = QFont("monospace")
    f.setStyleHint(QFont.Monospace)
    f.setPixelSize(px)
    f.setWeight(peso)
    return f


def adesivo(p, centro, angulo, tamanho, fundo, texto, cor_texto, borda=None, px=30):
    p.save()
    p.translate(centro)
    p.rotate(angulo)
    r = QRectF(-tamanho[0] / 2, -tamanho[1] / 2, *tamanho)
    p.setPen(QPen(borda or fundo.darker(130), 3))
    p.setBrush(fundo)
    p.drawRoundedRect(r, 12, 12)
    p.setPen(cor_texto)
    p.setFont(fonte(px))
    p.drawText(r, Qt.AlignCenter, texto)
    p.restore()


def cadeado(p, centro):
    p.save()
    p.translate(centro)
    brilho = QRadialGradient(QPointF(0, 6), 120)
    halo = QColor(CIANO)
    for parada, alfa in ((0.0, 110), (0.45, 40), (1.0, 0)):
        halo.setAlpha(alfa)
        brilho.setColorAt(parada, halo)
    p.setPen(Qt.NoPen)
    p.setBrush(brilho)
    p.drawEllipse(QPointF(0, 6), 120, 120)
    p.setBrush(Qt.NoBrush)
    p.setPen(QPen(CIANO, 12, Qt.SolidLine, Qt.RoundCap))
    p.drawArc(QRectF(-34, -64, 68, 76), 0, 180 * 16)            # a alça
    p.drawLine(QPointF(-34, -26), QPointF(-34, -6))
    p.drawLine(QPointF(34, -26), QPointF(34, -6))
    p.setPen(Qt.NoPen)
    p.setBrush(CIANO)
    p.drawRoundedRect(QRectF(-54, -12, 108, 84), 14, 14)
    p.setBrush(QColor("#0b1016"))                                # o buraco da chave
    p.drawEllipse(QPointF(0, 18), 11, 11)
    p.drawRoundedRect(QRectF(-5, 18, 10, 30), 2, 2)
    p.restore()


def desenhar():
    img = QImage(LARGURA, ALTURA, QImage.Format_ARGB32)
    img.fill(0)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    p.setRenderHint(QPainter.TextAntialiasing)

    tampa = QRectF(14, 8, LARGURA - 28, ALTURA - 58)
    grad = QLinearGradient(tampa.topLeft(), tampa.bottomLeft())
    grad.setColorAt(0.0, QColor("#1b222c"))
    grad.setColorAt(1.0, QColor("#0d1117"))
    p.setPen(QPen(QColor("#2b3542"), 3))
    p.setBrush(grad)
    p.drawRoundedRect(tampa, 24, 24)
    p.setPen(QPen(QColor(255, 255, 255, 18), 2))                 # reflexo na borda de cima
    p.drawLine(QPointF(tampa.left() + 30, tampa.top() + 6), QPointF(tampa.right() - 30, tampa.top() + 6))

    cadeado(p, QPointF(LARGURA / 2, tampa.center().y() - 6))
    adesivo(p, QPointF(118, 92), -9, (150, 64), VERDE, "sudo", QColor("#04130c"), px=34)
    adesivo(p, QPointF(488, 96), 11, (112, 70), MAGENTA, "</>", QColor("#1a0416"), px=36)
    adesivo(p, QPointF(126, 300), 6, (176, 48), QColor("#0b1016"), "0xC0FFEE", CIANO, borda=CIANO, px=24)
    adesivo(p, QPointF(472, 302), -6, (170, 54), QColor("#111a24"), "root@pet", VERDE, borda=QColor("#2b3542"),
            px=24)

    base = QRectF(0, ALTURA - 50, LARGURA, 40)
    grad = QLinearGradient(base.topLeft(), base.bottomLeft())
    grad.setColorAt(0.0, QColor("#3b4452"))
    grad.setColorAt(1.0, QColor("#1c2129"))
    p.setPen(QPen(QColor("#12161c"), 2))
    p.setBrush(grad)
    p.drawRoundedRect(base, 14, 14)
    p.setPen(Qt.NoPen)
    p.setBrush(QColor("#151a21"))
    p.drawRoundedRect(QRectF(LARGURA / 2 - 60, ALTURA - 50, 120, 10), 4, 4)   # o vão da dobradiça
    p.end()
    return img


def main():
    QGuiApplication.instance() or QGuiApplication(sys.argv[:1])
    destino = RAIZ / "pets" / "cypher" / "notebook.png"
    destino.parent.mkdir(parents=True, exist_ok=True)
    if not desenhar().save(str(destino)):
        sys.exit(f"não consegui gravar {destino}")
    print(f"notebook gravado em {destino.relative_to(RAIZ)}", file=sys.stderr)


if __name__ == "__main__":
    main()
