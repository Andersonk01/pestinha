"""
Idioma: o pet fala o idioma do sistema (português ou inglês).

- Todo texto marcado com tr() ou N_() tem a tradução em pestinha/idioma_en.py, com os mesmos {campos}, e
  nenhuma tradução sobra.
- Nenhum tr() roda na importação de um módulo: o idioma só é decidido quando o programa abre.
- A escolha do idioma: PESTINHA_IDIOMA, as variáveis do sistema, o Qt, e o inglês para o resto.
"""
import ast
import re
import string
from pathlib import Path

import pytest

from pestinha import idioma
from pestinha.idioma_en import TEXTOS

RAIZ = Path(__file__).resolve().parent.parent
ARQUIVOS = sorted((RAIZ / "pestinha").rglob("*.py")) + [RAIZ / "main.py", RAIZ / "ferramentas" / "pestinha_ctl.py"]


def _nome(no):
    return getattr(no.func, "id", None) or getattr(no.func, "attr", None)


def chamadas(arvore):
    """As chamadas tr(...) e N_(...) de uma árvore."""
    for no in ast.walk(arvore):
        if isinstance(no, ast.Call) and _nome(no) in ("tr", "N_") and no.args:
            yield no


def marcados():
    """(arquivo, linha, texto) de cada tr("...") e N_("...") com texto literal."""
    for arq in ARQUIVOS:
        for no in chamadas(ast.parse(arq.read_text(encoding="utf-8"))):
            arg = no.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                yield arq.relative_to(RAIZ), no.lineno, arg.value


def campos(texto):
    return {c[1] for c in string.Formatter().parse(texto) if c[1] is not None}


@pytest.fixture
def em(monkeypatch):
    """Troca o idioma só dentro do teste."""
    def trocar(codigo):
        monkeypatch.setattr(idioma, "_atual", codigo)
    return trocar


def test_todo_texto_marcado_tem_traducao_com_os_mesmos_campos():
    faltando, campos_errados = [], []
    for arq, linha, texto in marcados():
        if texto not in TEXTOS:
            faltando.append(f"{arq}:{linha} {texto!r}")
        elif campos(texto) != campos(TEXTOS[texto]):
            campos_errados.append(f"{arq}:{linha} {texto!r}")
    assert faltando == [] and campos_errados == []


def test_nenhuma_traducao_sobra():
    usados = {texto for _a, _l, texto in marcados()}
    assert sorted(set(TEXTOS) - usados) == []


def test_tr_so_recebe_texto_literal_ou_constante_marcada():
    """Um f-string não pode ser chave: o texto muda a cada chamada e nunca acha a tradução."""
    ruins = []
    for arq in ARQUIVOS:
        for no in chamadas(ast.parse(arq.read_text(encoding="utf-8"))):
            if isinstance(no.args[0], ast.JoinedStr) or (_nome(no) == "N_" and not isinstance(no.args[0], ast.Constant)):
                ruins.append(f"{arq.relative_to(RAIZ)}:{no.lineno}")
    assert ruins == []


def test_nenhum_tr_roda_na_importacao():
    """No nível do módulo (fora de funções e lambdas), só N_(): o idioma ainda não foi decidido."""
    ruins = []

    def visitar(no, arq):
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            return
        if isinstance(no, ast.ClassDef):
            for filho in no.body:
                visitar(filho, arq)
            return
        if isinstance(no, ast.Call) and _nome(no) == "tr":
            ruins.append(f"{arq.relative_to(RAIZ)}:{no.lineno}")
        for filho in ast.iter_child_nodes(no):
            visitar(filho, arq)

    for arq in ARQUIVOS:
        for no in ast.parse(arq.read_text(encoding="utf-8")).body:
            visitar(no, arq)
    assert ruins == []


def test_tr_traduz_e_preenche_campos(em):
    em("en")
    assert idioma.tr("Fechar") == TEXTOS["Fechar"]
    em("pt")
    assert idioma.tr("Fechar") == "Fechar"
    assert idioma.tr("texto sem tradução {x}", x=1) == "texto sem tradução 1"


@pytest.mark.parametrize("nome, esperado", [
    ("pt_BR.UTF-8", "pt"), ("pt_PT", "pt"), ("pt-BR", "pt"), ("Portuguese_Brazil", "pt"),
    ("en_US.UTF-8", "en"), ("fr_FR", "en"), ("de", "en"), ("", None), ("C", None), ("C.UTF-8", None),
    ("POSIX", None),
])
def test_escolher(nome, esperado):
    assert idioma.escolher(nome) == esperado


def test_do_sistema_na_ordem(monkeypatch):
    for v in ("PESTINHA_IDIOMA", "LC_ALL", "LC_MESSAGES", "LANG"):
        monkeypatch.delenv(v, raising=False)
    assert idioma.do_sistema() == "en"                         # nada: inglês
    assert idioma.do_sistema("pt_BR") == "pt"                  # Windows e macOS: o Qt informa
    monkeypatch.setenv("LANG", "pt_BR.UTF-8")
    assert idioma.do_sistema("en_US") == "pt"                  # a variável vem antes do Qt
    monkeypatch.setenv("LC_ALL", "C")
    assert idioma.do_sistema() == "pt"                         # "C" não diz idioma: segue para a próxima
    monkeypatch.setenv("LC_MESSAGES", "en_GB.UTF-8")
    assert idioma.do_sistema() == "en"
    monkeypatch.setenv("PESTINHA_IDIOMA", "pt")
    assert idioma.do_sistema() == "pt"                         # a escolha na mão vence tudo
    monkeypatch.setenv("PESTINHA_IDIOMA", "klingon")
    assert idioma.do_sistema() == "en"                         # escolha inválida é ignorada


def test_definir_so_aceita_idioma_conhecido(em):
    em("pt")
    with pytest.raises(ValueError):
        idioma.definir("fr")
    assert idioma.atual() == "pt"


# ---------------- conteúdo por idioma ----------------

def test_nomes_no_idioma():
    from pestinha.paths import no_idioma
    assert no_idioma("cartazes.txt", "pt") == ["cartazes.txt"]
    assert no_idioma("cartazes.txt", "en") == ["cartazes.en.txt", "cartazes.txt"]
    assert no_idioma("memes", "en") == ["memes.en", "memes"]
    assert no_idioma("memes/trabalhando", "en") == ["memes.en/trabalhando", "memes/trabalhando"]
    assert no_idioma("bolinha_papel.png", "en") == ["bolinha_papel.en.png", "bolinha_papel.png"]


def test_conteudo_prefere_a_versao_do_idioma_e_volta_a_original(tmp_path, em):
    from pestinha.paths import Paths
    paths = Paths(root=tmp_path)
    pet = paths.pets / "teste"
    (pet / "memes" / "feliz").mkdir(parents=True)
    (pet / "cartazes.txt").write_text("[greve]\nEM GREVE\n", encoding="utf-8")
    (pet / "recadinhos.txt").write_text("oi\n", encoding="utf-8")
    (pet / "recadinhos.en.txt").write_text("hi\n", encoding="utf-8")
    c = paths.conteudo("teste")
    em("en")
    assert c.notes == pet / "recadinhos.en.txt"
    assert c.signs == pet / "cartazes.txt"                     # sem a versão em inglês, a original
    assert c.memes == pet / "memes"
    (pet / "memes.en" / "trabalhando").mkdir(parents=True)
    assert c.memes == pet / "memes.en" and c.memes_trabalho == pet / "memes.en" / "trabalhando"
    em("pt")
    assert c.notes == pet / "recadinhos.txt" and c.memes == pet / "memes"


def test_os_tres_pets_tem_as_frases_em_ingles_com_as_mesmas_secoes():
    from pestinha.core.protesto import load_signs
    from pestinha.paths import Paths
    paths = Paths()
    for pet in ("bryan", "cypher", "jorge"):
        pasta = paths.pets / pet
        for nome in ("cartazes", "recadinhos", "recadinhos_tristes"):
            assert (pasta / f"{nome}.en.txt").is_file(), (pet, nome)
        pt, en = load_signs(pasta / "cartazes.txt"), load_signs(pasta / "cartazes.en.txt")
        assert set(pt) == set(en), pet
        assert all(en[secao] for secao in en), pet


# ---------------- as telas em inglês, sem português ----------------

PORTUGUES = re.compile(r"[ãõçáéíóúâêôàÃÕÇÁÉÍÓÚÂÊÔ]|\b(não|você|de|da|dos|das|para|com|que|ele|uma|pelo|pela)\b",
                       re.IGNORECASE)
# nomes de arquivo e pasta do projeto, que não se traduzem
NOMES_DE_ARQUIVO = ("PRIVACIDADE.md", "recadinhos.txt", "assets/comum", "pets/<pet>", "timeline.csv")


def com_portugues(textos):
    ruins = []
    for texto in textos:
        limpo = texto
        for nome in NOMES_DE_ARQUIVO:
            limpo = limpo.replace(nome, "")
        if PORTUGUES.search(limpo):
            ruins.append(texto)
    return ruins


def textos_visiveis(janela):
    from PySide6.QtWidgets import QAbstractButton, QComboBox, QGroupBox, QLabel, QWidget
    textos = [janela.windowTitle()]
    for w in [janela] + janela.findChildren(QWidget):
        textos.append(w.toolTip())
        if isinstance(w, (QLabel, QAbstractButton)):
            textos.append(w.text())
        elif isinstance(w, QGroupBox):
            textos.append(w.title())
        elif isinstance(w, QComboBox):
            textos += [w.itemText(i) for i in range(w.count())]
    return [t for t in textos if t]


def test_telas_em_ingles_sem_portugues(tmp_path, monkeypatch, em):
    from types import SimpleNamespace
    from unittest.mock import Mock
    from PySide6.QtWidgets import QApplication, QMenu
    from pestinha import config
    from pestinha.paths import Paths
    from pestinha.settings_store import SettingsStore
    from pestinha.ui.onboarding import Onboarding
    from pestinha.ui.ui import SettingsDialog
    import pestinha.app as app_mod

    QApplication.instance() or QApplication([])
    antes = set(QApplication.topLevelWidgets())              # janelas de outros testes não contam
    em("en")
    paths = Paths(root=RAIZ, dados=tmp_path / "memory")
    textos = []
    for pet in config.list_pets(paths):
        d = SettingsDialog(dict(config.DEFAULT_PERMISSIONS, pet=pet), paths, first_run=True)
        textos += textos_visiveis(d)
        o = Onboarding(config.load_pet(paths, pet)["nome"])
        for i in range(o.stack.count()):
            o.stack.setCurrentIndex(i)
            textos += textos_visiveis(o)

    monkeypatch.setattr(app_mod, "PanicHotkey", lambda: SimpleNamespace(ok=True, pressed=Mock()))
    app = app_mod.PestinhaApp(SettingsStore(paths), paths)
    for timer in app.findChildren(app_mod.QTimer):
        timer.stop()
    textos += [a.text() for a in app.tray.menu.actions()]
    menus = []

    class MenuQueAnota(QMenu):
        def exec(self, *_args):
            menus.append([a.text() for a in self.actions()])

    import pestinha.controle.interacao as interacao
    monkeypatch.setattr(interacao, "QMenu", MenuQueAnota)
    app.show_pet_menu(app.pet.pos())
    assert menus and menus[0]
    textos += menus[0]
    for chave in ("greve", "neural"):
        app.floats.toggle(chave)
    textos += [w.windowTitle() for w in set(QApplication.topLevelWidgets()) - antes if w.windowTitle()]
    textos += [frase for secao in app.protest.signs.values() for frase in secao]
    textos += config.check_assets(app.conteudo)
    assert com_portugues(textos) == []
