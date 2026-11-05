"""
ESTILOS - paletas que valem por cima das cores do personagem (a escolha "estilo" das configurações).

O estilo troca as cores do corpo e os efeitos da tela; os acessórios continuam os do personagem (um
acessório com a cor "moldura", "olho" ou "brilho" acompanha a paleta nova). "original" deixa tudo
como está no pets/<pet>.json. Os nomes válidos ficam em config.ESTILOS.
"""

from dataclasses import replace

from PySide6.QtGui import QColor

from .desenho_rosto import CAMPOS_DE_COR

PALETAS = {
    # rosa-chiclete, sem efeitos
    "rosa": dict(moldura="#ff6fb5", casca="#1a0f16", tela="#26121e", olho="#ff8fcb", brilho="#ffe3f1",
                 efeitos=()),
    # o da intro do Ryoku: ciano #6EE7F9, chuva verde #34D399, scanlines e glitch magenta/ciano
    "cyber": dict(moldura="#6EE7F9", casca="#05080c", tela="#08111a", olho="#6EE7F9", brilho="#e6fbff",
                  codigo="#34D399", efeitos=("chuva", "scanlines", "glitch")),
    # terminal verde, com a chuva de código
    "matrix": dict(moldura="#00e85c", casca="#020a04", tela="#03120a", olho="#39ff88", brilho="#d6ffe6",
                   codigo="#00c853", efeitos=("chuva", "scanlines")),
    # monitor âmbar antigo
    "ambar": dict(moldura="#ffb000", casca="#120c02", tela="#1a1204", olho="#ffc23d", brilho="#fff0c8",
                  efeitos=("scanlines",)),
}


def com_estilo(base, nome):
    """A aparência do personagem com o estilo `nome`; "original" ou um nome desconhecido devolvem a base."""
    paleta = PALETAS.get(nome)
    if paleta is None:
        return base
    cores = {k: QColor(paleta[k]) for k in CAMPOS_DE_COR}
    codigo = QColor(paleta["codigo"]) if "codigo" in paleta else None
    return replace(base, **cores, codigo=codigo, efeitos=frozenset(paleta["efeitos"]))
