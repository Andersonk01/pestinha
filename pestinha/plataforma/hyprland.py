"""
Linux com Hyprland: as leituras vêm do próprio compositor, pelo socket de controle dele (o mesmo que o
`hyprctl` usa), e o tempo ocioso pelo protocolo ext-idle-notify do Wayland (_ocioso_wayland.py).

No Wayland, os comandos do X11 (xdotool, wmctrl, xprintidle) só enxergam as janelas do XWayland, e um
programa não pode posicionar as próprias janelas. Por isso o pet roda pelo XWayland (preparar_qt), onde o
move() vale, e este módulo traduz as coordenadas do Hyprland para as do XWayland.

As janelinhas do pet (o pet, a bolinha, os fogos, os cartazes) levam o título TITULO_DAS_JANELAS, e as
regras de janela do Hyprland (em todos os workspaces, sem borda, sombra, animação nem foco) as acham por
ele. O Hyprland não deixa um programa ouvir o teclado dos outros: o atalho de pânico é um bind do próprio
Hyprland que chama o controle local (controle/remoto.py, ferramentas/pestinha_ctl.py).

O Hyprland manda o título das outras janelas junto com a geometria; ele é descartado aqui, como no wmctrl.
"""

import json
import os
import socket
import time
from collections import namedtuple

import psutil

from ..log import log
from ._ocioso_wayland import OciosoWayland

LARGURA_MINIMA, ALTURA_MINIMA = 120, 60
CLASSE_DAS_JANELAS = "pestinha"             # WM_CLASS (o applicationName do Qt): o que as regras do Hyprland casam
TITULO_DAS_JANELAS = "pestinha:janela"      # título das janelinhas do pet; a tela de configurações tem outro
TODAS_AS_TELAS = True                       # as coordenadas valem em todos os monitores (ver para_xwayland)
TEM_CONTROLE_LOCAL = True                   # o atalho e o painel do sistema falam com o pet por um socket local
TECLAS_DO_ATALHO = "CTRL + ALT + SHIFT + B"
AVISO_SEM_ATALHO = ("o Hyprland não tem o atalho de pânico: adicione um bind de "
                    f"{TECLAS_DO_ATALHO} que rode `ferramentas/pestinha_ctl.py panico`")

# modmask do Hyprland: SHIFT=1, CAPS=2, CTRL=4, ALT=8, MOD2=16, MOD3=32, SUPER=64, MOD5=128
_MODS_DO_ATALHO = 1 | 4 | 8
_SEM_TRAVAS = ~(2 | 16)                     # Caps Lock e Num Lock não contam

Tela = namedtuple("Tela", "nome x y largura altura px_largura px_altura xx xy fator reservado")


# ============================================================
# SOCKET DE CONTROLE DO HYPRLAND
# ============================================================


def socket_de_controle(ambiente=None):
    """Caminho do socket de pedidos do Hyprland desta sessão, ou None fora dele."""
    ambiente = os.environ if ambiente is None else ambiente
    assinatura = ambiente.get("HYPRLAND_INSTANCE_SIGNATURE") or ""
    runtime = ambiente.get("XDG_RUNTIME_DIR") or ""
    if not assinatura or not runtime or "/" in assinatura:
        return None
    return os.path.join(runtime, "hypr", assinatura, ".socket.sock")


def disponivel(ambiente=None):
    """Diz se estamos dentro de uma sessão do Hyprland (o socket dele existe)."""
    caminho = socket_de_controle(ambiente)
    return caminho is not None and os.path.exists(caminho)


def pedir_sem_cache(comando, tempo=0.5, caminho=None):
    """Resposta em JSON do Hyprland para `comando` (ex.: "clients"), ou None se não deu."""
    caminho = caminho or socket_de_controle()
    if not caminho:
        return None
    partes = []
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM | socket.SOCK_CLOEXEC) as sock:
            sock.settimeout(tempo)
            sock.connect(caminho)
            sock.sendall(f"j/{comando}".encode("utf-8"))
            while True:
                bloco = sock.recv(65536)
                if not bloco:
                    break
                partes.append(bloco)
    except OSError:
        return None
    try:
        return json.loads(b"".join(partes).decode("utf-8", "replace"))
    except ValueError:
        return None


_cache = {}


def pedir(comando, validade=0.05, relogio=time.monotonic):
    """Como pedir_sem_cache, mas reaproveita uma resposta de menos de `validade` segundos."""
    agora = relogio()
    guardado = _cache.get(comando)
    if guardado is not None and agora - guardado[0] < validade:
        return guardado[1]
    resposta = pedir_sem_cache(comando)
    _cache[comando] = (agora, resposta)
    return resposta


# ============================================================
# COORDENADAS: HYPRLAND (lógicas) -> XWAYLAND (onde o Qt do pet vive)
# ============================================================


def montar_telas(monitores, zero_scaling):
    """
    Telas na ordem do Hyprland, com o canto de cada uma no XWayland.

    O Hyprland põe os monitores do XWayland lado a lado, a partir de (0, 0), na ordem da lista. Com
    `xwayland:force_zero_scaling`, cada um ocupa o tamanho em pixels e as distâncias são multiplicadas
    pela escala; sem ele, o tamanho lógico e escala 1. Com um monitor só, sem escala, nada muda.
    """
    telas = []
    deslocamento = 0.0
    for m in monitores or []:
        if not isinstance(m, dict) or m.get("disabled"):
            continue
        try:
            px_largura, px_altura = float(m["width"]), float(m["height"])
            if int(m.get("transform", 0)) % 2 == 1:
                px_largura, px_altura = px_altura, px_largura
            escala = float(m.get("scale") or 1.0) or 1.0
            reservado = tuple(float(v) for v in (m.get("reserved") or (0, 0, 0, 0))[:4])
            if len(reservado) != 4:
                reservado = (0.0, 0.0, 0.0, 0.0)
            tela = Tela(str(m.get("name", "")), float(m["x"]), float(m["y"]),
                        px_largura / escala, px_altura / escala, px_largura, px_altura,
                        deslocamento, 0.0, escala if zero_scaling else 1.0, reservado)
        except (KeyError, TypeError, ValueError):
            continue
        telas.append(tela)
        deslocamento += px_largura if zero_scaling else tela.largura
    return telas


def _distancia2(x, y, tela, zero_scaling):
    """Distância (ao quadrado) do ponto até a tela, como o Hyprland mede para escolher a tela do ponto."""
    largura, altura = (tela.px_largura, tela.px_altura) if zero_scaling else (tela.largura, tela.altura)
    dx = max(tela.x - x, 0.0, x - (tela.x + largura - 1))
    dy = max(tela.y - y, 0.0, y - (tela.y + altura - 1))
    return dx * dx + dy * dy


def tela_do_ponto(x, y, telas):
    """A tela mais perto do ponto (a que contém, se houver)."""
    if not telas:
        return None
    zero = any(t.fator != 1.0 for t in telas)
    return min(telas, key=lambda t: _distancia2(x, y, t, zero))


def para_xwayland(x, y, telas, tela=None):
    """Ponto do Hyprland para o XWayland; sem telas conhecidas, devolve o mesmo ponto."""
    tela = tela or tela_do_ponto(x, y, telas)
    if tela is None:
        return x, y
    return tela.xx + (x - tela.x) * tela.fator, tela.xy + (y - tela.y) * tela.fator


def retangulo_para_xwayland(x, y, largura, altura, telas):
    """(l, t, r, b) no XWayland de um retângulo do Hyprland; a tela do centro decide os dois cantos."""
    tela = tela_do_ponto(x + largura / 2, y + altura / 2, telas)
    l, t = para_xwayland(x, y, telas, tela)
    r, b = para_xwayland(x + largura, y + altura, telas, tela)
    return int(round(l)), int(round(t)), int(round(r)), int(round(b))


def _zero_scaling():
    """Lê `xwayland:force_zero_scaling` (int no hyprlang, bool no config em Lua)."""
    opcao = pedir("getoption xwayland:force_zero_scaling", validade=10.0)
    if not isinstance(opcao, dict):
        return False
    return bool(opcao.get("int", opcao.get("bool", False)))


def _monitores():
    """Lista de monitores do Hyprland (reaproveitada por 2 s)."""
    monitores = pedir("monitors", validade=2.0)
    return monitores if isinstance(monitores, list) else []


def _telas():
    """Telas do Hyprland com o canto no XWayland."""
    return montar_telas(_monitores(), _zero_scaling())


def workspaces_visiveis(monitores):
    """Ids dos workspaces na tela agora: o ativo de cada monitor e o especial aberto, se houver."""
    ids = set()
    for m in monitores or []:
        if not isinstance(m, dict):
            continue
        for chave in ("activeWorkspace", "specialWorkspace"):
            ws = m.get(chave)
            if isinstance(ws, dict) and isinstance(ws.get("id"), int) and ws["id"] != 0:
                ids.add(ws["id"])
    return ids


# ============================================================
# LEITURAS (as mesmas funções dos outros sistemas)
# ============================================================


def _numero(valor):
    """Inteiro do JSON (o fullscreen já foi bool em versões antigas do Hyprland)."""
    try:
        return int(valor)
    except (TypeError, ValueError):
        return 0


def _endereco(cliente):
    """Endereço da janela no Hyprland ("0x55...") como número, ou 0."""
    try:
        return int(str(cliente.get("address", "0")), 16)
    except ValueError:
        return 0


def _geometria(cliente):
    """(x, y, largura, altura) de uma janela do Hyprland, ou None."""
    try:
        (x, y), (largura, altura) = cliente["at"], cliente["size"]
        return float(x), float(y), float(largura), float(altura)
    except (KeyError, TypeError, ValueError):
        return None


def parse_clientes(clientes, monitores, telas, meu_pid, excluir):
    """
    [(endereço, (l, t, r, b), maximizada)] das janelas visíveis, de cima para baixo, no XWayland.

    O Hyprland não diz a ordem de empilhamento: tela cheia fica por cima de tudo, depois as fixadas,
    as flutuantes e as do mosaico; dentro de cada grupo, a que teve foco por último fica em cima.
    O título vem junto no JSON e é ignorado.
    """
    visiveis = workspaces_visiveis(monitores)
    achadas = []
    for c in clientes or []:
        if not isinstance(c, dict) or not c.get("mapped", True) or c.get("hidden"):
            continue
        if c.get("pid") == meu_pid:
            continue
        ws = (c.get("workspace") or {}).get("id")
        if ws not in visiveis and not c.get("pinned"):
            continue
        geometria = _geometria(c)
        if geometria is None:
            continue
        x, y, largura, altura = geometria
        if largura < LARGURA_MINIMA or altura < ALTURA_MINIMA:
            continue
        endereco = _endereco(c)
        if endereco in excluir:
            continue
        tela_cheia = _numero(c.get("fullscreen"))
        grupo = 0 if tela_cheia >= 2 else 1 if c.get("pinned") else 2 if c.get("floating") else 3
        foco = _numero(c.get("focusHistoryID", 999))
        foco = foco if foco >= 0 else 999
        rect = retangulo_para_xwayland(x, y, largura, altura, telas)
        achadas.append(((grupo, foco), (endereco, rect, tela_cheia != 0)))
    achadas.sort(key=lambda item: item[0])
    return [janela for _, janela in achadas]


def janelas_visiveis(excluir, escala=1.0):
    """Janelas visíveis de outros programas, de cima para baixo (sem as do próprio pet)."""
    return parse_clientes(pedir("clients", validade=0.2), _monitores(), _telas(), os.getpid(), excluir)


def _ativa():
    """A janela em primeiro plano (dict do Hyprland), ou None se não houver ou for do próprio pet."""
    ativa = pedir("activewindow", validade=0.1)
    if not isinstance(ativa, dict) or not ativa or ativa.get("pid") == os.getpid():
        return None
    return ativa


def retangulo_ativo(escala=1.0):
    """Retângulo da janela ativa no XWayland, ou None."""
    ativa = _ativa()
    geometria = _geometria(ativa) if ativa else None
    if geometria is None:
        return None
    return retangulo_para_xwayland(*geometria, _telas())


def cobre_a_tela(ativa, telas):
    """Diz se a janela é tela cheia de verdade (não só maximizada) ou cobre um monitor inteiro."""
    if _numero(ativa.get("fullscreen")) >= 2:
        return True
    geometria = _geometria(ativa)
    if geometria is None:
        return False
    x, y, largura, altura = geometria
    for t in telas:
        if x <= t.x and y <= t.y and x + largura >= t.x + t.largura and y + altura >= t.y + t.altura:
            return True
    return False


def tela_cheia():
    """A janela em primeiro plano está em tela cheia (jogo, vídeo, apresentação)."""
    ativa = _ativa()
    return bool(ativa) and cobre_a_tela(ativa, _telas())


def processo_ativo():
    """Nome do programa da janela ativa (pelo pid e o psutil; a classe da janela, se o pid falhar)."""
    ativa = _ativa()
    if not ativa:
        return "unknown"
    try:
        return psutil.Process(int(ativa.get("pid"))).name().lower()
    except (TypeError, ValueError, psutil.Error):
        return str(ativa.get("class") or "unknown").lower()


_ocioso = None


def ocioso_segundos():
    """Segundos sem teclado e mouse (protocolo ext-idle-notify); 0 se o compositor não oferecer."""
    global _ocioso
    if _ocioso is None:
        _ocioso = OciosoWayland()
        if not _ocioso.iniciar(esperar=0.5):
            log("[ocioso] o compositor não ofereceu o ext-idle-notify: fica como se você estivesse sempre ativo")
    return _ocioso.segundos()


def posicao_cursor():
    """Cursor no XWayland, lido do Hyprland: o Qt só vê o cursor quando ele passa por uma janela do pet."""
    pos = pedir("cursorpos", validade=0.03)
    try:
        x, y = float(pos["x"]), float(pos["y"])
    except (KeyError, TypeError, ValueError):
        return None
    x, y = para_xwayland(x, y, _telas())
    return int(round(x)), int(round(y))


def areas_uteis():
    """{nome do monitor: (l, t, r, b)} no XWayland, sem o que a barra e o dock reservam."""
    areas = {}
    for t in _telas():
        esquerda, topo, direita, baixo = t.reservado
        l, top = para_xwayland(t.x + esquerda, t.y + topo, [t], t)
        r, b = para_xwayland(t.x + t.largura - direita, t.y + t.altura - baixo, [t], t)
        if r > l and b > top:
            areas[t.nome] = (int(round(l)), int(round(top)), int(round(r)), int(round(b)))
    return areas


def sem_foco_nativo(janela_id):
    """Quem tira o foco é a regra de janela do Hyprland (no_focus), achada pelo título."""


def atalho_configurado(binds=None):
    """Diz se o Hyprland tem um bind de Ctrl+Alt+Shift+B (o que chama o pânico)."""
    binds = pedir("binds", validade=0.0) if binds is None else binds
    for b in binds or []:
        if not isinstance(b, dict):
            continue
        if _numero(b.get("modmask")) & _SEM_TRAVAS == _MODS_DO_ATALHO and str(b.get("key", "")).lower() == "b":
            return True
    return False


def iniciar_atalho(callback):
    """O atalho é do Hyprland (um bind que chama o controle local); devolve True se o bind existe."""
    return atalho_configurado()


def preparar_qt(ambiente=None):
    """
    Antes do QApplication: o pet roda pelo XWayland, onde as janelas podem se posicionar sozinhas.
    PESTINHA_QPA escolhe outra plataforma do Qt (ex.: "wayland", para testar).
    """
    ambiente = os.environ if ambiente is None else ambiente
    escolhida = ambiente.get("PESTINHA_QPA") or ""
    if escolhida:
        ambiente["QT_QPA_PLATFORM"] = escolhida
    elif ambiente.get("DISPLAY"):
        ambiente["QT_QPA_PLATFORM"] = "xcb"
    else:
        log("[hyprland] sem XWayland (DISPLAY vazio): o pet não consegue se mover pela tela")
