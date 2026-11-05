"""
PLATAFORMA - a única parte do código que conhece o sistema operacional.

Cada sistema tem um módulo com as mesmas funções (windows.py, macos.py, linux.py, hyprland.py). Este
arquivo escolhe o certo na importação: no Linux, hyprland.py quando a sessão é do Hyprland e linux.py
(X11) nos outros casos; PESTINHA_PLATAFORMA=x11 ou =hyprland força um deles (os testes usam x11).
Os retângulos são em pixels físicos (o app divide pelo dpr).

    ocioso_segundos()            segundos desde o último teclado ou mouse
    processo_ativo()             nome (minúsculo) do programa em primeiro plano
    retangulo_ativo(escala)      retângulo da janela em primeiro plano, ou None
    tela_cheia()                 a janela em primeiro plano cobre o monitor inteiro
    janelas_visiveis(excluir, escala)   [(id, (l, t, r, b), maximizada)] de cima para baixo
    sem_foco_nativo(janela_id)   a janela do pet não rouba o foco (quando o sistema permite)
    iniciar_atalho(callback)     Ctrl+Alt+Shift+B; devolve True se registrou

Opcionais (quem não tem fica com o padrão do Qt):
    preparar_qt()                antes do QApplication (o Hyprland escolhe o XWayland)
    posicao_cursor()             cursor em pixels físicos, ou None para usar o do Qt
    areas_uteis()                {nome da tela: (l, t, r, b)} sem as barras, ou {} para usar o do Qt
    CLASSE_DAS_JANELAS           nome do programa para o sistema (WM_CLASS), ou ""
    TITULO_DAS_JANELAS           começo do título das janelinhas do pet (regras do compositor), ou ""
    trazer_para_frente(titulo)   põe a janela por cima quando o raise() do Qt não basta
    TODAS_AS_TELAS               as coordenadas valem em todos os monitores (não só no principal)
    TEM_CONTROLE_LOCAL           liga o controle local (controle/remoto.py)
    AVISO_SEM_ATALHO             o aviso quando o atalho de pânico não registrou

Só no Windows, por enquanto (TEM_INICIO_AUTOMATICO diz se existe):
    inicia_com_sistema()         o programa está marcado para abrir ao entrar no sistema
    definir_inicio_com_sistema(ligado)   liga ou desliga isso; devolve True se conseguiu

Igual em todos (_som.py):
    Tocador                      toca .wav sem travar (pw-play, paplay, aplay, afplay ou winsound)
"""

import os
import sys

if sys.platform == "win32":
    from . import windows as _backend
elif sys.platform == "darwin":
    from . import macos as _backend
else:
    from . import hyprland as _hyprland
    _pedido = os.environ.get("PESTINHA_PLATAFORMA", "").strip().lower()
    if _pedido != "x11" and (_pedido == "hyprland" or _hyprland.disponivel()):
        _backend = _hyprland
    else:
        from . import linux as _backend

NOME_DO_SISTEMA = {"win32": "Windows", "darwin": "macOS"}.get(sys.platform, "Linux")
NOME_DA_SESSAO = "Hyprland" if _backend.__name__.endswith(".hyprland") else NOME_DO_SISTEMA

ocioso_segundos = _backend.ocioso_segundos
processo_ativo = _backend.processo_ativo
retangulo_ativo = _backend.retangulo_ativo
tela_cheia = _backend.tela_cheia
janelas_visiveis = _backend.janelas_visiveis
sem_foco_nativo = _backend.sem_foco_nativo
iniciar_atalho = _backend.iniciar_atalho

preparar_qt = getattr(_backend, "preparar_qt", lambda: None)
posicao_cursor = getattr(_backend, "posicao_cursor", lambda: None)
areas_uteis = getattr(_backend, "areas_uteis", dict)
CLASSE_DAS_JANELAS = getattr(_backend, "CLASSE_DAS_JANELAS", "")
TITULO_DAS_JANELAS = getattr(_backend, "TITULO_DAS_JANELAS", "")
trazer_para_frente = getattr(_backend, "trazer_para_frente", lambda titulo: False)
TODAS_AS_TELAS = getattr(_backend, "TODAS_AS_TELAS", sys.platform == "win32")
TEM_CONTROLE_LOCAL = getattr(_backend, "TEM_CONTROLE_LOCAL", False)
AVISO_SEM_ATALHO = getattr(_backend, "AVISO_SEM_ATALHO", "")

TEM_INICIO_AUTOMATICO = hasattr(_backend, "definir_inicio_com_sistema")
from ._som import Tocador  # noqa: E402  (o mesmo em todo sistema: escolhe pw-play, afplay, winsound...)

inicia_com_sistema = getattr(_backend, "inicia_com_sistema", lambda: False)
definir_inicio_com_sistema = getattr(_backend, "definir_inicio_com_sistema", lambda ligado: False)
