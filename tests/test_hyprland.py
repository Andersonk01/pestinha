"""
Backend do Hyprland (pestinha/plataforma/hyprland.py), o tempo ocioso pelo Wayland
(_ocioso_wayland.py), o controle local (controle/remoto.py) e o ferramentas/pestinha_ctl.py.

Nada aqui precisa do Hyprland: as respostas dele são exemplos em JSON e os sockets são falsos,
abertos numa pasta temporária.
"""
import json
import os
import socket
import struct
import sys
import threading
from pathlib import Path
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ferramentas"))

import pytest  # noqa: E402

from pestinha import config  # noqa: E402
from pestinha.plataforma import _ocioso_wayland as ow  # noqa: E402
from pestinha.plataforma import hyprland  # noqa: E402
from pestinha.controle import remoto  # noqa: E402
import pestinha_ctl  # noqa: E402

MEU_PID = 4242

UM_MONITOR = [{
    "id": 0, "name": "eDP-1", "x": 0, "y": 0, "width": 1920, "height": 1080, "scale": 1, "transform": 0,
    "reserved": [0, 36, 0, 0], "activeWorkspace": {"id": 1, "name": "1"},
    "specialWorkspace": {"address": "", "type": "", "name": ""},
}]


def cliente(endereco, x, y, w, h, ws=1, pid=100, floating=False, foco=0, **extra):
    base = {"address": endereco, "at": [x, y], "size": [w, h], "workspace": {"id": ws}, "pid": pid,
            "floating": floating, "focusHistoryID": foco, "mapped": True, "hidden": False,
            "fullscreen": 0, "pinned": False, "title": "um documento privado", "class": "kitty"}
    base.update(extra)
    return base


# ------------------------------------------------------------------ socket e escolha do backend


def test_socket_de_controle_so_dentro_do_hyprland(tmp_path):
    amb = {"HYPRLAND_INSTANCE_SIGNATURE": "abc_123", "XDG_RUNTIME_DIR": str(tmp_path)}
    caminho = hyprland.socket_de_controle(amb)
    assert caminho == str(tmp_path / "hypr" / "abc_123" / ".socket.sock")
    assert not hyprland.disponivel(amb)
    (tmp_path / "hypr" / "abc_123").mkdir(parents=True)
    Path(caminho).touch()
    assert hyprland.disponivel(amb)
    assert hyprland.socket_de_controle({"XDG_RUNTIME_DIR": str(tmp_path)}) is None
    assert hyprland.socket_de_controle({"HYPRLAND_INSTANCE_SIGNATURE": "../x", "XDG_RUNTIME_DIR": "/r"}) is None


def servidor_falso(caminho, respostas, recebidos):
    """Um 'Hyprland' que responde um pedido por conexão e fecha, como o de verdade."""
    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    srv.bind(str(caminho))
    srv.listen(8)

    def laco():
        while True:
            try:
                conexao, _ = srv.accept()
            except OSError:
                return
            with conexao:
                pedido = conexao.recv(4096).decode()
                recebidos.append(pedido)
                conexao.sendall(respostas.get(pedido, "unknown request").encode())

    threading.Thread(target=laco, daemon=True).start()
    return srv


def test_pedir_fala_o_protocolo_do_hyprctl(tmp_path):
    caminho = tmp_path / "h.sock"
    recebidos = []
    srv = servidor_falso(caminho, {"j/cursorpos": '{"x": 10, "y": 20}'}, recebidos)
    try:
        assert hyprland.pedir_sem_cache("cursorpos", caminho=str(caminho)) == {"x": 10, "y": 20}
        assert hyprland.pedir_sem_cache("nada", caminho=str(caminho)) is None     # não é JSON
        assert recebidos == ["j/cursorpos", "j/nada"]
    finally:
        srv.close()
    assert hyprland.pedir_sem_cache("cursorpos", caminho=str(tmp_path / "nao-existe")) is None


def test_pedir_reaproveita_a_resposta_por_um_tempo(monkeypatch):
    chamadas = []
    monkeypatch.setattr(hyprland, "pedir_sem_cache", lambda cmd: chamadas.append(cmd) or {"n": len(chamadas)})
    monkeypatch.setattr(hyprland, "_cache", {})
    relogio = iter([0.0, 0.01, 0.2]).__next__
    assert hyprland.pedir("clients", validade=0.1, relogio=relogio) == {"n": 1}
    assert hyprland.pedir("clients", validade=0.1, relogio=relogio) == {"n": 1}
    assert hyprland.pedir("clients", validade=0.1, relogio=relogio) == {"n": 2}


# ------------------------------------------------------------------ coordenadas


def test_um_monitor_sem_escala_nao_muda_nada():
    telas = hyprland.montar_telas(UM_MONITOR, zero_scaling=True)
    assert [t.nome for t in telas] == ["eDP-1"]
    assert hyprland.para_xwayland(789, 769, telas) == (789, 769)
    assert hyprland.retangulo_para_xwayland(18, 54, 1884, 1008, telas) == (18, 54, 1902, 1062)


def test_xwayland_poe_os_monitores_lado_a_lado_com_a_escala():
    monitores = [
        {"name": "eDP-1", "x": 0, "y": 0, "width": 2880, "height": 1800, "scale": 2, "transform": 0},
        {"name": "HDMI-A-1", "x": 1440, "y": -200, "width": 1920, "height": 1080, "scale": 1, "transform": 0},
    ]
    zero = hyprland.montar_telas(monitores, zero_scaling=True)
    assert [(t.xx, t.xy, t.fator) for t in zero] == [(0, 0, 2.0), (2880, 0, 1.0)]
    assert hyprland.para_xwayland(100, 50, zero) == (200, 100)              # dentro do eDP, em pixels
    assert hyprland.para_xwayland(1440 + 10, -200 + 5, zero) == (2890, 5)   # o HDMI começa em 2880
    sem_zero = hyprland.montar_telas(monitores, zero_scaling=False)
    assert [(t.xx, t.fator) for t in sem_zero] == [(0, 1.0), (1440, 1.0)]
    assert hyprland.para_xwayland(100, 50, sem_zero) == (100, 50)


def test_monitor_girado_troca_largura_e_altura():
    girado = [{"name": "DP-1", "x": 0, "y": 0, "width": 1920, "height": 1080, "scale": 1, "transform": 1}]
    tela = hyprland.montar_telas(girado, zero_scaling=False)[0]
    assert (tela.largura, tela.altura) == (1080, 1920)


def test_monitor_quebrado_e_ignorado():
    assert hyprland.montar_telas([{"name": "x"}, "lixo", None], zero_scaling=False) == []
    assert hyprland.para_xwayland(5, 6, []) == (5, 6)


def test_area_util_tira_a_barra(monkeypatch):
    monkeypatch.setattr(hyprland, "_telas", lambda: hyprland.montar_telas(UM_MONITOR, True))
    assert hyprland.areas_uteis() == {"eDP-1": (0, 36, 1920, 1080)}


# ------------------------------------------------------------------ janelas


def test_janelas_visiveis_filtra_e_ordena_de_cima_para_baixo():
    telas = hyprland.montar_telas(UM_MONITOR, True)
    clientes = [
        cliente("0x10", 18, 54, 1884, 1008, foco=1),                         # mosaico, foco antigo
        cliente("0x20", 300, 200, 800, 500, floating=True, foco=2),          # flutuante
        cliente("0x30", 0, 0, 1920, 1080, ws=2),                              # outro workspace
        cliente("0x40", 10, 10, 50, 50, floating=True),                       # pequena demais
        cliente("0x50", 100, 100, 400, 300, pid=MEU_PID),                     # o próprio pet
        cliente("0x60", 100, 100, 400, 300, hidden=True),                     # aba escondida do grupo
        cliente("0x70", 100, 100, 400, 300, mapped=False),
        cliente("0x80", 500, 500, 300, 200, ws=7, pinned=True, floating=True),  # fixada: em todo lugar
        cliente("0x90", 0, 0, 1920, 1080, fullscreen=2, foco=0),             # tela cheia, por cima
        cliente("0xa0", 50, 60, 300, 300, floating=True, foco=5),
    ]
    achadas = hyprland.parse_clientes(clientes, UM_MONITOR, telas, MEU_PID, excluir={0xA0})
    assert [hex(e) for e, _, _ in achadas] == ["0x90", "0x80", "0x20", "0x10"]
    assert achadas[0][2] is True and achadas[3][2] is False                 # tela cheia conta como maximizada
    assert achadas[3][1] == (18, 54, 1902, 1062)
    assert all("documento" not in repr(j) for j in achadas)                 # o título nunca sai daqui


def test_workspace_especial_aberto_tambem_conta():
    monitores = [dict(UM_MONITOR[0], specialWorkspace={"id": -98, "name": "special:magic"})]
    assert hyprland.workspaces_visiveis(monitores) == {1, -98}
    assert hyprland.workspaces_visiveis(UM_MONITOR) == {1}


def test_tela_cheia_de_verdade_e_maximizada():
    telas = hyprland.montar_telas(UM_MONITOR, True)
    assert hyprland.cobre_a_tela({"fullscreen": 2, "at": [0, 0], "size": [10, 10]}, telas)
    assert not hyprland.cobre_a_tela({"fullscreen": 1, "at": [18, 54], "size": [1884, 1008]}, telas)
    assert hyprland.cobre_a_tela({"fullscreen": 0, "at": [0, 0], "size": [1920, 1080]}, telas)   # jogo sem borda
    assert not hyprland.cobre_a_tela({"fullscreen": False, "at": [0, 0], "size": [800, 600]}, telas)


def test_processo_ativo_usa_o_pid_e_cai_na_classe(monkeypatch):
    monkeypatch.setattr(hyprland, "_ativa", lambda: {"pid": os.getpid(), "class": "Algo"})
    assert hyprland.processo_ativo().startswith("python")
    monkeypatch.setattr(hyprland, "_ativa", lambda: {"pid": "x", "class": "Zen"})
    assert hyprland.processo_ativo() == "zen"
    monkeypatch.setattr(hyprland, "_ativa", lambda: None)
    assert hyprland.processo_ativo() == "unknown"


def test_atalho_do_hyprland_ignora_caps_e_num_lock():
    bind = {"modmask": 13, "key": "B"}
    assert hyprland.atalho_configurado([bind])
    assert hyprland.atalho_configurado([dict(bind, modmask=13 | 16)])       # Num Lock ligado
    assert not hyprland.atalho_configurado([dict(bind, modmask=12)])        # sem o Shift
    assert not hyprland.atalho_configurado([dict(bind, key="N")])
    assert not hyprland.atalho_configurado([])


def test_preparar_qt_escolhe_o_xwayland():
    amb = {"DISPLAY": ":0", "QT_QPA_PLATFORM": "wayland;xcb"}
    hyprland.preparar_qt(amb)
    assert amb["QT_QPA_PLATFORM"] == "xcb"
    amb = {"DISPLAY": ":0", "PESTINHA_QPA": "wayland"}
    hyprland.preparar_qt(amb)
    assert amb["QT_QPA_PLATFORM"] == "wayland"
    amb = {"QT_QPA_PLATFORM": "wayland"}
    hyprland.preparar_qt(amb)                                               # sem XWayland: deixa como está
    assert amb["QT_QPA_PLATFORM"] == "wayland"


def test_por_cima_nas_duas_configs_do_hyprland(monkeypatch):
    lua, antigo = hyprland.comandos_para_frente("pestinha:janela:notebook")
    assert lua == ("dispatch hl.dsp.window.alter_zorder({ mode = 'top', "
                   "window = 'title:^pestinha:janela:notebook$' })")
    assert antigo == "dispatch alterzorder top,title:^pestinha:janela:notebook$"
    assert "\\'" in hyprland.comandos_para_frente("a'b")[0]                    # aspas escapadas no Lua

    enviados = []
    monkeypatch.setattr(hyprland, "conversar", lambda msg: enviados.append(msg) or
                        ("ok" if msg.startswith("dispatch alterzorder") else "error: lua"))
    monkeypatch.setattr(hyprland, "_ultimo_para_frente", {})
    monkeypatch.setattr(hyprland, "_comando_que_vale", None)
    agora = [10.0]
    assert hyprland.trazer_para_frente("pestinha:janela:notebook", relogio=lambda: agora[0])
    assert [m.split()[1] for m in enviados] == ["hl.dsp.window.alter_zorder({", "alterzorder"]
    agora[0] += 0.5
    assert hyprland.trazer_para_frente("pestinha:janela:notebook", relogio=lambda: agora[0])
    assert len(enviados) == 2                                               # menos de 1 s: não pede de novo
    agora[0] += 1.0
    hyprland.trazer_para_frente("pestinha:janela:notebook", relogio=lambda: agora[0])
    assert enviados[-1].startswith("dispatch alterzorder") and len(enviados) == 3   # já sabe qual vale
    assert not hyprland.trazer_para_frente("")


def test_mesmas_funcoes_dos_outros_sistemas():
    for nome in ["ocioso_segundos", "processo_ativo", "retangulo_ativo", "tela_cheia",
                 "janelas_visiveis", "sem_foco_nativo", "iniciar_atalho"]:
        assert callable(getattr(hyprland, nome)), nome


# ------------------------------------------------------------------ tempo ocioso (Wayland)


def evento_global(nome, interface, versao):
    return ow.mensagem(2, 0, struct.pack("=I", nome) + ow.string(interface) + struct.pack("=I", versao))


def test_mensagens_do_wayland_chegam_em_pedacos():
    leitor = ow.Mensagens()
    dados = evento_global(7, "wl_seat", 9) + ow.mensagem(6, 0)
    assert leitor.alimentar(dados[:5]) == []
    saida = leitor.alimentar(dados[5:])
    assert [(o, op) for o, op, _ in saida] == [(2, 0), (6, 0)]
    texto, _ = ow.ler_string(saida[0][2], 4)
    assert texto == "wl_seat"
    with pytest.raises(ValueError):
        ow.Mensagens().alimentar(struct.pack("=II", 1, 4 << 16))


def test_ocioso_assina_o_aviso_e_conta_o_tempo():
    agora = [100.0]
    o = ow.OciosoWayland(limiar_ms=300, relogio=lambda: agora[0])
    enviados = []
    globais = {}
    for dados in (evento_global(3, "wl_compositor", 6), evento_global(7, "wl_seat", 9),
                  evento_global(9, "ext_idle_notifier_v1", 2)):
        for objeto, opcode, args in ow.Mensagens().alimentar(dados):
            assert o.tratar(objeto, opcode, args, globais, enviados.append)
    assert set(globais) == {"wl_seat", "ext_idle_notifier_v1"}
    assert o.tratar(3, 0, b"", globais, enviados.append)                    # fim da lista de globais
    assert o.disponivel and o.versao == 2
    pedidos = ow.Mensagens().alimentar(enviados[0])
    assert [(obj, op) for obj, op, _ in pedidos] == [(2, 0), (2, 0), (5, 2)]     # dois binds e o "input idle"
    assert struct.unpack("=III", pedidos[2][2]) == (6, 300, 4)
    assert o.segundos() == 0.0
    o.tratar(6, 0, b"", globais, enviados.append)                           # parado há 0,3 s
    agora[0] += 2.0
    assert o.segundos() == pytest.approx(2.3)
    o.tratar(6, 1, b"", globais, enviados.append)                           # voltou
    assert o.segundos() == 0.0


def test_ocioso_sem_o_protocolo_desiste():
    o = ow.OciosoWayland()
    globais = {"wl_seat": (7, 9)}
    assert not o.tratar(3, 0, b"", globais, lambda dados: None)
    assert not o.disponivel and o.segundos() == 0.0


def test_ocioso_conversa_com_um_compositor_falso(tmp_path):
    caminho = str(tmp_path / "wayland-9")
    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    srv.bind(caminho)
    srv.listen(1)
    recebido = []

    def compositor():
        conexao, _ = srv.accept()
        with conexao:
            recebido.append(conexao.recv(4096))                            # get_registry + sync
            conexao.sendall(evento_global(7, "wl_seat", 9) + evento_global(9, "ext_idle_notifier_v1", 1)
                            + ow.mensagem(3, 0, struct.pack("=I", 0)))
            recebido.append(conexao.recv(4096))                            # binds + get_idle_notification
            conexao.sendall(ow.mensagem(6, 0))                             # idled
            conexao.recv(1)                                                # espera o cliente fechar

    threading.Thread(target=compositor, daemon=True).start()
    o = ow.OciosoWayland(limiar_ms=500)
    try:
        assert o.iniciar(caminho, esperar=2.0)
        assert o.versao == 1
        for _ in range(200):
            if o.segundos() > 0:
                break
            threading.Event().wait(0.01)
        assert o.segundos() >= 0.5
        pedidos = ow.Mensagens().alimentar(recebido[1])
        assert pedidos[-1][:2] == (5, 1)                                    # versão 1: get_idle_notification
    finally:
        o.parar()
        srv.close()


def test_caminho_do_socket_wayland():
    assert ow.caminho_do_socket({"WAYLAND_DISPLAY": "wayland-1", "XDG_RUNTIME_DIR": "/run/user/1"}) == \
        "/run/user/1/wayland-1"
    assert ow.caminho_do_socket({"WAYLAND_DISPLAY": "/tmp/w"}) == "/tmp/w"
    assert ow.caminho_do_socket({}) is None


# ------------------------------------------------------------------ controle local


class AppFalso:
    def __init__(self):
        self.perms = dict(config.DEFAULT_PERMISSIONS, configurado=True)
        self.nome = "Bryan"
        self.paused = False
        self.hidden = False
        self.hotkey = SimpleNamespace(ok=True)
        self.settings = None
        self.chamadas = []

    def apply_perms(self, novos):
        self.chamadas.append(("perms", novos))
        self.perms.update(novos)

    def panic(self):
        self.chamadas.append(("panico",))
        self.perms["ativo"] = False

    def open_settings(self):
        self.chamadas.append(("configuracoes",))

    def toggle_pause(self):
        self.paused = not self.paused

    def toggle_hidden(self):
        self.hidden = not self.hidden


def test_controle_status_nao_mostra_o_que_nao_e_do_pet():
    resposta = remoto.executar(AppFalso(), {"cmd": "status"})
    assert resposta["ok"] and resposta["pet"] == "bryan" and resposta["ativo"] is True
    assert "configurado" not in resposta["perms"] and "ativo" not in resposta["perms"]
    assert resposta["perms"]["bolinha"] is True
    json.dumps(resposta)                                                   # vira JSON sem problema


def test_controle_muda_permissoes_e_recusa_as_de_sessao():
    app = AppFalso()
    resposta = remoto.executar(app, {"cmd": "perms", "valores": {"bolinha": False, "ativo": False,
                                                                 "pet": "jorge", "memes": "sim",
                                                                 "inventada": True}})
    assert app.chamadas == [("perms", {"bolinha": False})]
    assert resposta["perms"]["bolinha"] is False and app.perms["ativo"] is True
    assert resposta["ignorados"] == ["ativo", "inventada", "memes", "pet"]
    assert not remoto.executar(app, {"cmd": "perms"})["ok"]


def test_controle_panico_e_religar():
    app = AppFalso()
    assert remoto.executar(app, {"cmd": "panico"})["ativo"] is False
    assert remoto.executar(app, {"cmd": "panico"})["ativo"] is False       # o segundo não faz nada
    assert app.chamadas == [("panico",)]
    assert remoto.executar(app, {"cmd": "religar"})["ativo"] is True
    assert app.chamadas[-1] == ("perms", {"ativo": True})


def test_controle_alterna_e_recusa_o_desconhecido():
    app = AppFalso()
    assert remoto.executar(app, {"cmd": "pausar"})["pausado"] is True
    assert remoto.executar(app, {"cmd": "esconder"})["escondido"] is True
    remoto.executar(app, {"cmd": "configuracoes"})
    assert ("configuracoes",) in app.chamadas
    assert not remoto.executar(app, {"cmd": "rm -rf"})["ok"]
    assert not remoto.executar(app, ["status"])["ok"]


def test_caminho_do_controle():
    assert remoto.caminho_do_socket({"XDG_RUNTIME_DIR": "/run/user/7"}) == "/run/user/7/pestinha.sock"
    assert remoto.caminho_do_socket({}) is None
    assert pestinha_ctl.caminho_do_socket({"XDG_RUNTIME_DIR": "/run/user/7"}) == "/run/user/7/pestinha.sock"


def test_controle_local_de_ponta_a_ponta(tmp_path):
    from PySide6.QtCore import QEventLoop, QTimer
    from PySide6.QtWidgets import QApplication

    # QApplication (não QCoreApplication): os testes do app, depois, precisam de widgets
    qapp = QApplication.instance() or QApplication([])
    app = AppFalso()
    caminho = str(tmp_path / "pestinha.sock")
    controle = remoto.ControleLocal(app, caminho)
    assert controle.ok
    respostas = {}

    def cliente_ctl():
        respostas["perms"] = pestinha_ctl.enviar(pestinha_ctl.montar_pedido(["perms", "fogos=off"]), caminho)
        respostas["lixo"] = pestinha_ctl.enviar("não é um objeto", caminho)

    fio = threading.Thread(target=cliente_ctl)
    fio.start()
    laco = QEventLoop()
    relogio = QTimer()
    relogio.timeout.connect(lambda: laco.quit() if not fio.is_alive() else None)
    relogio.start(10)
    QTimer.singleShot(5000, laco.quit)
    laco.exec()
    fio.join(1)
    controle.fechar()
    assert respostas["perms"]["ok"] and respostas["perms"]["perms"]["fogos"] is False
    assert app.perms["fogos"] is False
    assert respostas["lixo"] == {"ok": False, "erro": "o pedido precisa ser um objeto JSON"}
    assert pestinha_ctl.enviar({"cmd": "status"}, caminho) is None          # fechado: o pet não está rodando
    assert qapp is not None


def test_pestinha_ctl_monta_os_pedidos():
    assert pestinha_ctl.montar_pedido(["status"]) == {"cmd": "status"}
    assert pestinha_ctl.montar_pedido(["perms", "bolinha=off", "fogos=ON", "memes=1"]) == \
        {"cmd": "perms", "valores": {"bolinha": False, "fogos": True, "memes": True}}
    for ruim in ([], ["perms"], ["perms", "bolinha"], ["perms", "bolinha=talvez"], ["status", "x"], ["rm"]):
        with pytest.raises(ValueError):
            pestinha_ctl.montar_pedido(ruim)
    assert pestinha_ctl.main(["perms", "x"]) == 2
