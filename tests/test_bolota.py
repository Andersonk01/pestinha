"""
O Bolota: a bolinha de pelo, de forma "bola" (body/desenho_bola.py).

- O personagem carrega, tem o conteúdo e a voz dele e o corpo (pelo sem olhos e sem patinhas).
- Desenha toda emoção, pose e estilo sem passar do chão nem sair da janela.
- A animação: andando, rola (a distância vira giro); parado, fica em pé; feliz e rápido, corre;
  achata no pouso; acena ao acordar e quando fica feliz parado.
- Sem o corpo.png, o pelo é desenhado por código e o pet avisa.
"""
import math
import sys
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pytest  # noqa: E402
from PySide6.QtGui import QColor, QImage, QPainter  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from pestinha import config  # noqa: E402
from pestinha.body.desenho_bola import (  # noqa: E402
    BOLA_Y, DURACAO_ACENO, OLHO_DX, OLHO_R, OLHO_Y, RAIO, AnimacaoBola, CorpoBola, Pose, desenhar_bola, tingir,
)
from pestinha.body.desenho_rosto import aparencia_de  # noqa: E402
from pestinha.body.estilos import com_estilo  # noqa: E402
from pestinha.body.pet import CX, CY, WIN, PetWindow  # noqa: E402
from pestinha.body.pet_state import PetState  # noqa: E402
from pestinha.core.emotion import EYE_SHAPES  # noqa: E402
from pestinha.paths import Paths  # noqa: E402

PATHS = Paths(root=ROOT)
CHAO = CY + 45                      # a base do corpo físico, na janela


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


@pytest.fixture(scope="module")
def bolota(app):
    return aparencia_de(config.load_pet(PATHS, "bolota")["aparencia"])


@pytest.fixture(scope="module")
def corpo(app):
    return CorpoBola(QImage(str(PATHS.conteudo("bolota").corpo)))


def pintar(corpo, aparencia, emocao="observando", pose=None, blink=1.0, carinho=False, gaze=(0.0, 0.0)):
    img = QImage(WIN, WIN, QImage.Format_ARGB32)
    img.fill(0)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    p.translate(CX, CY)
    desenhar_bola(p, corpo, pose or Pose(), dict(EYE_SHAPES[emocao]), gaze, blink, emocao, carinho=carinho,
                  aparencia=aparencia, agora=0.3)
    p.end()
    return img


def opacos(img):
    return [(x, y) for y in range(0, img.height()) for x in range(0, img.width())
            if QColor.fromRgba(img.pixel(x, y)).alpha() > 40]


def perto(img, cor, x0, y0, x1, y1, tolerancia=30):
    """Quantos pixels do retângulo têm a cor `cor`."""
    alvo = QColor(cor)
    n = 0
    for y in range(int(y0), int(y1)):
        for x in range(int(x0), int(x1)):
            c = QColor.fromRgba(img.pixel(x, y))
            if c.alpha() > 200 and max(abs(c.red() - alvo.red()), abs(c.green() - alvo.green()),
                                       abs(c.blue() - alvo.blue())) <= tolerancia:
                n += 1
    return n


# ---------------- o personagem ----------------

def test_bolota_carrega_e_tem_conteudo_e_voz_proprios():
    pet = config.load_pet(PATHS, "bolota")
    assert pet["nome"] == "Bolota" and pet["aparencia"]["forma"] == "bola"
    assert pet["reacao_notebook"] == "triste" and pet["brincadeira"]["bola"] > 1.0
    assert set(pet["descricao"]) == {"en", "pt"}
    assert pet["seed"] not in {config.load_pet(PATHS, p)["seed"] for p in ("bryan", "cypher", "jorge")}
    c = PATHS.conteudo("bolota")
    for arquivo in (c.corpo, c.bolinha_papel, c.signs, c.notes, c.notes_sad):
        assert arquivo.is_file() and arquivo.parent == PATHS.pets / "bolota", arquivo
    sons = {p.stem for p in (PATHS.pets / "bolota" / "sons").glob("*.wav")}
    assert {"bip", "feliz", "triste", "bravo", "susto", "curioso", "batida", "liga"} <= sons
    for caminho in (PATHS.pets / "bolota" / "sons").glob("*.wav"):
        with wave.open(str(caminho), "rb") as w:
            assert (w.getnchannels(), w.getsampwidth()) == (1, 2), caminho
            assert 0.05 < w.getnframes() / w.getframerate() < 4.0, caminho


def test_temperamento_so_usa_conexoes_que_existem():
    from pestinha.core.nervous_system import CONNECTIONS
    nomes = {f"{c[0]}->{c[1]}" for c in CONNECTIONS} | {c[1] for c in CONNECTIONS}
    assert [k for k in config.load_pet(PATHS, "bolota")["temperamento"] if k not in nomes] == []


def test_o_corpo_nao_tem_olhos_nem_patinhas(app):
    """O corpo.png é só o pelo: nada do creme dos olhos e nada fora da bola, onde ficavam as patinhas."""
    img = QImage(str(PATHS.conteudo("bolota").corpo))
    assert img.width() == img.height() and img.width() >= 200
    creme = 0
    for y in range(0, img.height(), 2):
        for x in range(0, img.width(), 2):
            c = QColor.fromRgba(img.pixel(x, y))
            if c.alpha() > 200 and c.red() > 200 and c.green() > 180 and c.blue() > 140:
                creme += 1
    assert creme == 0
    lado = img.width()
    meio = QColor.fromRgba(img.pixel(lado // 2, lado // 2))
    assert meio.alpha() == 255
    for x in (2, lado - 3):                       # nas laterais, na altura das patinhas da arte: transparente
        assert QColor.fromRgba(img.pixel(x, int(lado * 0.62))).alpha() == 0


def test_forma_desconhecida_vira_tela_e_estilo_tinge_a_bola():
    assert aparencia_de({"forma": "triangulo"}).forma == "tela"
    assert aparencia_de({}).forma == "tela" and aparencia_de({}).tinta is None
    a = aparencia_de({"forma": "bola"})
    assert a.forma == "bola" and a.tinta is None
    rosa = com_estilo(a, "rosa")
    assert rosa.forma == "bola" and rosa.tinta == rosa.moldura
    assert com_estilo(a, "original") is a


# ---------------- o desenho ----------------

def test_desenha_toda_emocao_pose_e_estilo_sem_passar_do_chao(corpo, bolota):
    poses = [Pose(), Pose(rolagem=90), Pose(rolagem=200), Pose(corrida=1.0, velocidade=260, direcao=-1),
             Pose(aceno=1.0), Pose(achatar=0.24)]
    for estilo in config.ESTILOS:
        a = com_estilo(bolota, estilo)
        for emocao in EYE_SHAPES:
            for pose in poses:
                pontos = opacos(pintar(corpo, a, emocao, pose))
                assert pontos, (estilo, emocao, pose)
                assert max(y for _x, y in pontos) <= CHAO + 1, (estilo, emocao, pose)     # nada abaixo do chão
                assert min(x for x, _y in pontos) > 0 and max(x for x, _y in pontos) < WIN - 1, (estilo, emocao)
                assert min(y for _x, y in pontos) > 0, (estilo, emocao)


def test_os_pezinhos_tocam_o_chao_parado(corpo, bolota):
    pontos = opacos(pintar(corpo, bolota))
    assert max(y for _x, y in pontos) >= CHAO - 2


def test_olho_aberto_mostra_o_branco_e_fechado_nao(corpo, bolota):
    cx, cy = CX + OLHO_DX, CY + BOLA_Y + OLHO_Y
    caixa = (cx - OLHO_R, cy - OLHO_R, cx + OLHO_R, cy + OLHO_R)
    branco = bolota.tela
    aberto = perto(pintar(corpo, bolota), branco, *caixa)
    assert aberto > OLHO_R * OLHO_R                                    # boa parte do olho é branco
    for fechado in (pintar(corpo, bolota, blink=0.08), pintar(corpo, bolota, "dormindo"),
                    pintar(corpo, bolota, "contente", carinho=True)):
        assert perto(fechado, branco, *caixa) < aberto * 0.05


def test_pupila_segue_o_olhar(corpo, bolota):
    cx, cy = CX + OLHO_DX, CY + BOLA_Y + OLHO_Y
    pupila = bolota.olho
    direita = perto(pintar(corpo, bolota, gaze=(1.0, 0.0)), pupila, cx, cy - OLHO_R, cx + OLHO_R, cy + OLHO_R)
    esquerda = perto(pintar(corpo, bolota, gaze=(1.0, 0.0)), pupila, cx - OLHO_R, cy - OLHO_R, cx, cy + OLHO_R)
    assert direita > esquerda


def test_estilo_tinge_o_pelo(app, corpo):
    rosa = tingir(corpo.imagem, QColor("#ff6fb5"))
    lado = rosa.width()
    soma = [0, 0, 0]
    for y in range(lado // 4, 3 * lado // 4, 4):
        for x in range(lado // 4, 3 * lado // 4, 4):
            c = QColor.fromRgba(rosa.pixel(x, y))
            soma[0] += c.red()
            soma[1] += c.green()
            soma[2] += c.blue()
    r, g, b = soma
    assert r > b > g                                                    # rosa: muito vermelho, azul, pouco verde
    assert corpo.pixmap(QColor("#ff6fb5")) is corpo.pixmap(QColor("#ff6fb5"))     # feito uma vez só


def test_sem_imagem_o_pelo_e_desenhado_por_codigo(app):
    c = CorpoBola(QImage("/nao/existe.png"))
    assert not c.imagem.isNull()
    assert QColor.fromRgba(c.imagem.pixel(c.imagem.width() // 2, c.imagem.height() // 2)).alpha() == 255


def test_falta_do_corpo_vira_aviso(tmp_path):
    paths = Paths(root=tmp_path)
    (paths.pets / "teste").mkdir(parents=True)
    avisos = config.check_assets(paths.conteudo("teste"), "bola")
    assert any("corpo.png" in a for a in avisos)
    assert not any("corpo.png" in a for a in config.check_assets(paths.conteudo("teste")))


# ---------------- a animação ----------------

def andar(anim, x0, x1, passos, emocao="observando", t0=0.0, dt=1 / 30):
    t = t0
    for i in range(passos + 1):
        anim.passo(t, x0 + (x1 - x0) * i / passos, 0.0, True, False, emocao)
        t += dt
    return t


def test_andando_rola_e_parado_fica_em_pe():
    anim = AnimacaoBola()
    t = andar(anim, 0.0, 60.0, 30)                                      # 60 px em 1 s: rolando
    esperado = math.degrees(60.0 / RAIO) % 360.0
    assert anim.pose.rolagem == pytest.approx(esperado, abs=12.0)
    assert anim.pose.rolando() and anim.pose.corrida < 0
    for _ in range(60):                                                 # 2 s parado
        t += 1 / 30
        anim.passo(t, 60.0, 0.0, True, False, "observando")
    assert not anim.pose.rolando() and anim.pose.patinhas() > 0.9


def test_para_a_esquerda_rola_ao_contrario():
    anim = AnimacaoBola()
    andar(anim, 0.0, -20.0, 30)
    assert anim.pose.direcao == -1
    assert 180.0 < anim.pose.rolagem < 360.0                            # girou no sentido anti-horário


def test_feliz_e_rapido_corre_em_pe():
    anim = AnimacaoBola()
    andar(anim, 0.0, 300.0, 30, emocao="feliz")                         # 300 px/s
    assert anim.pose.correndo() and not anim.pose.rolando()
    assert anim.pose.velocidade > 200


def test_achata_ao_pousar_e_volta():
    anim = AnimacaoBola()
    anim.passo(0.0, 0.0, 0.0, True, False, "observando")
    anim.passo(0.03, 0.0, 900.0, False, False, "observando")            # caindo
    anim.passo(0.06, 0.0, 0.0, True, False, "observando")               # pousou
    assert anim.pose.achatar > 0.15
    t = 0.06
    for _ in range(30):
        t += 1 / 30
        anim.passo(t, 0.0, 0.0, True, False, "observando")
    assert anim.pose.achatar < 0.01


def test_acena_ao_acordar_e_para_depois():
    anim = AnimacaoBola()
    anim.passo(0.0, 0.0, 0.0, True, False, "dormindo")
    anim.passo(0.5, 0.0, 0.0, True, False, "observando")                # acordou
    anim.passo(0.9, 0.0, 0.0, True, False, "observando")
    assert anim.pose.aceno > 0.9
    anim.passo(0.5 + DURACAO_ACENO + 0.1, 0.0, 0.0, True, False, "observando")
    assert anim.pose.aceno == 0.0


def test_nao_acena_andando_nem_na_primeira_emocao():
    anim = AnimacaoBola()
    anim.passo(0.0, 0.0, 0.0, True, False, "feliz")
    anim.passo(0.3, 0.0, 0.0, True, False, "feliz")
    assert anim.pose.aceno == 0.0
    andar(anim, 0.0, 30.0, 10, emocao="observando", t0=0.4)
    anim.passo(0.8, 32.0, 0.0, True, False, "feliz")                    # ficou feliz andando
    assert anim.pose.aceno == 0.0


# ---------------- a janela ----------------

def test_a_janela_do_pet_desenha_a_bola(app, bolota, corpo):
    janela = PetWindow(300, 300, PetState())
    janela.aparencia, janela.corpo = bolota, corpo
    janela.animate(0.0)
    janela.body.x += 40
    janela.animate(0.1)
    img = janela.grab().toImage()
    assert opacos(img)
    janela.close()
