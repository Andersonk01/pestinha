"""
Estilos (cores por cima das do personagem), os acessórios e efeitos novos, o Cypher e os sons.

O estilo vale na hora e nunca muda os acessórios do personagem. Os sons nunca derrubam o pet: um som
que falta, ou não abre, é silêncio; nos testes o tocador é falso (ou mudo, pelo PESTINHA_SEM_SOM).
"""
import sys
import wave
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ferramentas"))

from PySide6.QtGui import QColor, QImage, QPainter  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

import pestinha_ctl  # noqa: E402
from pestinha import config  # noqa: E402
from pestinha.body.desenho_rosto import BODY_H, PADRAO, aparencia_de, draw_face, glitch_ativo  # noqa: E402
from pestinha.body.estilos import PALETAS, com_estilo  # noqa: E402
from pestinha.body.pet import CX, CY, WIN  # noqa: E402
from pestinha.body.voz import GANHO, Voz  # noqa: E402
from pestinha.core.emotion import EYE_SHAPES  # noqa: E402
from pestinha.mind import sons as sons_mod  # noqa: E402
from pestinha.mind.sons import SOM_DA_EMOCAO, SonsController  # noqa: E402
from pestinha.paths import ConteudoPaths, Paths  # noqa: E402
from pestinha.plataforma._som import MAX_SIMULTANEOS, Tocador  # noqa: E402
from pestinha.settings_store import SettingsStore  # noqa: E402

PATHS = Paths(root=ROOT)


def pintar(aparencia, emocao="observando", agora=2.0):
    QApplication.instance() or QApplication([])
    img = QImage(WIN, WIN, QImage.Format_ARGB32)
    img.fill(0)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    p.translate(CX, CY)
    draw_face(p, dict(EYE_SHAPES[emocao]), (0.0, 0.0), 1.0, emocao, aparencia=aparencia, agora=agora)
    p.end()
    return img


def opacos(img):
    return [(x, y) for y in range(img.height()) for x in range(img.width())
            if QColor.fromRgba(img.pixel(x, y)).alpha() > 40]


# ---------------- estilos ----------------

def test_todo_estilo_tem_paleta_e_toda_paleta_tem_nome():
    assert set(PALETAS) | {"original"} == set(config.ESTILOS)
    assert set(config.ESTILO_NOMES) == set(config.ESTILOS)
    assert config.DEFAULT_PERMISSIONS["estilo"] == "original"


def test_estilo_troca_as_cores_e_mantem_os_acessorios():
    jorge = aparencia_de(config.load_pet(PATHS, "jorge")["aparencia"])
    rosa = com_estilo(jorge, "rosa")
    assert rosa.moldura == QColor("#ff6fb5") and rosa.olho == QColor("#ff8fcb")
    assert rosa.acessorios == jorge.acessorios                       # a gravata continua
    assert com_estilo(jorge, "original") is jorge
    assert com_estilo(jorge, "nao-existe") is jorge
    assert pintar(rosa) != pintar(jorge)


def test_estilo_cyber_tem_os_efeitos_da_intro():
    cyber = com_estilo(PADRAO, "cyber")
    assert cyber.efeitos == {"chuva", "scanlines", "glitch"}
    assert cyber.codigo == QColor("#34D399")
    assert com_estilo(PADRAO, "rosa").efeitos == frozenset()
    # os efeitos andam com o relógio: a chuva e o glitch mudam o desenho
    assert glitch_ativo(0.05) and not glitch_ativo(2.0)
    assert pintar(cyber, agora=0.05) != pintar(cyber, agora=2.0)


def test_escolhas_so_aceitam_opcoes_que_existem():
    assert config.permissoes_validas({"estilo": "rosa", "volume": "alto"}) == {"estilo": "rosa", "volume": "alto"}
    assert config.permissoes_validas({"estilo": "roxo", "volume": "ensurdecedor", "sons": "sim"}) == {}
    assert config.permissoes_validas({"sons": False, "digitacao": True}) == {"sons": False, "digitacao": True}


# ---------------- acessórios e efeitos ----------------

def test_acessorio_com_cor_de_parte_do_corpo_acompanha_o_estilo():
    a = aparencia_de({"acessorios": {"fones": "moldura", "capuz": "#26324a", "gravata": "olho"}})
    assert [n for n, _c in a.acessorios] == ["capuz", "fones", "gravata"]
    assert dict(a.acessorios)["fones"] == "moldura"
    assert dict(com_estilo(a, "ambar").acessorios)["fones"] == "moldura"
    assert aparencia_de({"acessorios": {"fones": "laranja"}}).acessorios == (("fones", "moldura"),)   # padrão dele


def test_efeitos_e_cor_da_chuva_validados():
    a = aparencia_de({"efeitos": ["chuva", "fumaça", 3], "codigo": "#00ff00"})
    assert a.efeitos == {"chuva"} and a.codigo == QColor("#00ff00")
    b = aparencia_de({"efeitos": "chuva", "codigo": "verde"})
    assert b.efeitos == frozenset() and b.codigo is None


def test_cypher_desenha_toda_expressao_sem_passar_do_chao():
    cypher = aparencia_de(config.load_pet(PATHS, "cypher")["aparencia"])
    assert [n for n, _c in cypher.acessorios] == ["capuz", "fones"]
    for estilo in config.ESTILOS:
        a = com_estilo(cypher, estilo)
        for emocao in EYE_SHAPES:
            pontos = opacos(pintar(a, emocao))
            assert max(y for _x, y in pontos) <= CY + BODY_H / 2 + 3, (estilo, emocao)   # nada embaixo do corpo
            assert min(x for x, _y in pontos) > 0 and max(x for x, _y in pontos) < WIN - 1, (estilo, emocao)
            assert min(y for _x, y in pontos) > 0, (estilo, emocao)


# ---------------- o Cypher ----------------

def test_cypher_tem_conteudo_proprio():
    c = PATHS.conteudo("cypher")
    for arquivo in (c.signs, c.notes, c.notes_sad, c.notebook):
        assert arquivo.is_file() and arquivo.parent == PATHS.pets / "cypher", arquivo
    cypher = config.load_pet(PATHS, "cypher")
    assert cypher["nome"] == "Cypher" and len(cypher["temperamento"]) >= 8
    assert cypher["seed"] not in {config.load_pet(PATHS, p)["seed"] for p in ("bryan", "jorge")}


# ---------------- arquivos de som ----------------

def sons_usados():
    return set(sons_mod.INTERVALO) | {nome for nome, _i in SOM_DA_EMOCAO.values()}


def test_todo_som_usado_existe_no_comum_e_e_um_wav_que_abre():
    pasta = PATHS.comum / "sons"
    arquivos = {p.stem for p in pasta.glob("*.wav")}
    assert sons_usados() <= arquivos, sons_usados() - arquivos
    assert {"digitando_1", "digitando_2", "digitando_3"} <= arquivos
    for caminho in list(pasta.glob("*.wav")) + list((PATHS.pets / "cypher" / "sons").glob("*.wav")):
        with wave.open(str(caminho), "rb") as w:
            assert (w.getnchannels(), w.getsampwidth()) == (1, 2), caminho
            amostras = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2")
        assert 0.05 < w.getnframes() / w.getframerate() < 4.0, caminho
        assert np.abs(amostras).max() > 3000, caminho                    # não é silêncio
    assert {p.stem for p in (PATHS.pets / "cypher" / "sons").glob("*.wav")} <= sons_usados()


# ---------------- voz ----------------

class TocadorFalso:
    disponivel = True

    def __init__(self):
        self.tocados, self.parados, self.todos = [], [], 0

    def tocar(self, caminho):
        self.tocados.append(Path(caminho))
        return len(self.tocados)

    def parar(self, identificador):
        if identificador is not None:
            self.parados.append(identificador)

    def parar_todos(self):
        self.todos += 1


def wav(caminho, amplitude=20000, segundos=0.1):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    n = int(8000 * segundos)
    dados = (np.sin(np.arange(n) / 3.0) * amplitude).astype("<i2")
    with wave.open(str(caminho), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(8000)
        w.writeframes(dados.tobytes())


def pico(caminho):
    with wave.open(str(caminho), "rb") as w:
        return np.abs(np.frombuffer(w.readframes(w.getnframes()), dtype="<i2")).max()


def voz_de_teste(tmp_path):
    proprio, comum = tmp_path / "pets" / "x", tmp_path / "comum"
    wav(comum / "sons" / "bip.wav")
    wav(comum / "sons" / "feliz.wav", segundos=0.5)
    wav(comum / "sons" / "digitando_1.wav")
    wav(comum / "sons" / "digitando_2.wav")
    tocador = TocadorFalso()
    return Voz(ConteudoPaths(proprio, comum), tmp_path / "cache", tocador=tocador), tocador, proprio


def test_voz_toca_com_o_volume_escolhido_e_guarda_a_copia(tmp_path):
    voz, tocador, _ = voz_de_teste(tmp_path)
    assert voz.tocar("feliz") == pytest.approx(0.5)
    original = pico(tmp_path / "comum" / "sons" / "feliz.wav")
    assert pico(tocador.tocados[-1]) == pytest.approx(original * GANHO["medio"], rel=0.01)
    assert tocador.tocados[-1].parent == tmp_path / "cache"
    voz.configurar(True, "alto")
    voz.tocar("feliz")
    assert pico(tocador.tocados[-1]) == pytest.approx(original * GANHO["alto"], rel=0.01)
    assert len(list((tmp_path / "cache").glob("*.wav"))) == 2          # uma cópia por volume, reaproveitada
    voz.tocar("feliz")
    assert len(list((tmp_path / "cache").glob("*.wav"))) == 2


def test_voz_prefere_o_som_do_pet_e_silencia_o_que_falta(tmp_path):
    voz, tocador, proprio = voz_de_teste(tmp_path)
    wav(proprio / "sons" / "bip.wav", amplitude=9000)
    voz.tocar("bip")
    assert pico(tocador.tocados[-1]) == pytest.approx(9000 * GANHO["medio"], rel=0.01)
    assert voz.tocar("nao_existe") == 0.0
    (tmp_path / "comum" / "sons" / "quebrado.wav").write_bytes(b"isto nao e um wav")
    assert voz.tocar("quebrado") == 0.0 and voz.tocar("quebrado") == 0.0
    voz.configurar(False, "medio")
    antes = len(tocador.tocados)
    assert voz.tocar("bip") == 0.0 and len(tocador.tocados) == antes and tocador.todos == 1


def test_voz_canal_para_o_som_anterior_e_variantes_do_pet_valem_sozinhas(tmp_path):
    voz, tocador, proprio = voz_de_teste(tmp_path)
    assert voz.variantes("digitando") == ["digitando_1", "digitando_2"]
    primeiro = voz.tocar("bip", canal="c")
    assert primeiro and voz.tocar("bip", canal="c")
    assert tocador.parados == [1]                                       # o primeiro foi parado
    wav(proprio / "sons" / "digitando_9.wav")
    assert voz.variantes("digitando") == ["digitando_9"]


# ---------------- quando tocar ----------------

class VozFalsa:
    def __init__(self, duracao=2.0):
        self.tocados, self.parados, self.duracao, self.silencio = [], [], duracao, 0

    def tocar(self, nome, canal=None):
        self.tocados.append(nome)
        return 0.3

    def tocar_um_de(self, prefixo, canal=None):
        self.tocados.append(prefixo)
        return self.duracao

    def parar(self, canal):
        self.parados.append(canal)

    def parar_tudo(self):
        self.silencio += 1


def test_emocao_nova_faz_som_com_intervalo_minimo():
    voz = VozFalsa()
    sons = SonsController(voz)
    sons.tick(0.0, "bravo", False, True, False)
    assert voz.tocados == []                                            # a primeira emoção não conta
    sons.tick(1.0, "observando", False, True, False)
    sons.tick(2.0, "bravo", False, True, False)
    sons.tick(3.0, "observando", False, True, False)
    sons.tick(4.0, "bravo", False, True, False)                         # de novo, cedo demais
    assert voz.tocados == ["bravo"]
    sons.tick(40.0, "observando", False, True, False)
    sons.tick(41.0, "bravo", False, True, False)
    assert voz.tocados == ["bravo", "bravo"]
    sons.tick(41.2, "assustado", False, True, False)                    # respiro entre dois sons
    assert voz.tocados == ["bravo", "bravo"]


def test_eventos_respeitam_o_intervalo_de_cada_som():
    voz = VozFalsa()
    sons = SonsController(voz)
    assert sons.cutucada(0.0) and not sons.cutucada(0.1) and sons.cutucada(0.5)
    assert sons.carinho(5.0) and not sons.carinho(6.0)
    assert voz.tocados == ["bip", "bip", "feliz"]


def test_digita_sentado_com_pausas_e_para_ao_levantar():
    voz = VozFalsa(duracao=2.0)
    sons = SonsController(voz, rng=SimpleNamespace(uniform=lambda a, b: a))
    sons.tick(0.0, "observando", True, True, False)                     # sentou: espera o início
    assert voz.tocados == []
    sons.tick(0.6, "observando", True, True, False)
    assert voz.tocados == ["digitando"]
    sons.tick(1.5, "observando", True, True, False)                     # ainda digitando
    sons.tick(3.0, "observando", True, True, False)                     # pausa (2 s + 1,5 s)
    assert voz.tocados == ["digitando"]
    sons.tick(4.2, "observando", True, True, False)
    assert voz.tocados == ["digitando", "digitando"]
    sons.tick(4.5, "observando", False, True, False)                    # levantou
    assert voz.parados == ["digitacao"]
    sons.tick(4.6, "observando", False, True, False)
    assert voz.parados == ["digitacao"]                                 # não fica parando à toa


def test_sem_digitacao_escondido_ou_dormindo_nao_digita():
    for args in ((True, False, False), (True, True, True)):
        voz = VozFalsa()
        sons = SonsController(voz, rng=SimpleNamespace(uniform=lambda a, b: a))
        for t in range(10):
            sons.tick(float(t), "observando", *args)
        assert voz.tocados == []
    voz = VozFalsa()
    sons = SonsController(voz, rng=SimpleNamespace(uniform=lambda a, b: a))
    sons.configurar(False)
    for t in range(10):
        sons.tick(float(t), "observando", True, True, False)
    assert voz.tocados == []


# ---------------- tocador do sistema ----------------

class ProcessoFalso:
    def __init__(self, args):
        self.args, self.vivo, self.terminado = args, True, False

    def poll(self):
        return None if self.vivo else 0

    def terminate(self):
        self.terminado, self.vivo = True, False


def test_tocador_escolhe_o_do_sistema_e_respeita_o_limite():
    processos = []

    def popen(args, **_kw):
        processos.append(ProcessoFalso(args))
        return processos[-1]

    t = Tocador(sistema="linux", ambiente={}, which=lambda c: c in ("paplay", "aplay"), popen=popen)
    assert t.comando == ("paplay",) and t.disponivel
    ids = [t.tocar(f"/tmp/{i}.wav") for i in range(MAX_SIMULTANEOS + 1)]
    assert ids[-1] is None and processos[0].args == ["paplay", "/tmp/0.wav"]
    t.parar(ids[0])
    assert processos[0].terminado
    assert t.tocar("/tmp/x.wav") is not None                            # abriu vaga
    t.parar_todos()
    assert all(p.terminado for p in processos)
    assert not Tocador(sistema="linux", ambiente={"PESTINHA_SEM_SOM": "1"}, which=lambda c: True).disponivel
    assert not Tocador(sistema="linux", ambiente={}, which=lambda c: False).disponivel
    assert Tocador(sistema="darwin", ambiente={}, which=lambda c: c == "afplay").comando == ("afplay",)


# ---------------- de fora (Hub, ryoku-pestinha) e no app ----------------

def test_ctl_manda_escolhas_como_texto():
    assert pestinha_ctl.montar_pedido(["perms", "estilo=Cyber", "volume=baixo", "sons=off"]) == \
        {"cmd": "perms", "valores": {"estilo": "cyber", "volume": "baixo", "sons": False}}
    for ruim in (["perms", "estilo=a b"], ["perms", "estilo="], ["perms", "sons=talvez"]):
        with pytest.raises(ValueError):
            pestinha_ctl.montar_pedido(ruim)


def test_estilo_e_som_valem_na_hora_no_app(tmp_path, monkeypatch):
    QApplication.instance() or QApplication([])
    import shutil
    import pestinha.app as app_mod
    shutil.copytree(PATHS.pets, tmp_path / "pets")
    paths = Paths(root=tmp_path)
    monkeypatch.setattr(app_mod, "PanicHotkey", lambda: SimpleNamespace(ok=True, pressed=Mock()))
    SettingsStore(paths).update(dict(config.DEFAULT_PERMISSIONS, pet="cypher"))
    app = app_mod.PestinhaApp(SettingsStore(paths), paths)
    for timer in app.findChildren(app_mod.QTimer):
        timer.stop()
    assert app.pet.aparencia.moldura == QColor("#6EE7F9")               # o original do Cypher
    app.apply_perms({"estilo": "rosa", "volume": "baixo", "digitacao": False})
    assert app.pet.aparencia.moldura == QColor("#ff6fb5")
    assert [n for n, _c in app.pet.aparencia.acessorios] == ["capuz", "fones"]
    assert app.mesa.caderno.cor_destaque == QColor("#ff6fb5")
    assert app.voz.volume == "baixo" and app.sons.digitacao is False
    assert SettingsStore(paths).perms["estilo"] == "rosa"               # gravado
    app.pet.grab()
