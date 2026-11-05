"""
Configuração comum dos testes (pasta tests/).

- Qt sem janela: os testes rodam em qualquer máquina, sem abrir nada na tela.
- Backend do X11 mesmo dentro do Hyprland: o app dos testes não abre o controle local de verdade nem
  fala com o compositor (tests/test_hyprland.py testa aquele backend direto, com saídas de exemplo).
- Mudo: PESTINHA_SEM_SOM deixa o tocador de som sem tocador (nenhum teste faz barulho de verdade).
- Português: PESTINHA_IDIOMA=pt, o idioma em que os textos são escritos (tests/test_idioma.py testa o inglês).
- Isolamento: apps e janelas criados num teste não continuam rodando nos seguintes.
"""
import gc
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("PESTINHA_PLATAFORMA", "x11")
os.environ.setdefault("PESTINHA_SEM_SOM", "1")
os.environ.setdefault("PESTINHA_IDIOMA", "pt")       # os testes conferem os textos originais; test_idioma testa o inglês

import pytest


@pytest.fixture(autouse=True)
def _encerrar_apps_e_janelas():
    from PySide6.QtWidgets import QApplication
    qt = QApplication.instance()
    antes = set(qt.topLevelWidgets()) if qt else set()
    yield
    from PySide6.QtCore import QTimer
    from pestinha.app import PestinhaApp
    for obj in gc.get_objects():
        if isinstance(obj, PestinhaApp):
            for timer in obj.findChildren(QTimer):
                timer.stop()
    qt = QApplication.instance()
    if qt:
        for widget in set(qt.topLevelWidgets()) - antes:
            for timer in widget.findChildren(QTimer):
                timer.stop()
            widget.close()
