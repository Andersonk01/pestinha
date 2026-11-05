"""
CONTROLE LOCAL - comandos de fora para o pet que já está rodando, por um socket local que só o seu
usuário alcança (fica em XDG_RUNTIME_DIR). Quem usa: o atalho de pânico do Hyprland e o painel do
sistema, pelo `ferramentas/pestinha_ctl.py`. Ligado só onde a plataforma pede (TEM_CONTROLE_LOCAL).

Uma linha JSON por conexão, e uma linha JSON de resposta:
    {"cmd": "status"}                       estado e permissões
    {"cmd": "perms", "valores": {...}}      muda permissões (as mesmas da tela de configurações,
                                            inclusive as escolhas "estilo" e "volume")
    {"cmd": "panico"}                       o mesmo que Ctrl+Alt+Shift+B: desliga tudo
    {"cmd": "religar"}                      liga de novo depois do pânico
    {"cmd": "configuracoes"}                abre a tela de configurações
    {"cmd": "pausar"}, {"cmd": "esconder"}  alternam, como no menu da bandeja
    {"cmd": "sair"}                         salva e fecha

Nada aqui lê ou devolve o que você faz no computador: só o estado do próprio pet.
"""

import json
import os

from PySide6.QtCore import QObject, QTimer
from PySide6.QtNetwork import QLocalServer

from .. import config
from ..log import log

# o pânico e a troca de personagem têm comandos próprios (a troca vale na próxima abertura)
FORA_DE_PERMS = {"ativo", "configurado", "pet"}
MAX_PEDIDO = 64 * 1024


def caminho_do_socket(ambiente=None):
    """Onde o socket fica (o pestinha_ctl.py usa a mesma regra), ou None sem XDG_RUNTIME_DIR."""
    ambiente = os.environ if ambiente is None else ambiente
    pasta = ambiente.get("XDG_RUNTIME_DIR") or ""
    return os.path.join(pasta, "pestinha.sock") if pasta else None


def estado(app):
    """O que o painel do sistema mostra: quem é o pet, se está ligado, pausado, escondido e as permissões."""
    perms = app.perms
    return {
        "ok": True,
        "pet": perms["pet"],
        "nome": app.nome,
        "ativo": perms["ativo"],
        "pausado": app.paused,
        "escondido": app.hidden,
        "atalho": bool(app.hotkey.ok),
        "pid": os.getpid(),
        "perms": {chave: perms[chave] for chave in config.DEFAULT_PERMISSIONS if chave not in FORA_DE_PERMS},
    }


def executar(app, pedido):
    """Aplica um pedido já lido e devolve a resposta (dict)."""
    if not isinstance(pedido, dict):
        return {"ok": False, "erro": "o pedido precisa ser um objeto JSON"}
    cmd = pedido.get("cmd")
    if cmd == "status":
        return estado(app)
    if cmd == "perms":
        valores = pedido.get("valores")
        if not isinstance(valores, dict):
            return {"ok": False, "erro": "faltou 'valores'"}
        novos = {k: v for k, v in config.permissoes_validas(valores).items() if k not in FORA_DE_PERMS}
        ignorados = sorted(set(valores) - set(novos))
        if novos:
            app.apply_perms(novos)
            if app.settings and app.settings.isVisible():
                app.settings.close()            # a tela aberta mostraria os valores antigos
        resposta = estado(app)
        if ignorados:
            resposta["ignorados"] = ignorados
        return resposta
    if cmd == "panico":
        if app.perms["ativo"]:
            app.panic()
        return estado(app)
    if cmd == "religar":
        if not app.perms["ativo"]:
            app.apply_perms({"ativo": True})
        return estado(app)
    if cmd == "configuracoes":
        app.open_settings()
        return estado(app)
    if cmd == "pausar":
        app.toggle_pause()
        return estado(app)
    if cmd == "esconder":
        app.toggle_hidden()
        return estado(app)
    if cmd == "sair":
        QTimer.singleShot(0, app.quit)          # responde antes de fechar
        return {"ok": True, "saindo": True}
    return {"ok": False, "erro": f"comando desconhecido: {cmd!r}"}


class ControleLocal(QObject):
    """Servidor do socket local; cada conexão manda uma linha e recebe uma linha."""

    def __init__(self, app, caminho=None):
        """Abre o socket (substituindo um que tenha sobrado de uma execução que caiu)."""
        super().__init__()
        self.app = app
        self.caminho = caminho or caminho_do_socket()
        self.servidor = QLocalServer(self)
        self.servidor.setSocketOptions(QLocalServer.UserAccessOption)
        self.ok = False
        if not self.caminho:
            log("[controle] sem XDG_RUNTIME_DIR: o controle local fica desligado")
            return
        # a trava de instância (main.py) garante que nenhum outro pet usa este socket
        QLocalServer.removeServer(self.caminho)
        self.ok = self.servidor.listen(self.caminho)
        if not self.ok:
            log(f"[controle] não abriu {self.caminho}: {self.servidor.errorString()}")
            return
        self.servidor.newConnection.connect(self._nova_conexao)

    def _nova_conexao(self):
        """Uma conexão chegou: espera a linha do pedido."""
        while self.servidor.hasPendingConnections():
            conexao = self.servidor.nextPendingConnection()
            conexao.setParent(self)
            conexao.readyRead.connect(lambda c=conexao: self._ler(c))
            conexao.disconnected.connect(conexao.deleteLater)
            # quem conecta e não manda nada não fica pendurado
            QTimer.singleShot(2000, conexao, conexao.disconnectFromServer)

    def _ler(self, conexao):
        """Lê o pedido inteiro (até a quebra de linha), responde e fecha."""
        dados = bytes(conexao.peek(MAX_PEDIDO + 1))
        if b"\n" not in dados and len(dados) <= MAX_PEDIDO:
            return                                  # ainda chegando
        linha = bytes(conexao.readAll()).split(b"\n", 1)[0]
        try:
            pedido = json.loads(linha.decode("utf-8"))
        except (UnicodeDecodeError, ValueError):
            resposta = {"ok": False, "erro": "o pedido não é JSON"}
        else:
            try:
                resposta = executar(self.app, pedido)
            except Exception as erro:               # um pedido ruim não derruba o pet
                log(f"[controle] erro no pedido {pedido!r}: {erro}")
                resposta = {"ok": False, "erro": str(erro)}
        conexao.write((json.dumps(resposta, ensure_ascii=False) + "\n").encode("utf-8"))
        conexao.flush()
        conexao.disconnectFromServer()

    def fechar(self):
        """Fecha o socket (ao sair)."""
        if self.servidor.isListening():
            self.servidor.close()
