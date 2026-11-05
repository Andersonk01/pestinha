"""
PESTINHA - ponto de entrada.

Rodar:
    python main.py              passo a passo e permissões na primeira vez; depois, abre direto
    python main.py --configurar abre a tela de permissões antes de começar
    python main.py --direto     usa as permissões salvas, mesmo com o pânico ligado
    python main.py --sair-em N  fecha sozinho depois de N segundos (para testes)
    python main.py --pet jorge  troca o personagem antes de abrir (vale para as próximas vezes)

Dependências em requirements.txt. Pânico: Ctrl + Alt + Shift + B (desliga tudo e continua desligado).
"""

import argparse
import hashlib
import sys

from PySide6.QtCore import QDir, QLocale, QLockFile, QTimer
from PySide6.QtWidgets import QApplication, QDialog, QMessageBox

from pestinha import config, idioma, plataforma, store
from pestinha.idioma import tr
from pestinha import log as log_module
from pestinha.paths import Paths
from pestinha.settings_store import SettingsStore
from pestinha.app import PestinhaApp
from pestinha.ui.onboarding import Onboarding
from pestinha.ui.ui import SettingsDialog, face_icon


def apagar_memoria(paths):
    """Apaga memory/ e confirma o resultado; devolve (sucesso, caminhos que falharam)."""
    falhas = store.apagar_pasta(paths.memory) if paths.memory.exists() else []
    return not falhas and not paths.memory.exists(), falhas


def travar_instancia(paths):
    """
    Trava que garante uma cópia só usando esta memória; None se outra já estiver aberta.
    Fica na pasta temporária porque o Windows não apagaria a memória com o arquivo da trava aberto.
    Quem recebe precisa guardar a trava enquanto o programa roda.
    """
    marca = hashlib.sha256(str(paths.memory).encode("utf-8")).hexdigest()[:16]
    trava = QLockFile(f"{QDir.tempPath()}/pestinha-{marca}.lock")
    trava.setStaleLockTime(0)       # enquanto a cópia estiver viva a trava vale; se ela caiu, a trava é recuperada
    return trava if trava.tryLock(0) else None


def deve_mostrar_tela(args, perms, primeira_vez):
    """Tela de permissões: na primeira vez, se pedida, antes de clicar em Começar ou para religar após o pânico."""
    if primeira_vez or args.configurar:
        return True
    if args.direto:
        return False
    return not perms["configurado"] or not perms["ativo"]


def main():
    parser = argparse.ArgumentParser(description="Pestinha")
    parser.add_argument("--direto", action="store_true", help=tr("pula a tela de permissões"))
    parser.add_argument("--configurar", action="store_true", help=tr("mostra a tela de permissões"))
    parser.add_argument("--sair-em", type=float, default=0.0, help=tr("fecha sozinho após N segundos (teste)"))
    parser.add_argument("--pet", default="", help=tr("personagem (o id em pets/, ex.: bryan ou jorge)"))
    args = parser.parse_args()

    plataforma.preparar_qt()                        # no Hyprland: XWayland, onde as janelas podem andar
    app = QApplication(sys.argv)
    idioma.definir(idioma.do_sistema(QLocale.system().name()))     # no Windows e no macOS, quem diz é o Qt
    if plataforma.CLASSE_DAS_JANELAS:
        app.setApplicationName(plataforma.CLASSE_DAS_JANELAS)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(face_icon())

    paths = Paths()
    log_module.setup(paths.log)
    log_module.capturar_erros()
    trava = travar_instancia(paths)
    if trava is None:
        QMessageBox.information(None, config.APP_NOME, tr("O {app} já está aberto. Procure o ícone na bandeja.",
                                                          app=config.APP_NOME))
        return 0

    store = SettingsStore(paths)
    if args.pet:
        if args.pet in config.list_pets(paths):
            store.update({"pet": args.pet})
        else:
            print(f"[pet] não existe o personagem {args.pet!r}; ficou o {store.perms['pet']}")
    perms = store.perms
    first_time = not paths.permissions.exists()
    if deve_mostrar_tela(args, perms, first_time):
        if first_time and Onboarding(config.load_pet(paths, config.escolher_pet(paths, perms["pet"]))["nome"]).exec() != QDialog.Accepted:
            pass                                    # "Pular" também segue para as permissões
        dialog = SettingsDialog(perms, paths, first_run=True)
        dialog.changed.connect(store.update)        # o diálogo trabalha numa cópia: cada escolha vem por aqui
        apagado = []

        def apagar_tudo():
            log_module.desligar_arquivo()           # nada pode recriar a pasta depois de apagada
            sucesso, falhas = apagar_memoria(paths)
            if not sucesso:
                log_module.setup(paths.log)
                detalhe = tr("\n\nArquivos que falharam: {lista}", lista=", ".join(falhas)) if falhas else ""
                QMessageBox.warning(
                    dialog, tr("Não foi possível apagar tudo"),
                    tr("Alguns dados continuam em {pasta}. Feche programas que possam estar usando esses arquivos "
                       "e tente novamente.{detalhe}", pasta=paths.memory, detalhe=detalhe),
                )
                return
            apagado.append(True)
            dialog.reject()

        dialog.wipe_all.connect(apagar_tudo)
        if dialog.exec() != QDialog.Accepted or apagado:
            return 0
        store.update({"configurado": True})         # grava já: a próxima vez abre direto

    pet_app = PestinhaApp(store, paths)
    if args.sair_em > 0:
        QTimer.singleShot(int(args.sair_em * 1000), pet_app.quit)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
