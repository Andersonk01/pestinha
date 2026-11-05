"""
ONBOARDING - passo a passo da primeira vez, com aviso de projeto em desenvolvimento.

Quatro telas curtas: o aviso, o que ele é, o que ele vê, e o que você escolhe.
Aparece só quando ainda não existe memory/permissions.json. "Pular" e "Começar"
levam direto à tela de permissões.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
)

from ..config import APP_NOME
from ..idioma import N_, tr
from .ui import STYLE, face_icon

DEV_NOTICE = N_(
    "Este é um projeto em desenvolvimento. Algumas coisas podem não funcionar direito, "
    "ainda há bugs a corrigir e o comportamento pode mudar bastante entre versões. "
    "Obrigado por testar!"
)

# (título, texto) de cada tela; passam por tr() ao montar
PAGES = [
    (N_("Projeto em desenvolvimento"),
     DEV_NOTICE),
    (N_("Oi, eu sou o {nome}"),
     N_("Sou uma telinha com dois olhinhos que mora no seu monitor principal. Eu caio, quico, "
        "pouso nas janelas, fico tristinho, brinco com a bolinha e, às vezes, apronto com "
        "post-its e memes.\n\nVocê pode me cutucar, me dar carinho, me jogar e abrir meu menu "
        "com o botão direito.")),
    (N_("O que eu vejo (e o que não vejo)"),
     N_("Eu vejo o nome do programa em primeiro plano, o tempo sem usar o teclado ou o mouse, "
        "e a posição das janelas para pousar nelas.\n\nNunca leio o conteúdo de nenhuma janela, "
        "página, documento ou conversa. Os detalhes estão em PRIVACIDADE.md.")),
    (N_("Agora você escolhe"),
     N_("Na próxima tela você decide o que eu posso fazer: travessuras, bolinha, carinho e "
        "mais. Tudo pode ser mudado depois, pelo menu da bandeja ou pelo botão direito em mim.\n\n"
        "Atalho de pânico: Ctrl + Alt + Shift + B desliga tudo na hora.")),
]


class Onboarding(QDialog):
    """Passo a passo da primeira vez: aviso de projeto em desenvolvimento, o que o pet é, o que ele vê e o que você escolhe."""
    def __init__(self, nome):
        """Monta as telas com o nome do personagem escolhido."""
        super().__init__()
        self.setWindowTitle(tr("{app} · primeira vez", app=APP_NOME))
        self.setWindowIcon(face_icon())
        self.setStyleSheet(STYLE)
        self.setMinimumWidth(480)
        self.index = 0

        root = QVBoxLayout(self)
        self.stack = QStackedWidget()
        for title, body in PAGES:
            title = tr(title, nome=nome)        # quem se apresenta é o pet escolhido
            body = tr(body)
            page = QLabel(
                f"<h3 style='color:#63e56f'>{title}</h3>"
                f"<p style='font-size:13px'>{body.replace(chr(10), '<br>')}</p>"
            )
            page.setWordWrap(True)
            page.setTextFormat(Qt.RichText)
            page.setAlignment(Qt.AlignTop)
            self.stack.addWidget(page)
        root.addWidget(self.stack, 1)

        self.counter = QLabel()
        self.counter.setObjectName("hint")
        root.addWidget(self.counter)

        buttons = QHBoxLayout()
        self.skip = QPushButton(tr("Pular"))
        self.skip.clicked.connect(self.accept)
        self.back = QPushButton(tr("Voltar"))
        self.back.clicked.connect(self.previous)
        self.next = QPushButton(tr("Próximo"))
        self.next.setObjectName("start")
        self.next.clicked.connect(self.advance)
        buttons.addWidget(self.skip)
        buttons.addStretch(1)
        buttons.addWidget(self.back)
        buttons.addWidget(self.next)
        root.addLayout(buttons)

        self._refresh()

    def _refresh(self):
        """Mostra a tela atual e ajusta os botões (Voltar, Próximo ou Começar)."""
        last = self.index == len(PAGES) - 1
        self.stack.setCurrentIndex(self.index)
        self.back.setEnabled(self.index > 0)
        self.next.setText(tr("Começar") if last else tr("Próximo"))
        self.counter.setText(tr("{atual} de {total}", atual=self.index + 1, total=len(PAGES)))

    def advance(self):
        """Vai para a próxima tela, ou termina na última."""
        if self.index == len(PAGES) - 1:
            self.accept()
            return
        self.index += 1
        self._refresh()

    def previous(self):
        """Volta uma tela."""
        if self.index > 0:
            self.index -= 1
            self._refresh()
