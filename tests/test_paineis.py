"""Painéis do menu (monitor neural e painel de protesto): abrir à mão deve manter o painel na tela."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pytest  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from pestinha import config  # noqa: E402
from pestinha.app import PestinhaApp  # noqa: E402
from pestinha.paths import Paths  # noqa: E402
from pestinha.settings_store import SettingsStore  # noqa: E402


@pytest.fixture
def pet_app(tmp_path):
    app_qt = QApplication.instance() or QApplication([])
    app_qt.setQuitOnLastWindowClosed(False)
    paths = Paths(root=tmp_path)
    store = SettingsStore(paths)
    store.update(dict(config.DEFAULT_PERMISSIONS))           # modo teste desligado (padrão)
    app = PestinhaApp(store, paths)
    yield app
    app.floats.hidden_by_tray = True
    for w in list(app.floats.windows.values()):
        w.close()


def test_painel_aberto_no_menu_fica_na_tela_fora_do_modo_teste(pet_app):
    pet_app.floats.open("neural")
    pet_app.floats.sync(pet_app.floats_allowed(), pet_app.floats_base())
    assert pet_app.floats.window("neural").isVisible()


def test_clicar_de_novo_fecha_o_painel(pet_app):
    pet_app.floats.toggle("greve")
    pet_app.floats.toggle("greve")
    pet_app.floats.sync(pet_app.floats_allowed(), pet_app.floats_base())
    assert not pet_app.floats.window("greve").isVisible()


def test_esconder_o_bryan_esconde_o_painel(pet_app):
    pet_app.floats.open("greve")
    pet_app.floats.sync(False, False)
    assert not pet_app.floats.window("greve").isVisible()


# ------------------------------------------------------------------ telas que o Qt vê noutro lugar


def test_geometria_das_telas_vem_do_sistema_quando_ele_informa(pet_app, monkeypatch):
    from pestinha import plataforma
    from PySide6.QtGui import QGuiApplication
    tela = QGuiApplication.screens()[0]
    dpr = tela.devicePixelRatio() or 1.0
    monkeypatch.setattr(plataforma, "geometrias", lambda: {tela.name(): (-1920, 0, 0, 1080)})
    monkeypatch.setattr(plataforma, "areas_uteis", lambda: {tela.name(): (-1920, 36, 0, 1080)})
    assert pet_app.screen_geometries()[0] == tuple(v / dpr for v in (-1920, 0, 0, 1080))
    assert pet_app.screen_bounds()[0] == tuple(v / dpr for v in (-1920, 36, 0, 1080))
    assert pet_app._telas()[0] == (-1920, 0, 1920 / dpr, 1080 / dpr, dpr)
    monkeypatch.setattr(plataforma, "geometrias", dict)
    g = tela.geometry()
    assert pet_app.screen_geometries()[0] == (g.x(), g.y(), g.x() + g.width(), g.y() + g.height())


def test_painel_salvo_num_monitor_que_o_qt_nao_ve_continua_la():
    from pestinha.world.arrastavel import posicao_acessivel
    areas = [(0, 36, 1920, 1080), (-1920, 36, 0, 1080)]          # o HDMI à esquerda, como o pet o vê
    assert posicao_acessivel((-800, 900), (1700, 900), (150, 110), areas) == (-800, 900)
    assert posicao_acessivel((-5000, 900), (1700, 900), (150, 110), areas) == (1700, 900)
