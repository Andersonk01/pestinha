"""
Tempo ocioso no Wayland pelo protocolo ext-idle-notify-v1: um cliente mínimo que fala o protocolo do
Wayland direto no socket do compositor, sem bibliotecas.

O compositor só manda dois avisos: "ficou parado por N ms" (idled) e "voltou" (resumed). Nenhuma tecla
e nenhuma posição: é a mesma informação que o xprintidle dava no X11.

Formato das mensagens do Wayland (na ordem de bytes da máquina; o socket é local):
    [id do objeto: u32] [tamanho << 16 | opcode: u32] [argumentos, cada um alinhado em 4 bytes]
    string = u32 com o tamanho (contando o \\0), os bytes e o preenchimento até múltiplo de 4
"""

import os
import socket
import struct
import threading
import time

# ids dos objetos que este cliente cria (o 1 é sempre o wl_display)
_DISPLAY, _REGISTRY, _SYNC, _SEAT, _NOTIFIER, _NOTIFICATION = 1, 2, 3, 4, 5, 6

_DISPLAY_SYNC, _DISPLAY_GET_REGISTRY = 0, 1            # pedidos do wl_display
_DISPLAY_ERROR = 0                                      # evento do wl_display
_REGISTRY_BIND = 0                                      # pedido do wl_registry
_REGISTRY_GLOBAL = 0                                    # evento do wl_registry
_CALLBACK_DONE = 0                                      # evento do wl_callback
_GET_IDLE, _GET_INPUT_IDLE = 1, 2                       # pedidos do ext_idle_notifier_v1
_IDLED, _RESUMED = 0, 1                                 # eventos do ext_idle_notification_v1

NOTIFIER = "ext_idle_notifier_v1"
SEAT = "wl_seat"


def string(texto):
    """Uma string no formato do Wayland."""
    dados = texto.encode("utf-8") + b"\0"
    return struct.pack("=I", len(dados)) + dados + b"\0" * (-len(dados) % 4)


def mensagem(objeto, opcode, args=b""):
    """Uma mensagem inteira: cabeçalho e argumentos."""
    return struct.pack("=II", objeto, ((8 + len(args)) << 16) | opcode) + args


def ler_string(dados, pos):
    """(texto, posição depois dele) a partir de `pos`."""
    tamanho = struct.unpack_from("=I", dados, pos)[0]
    texto = dados[pos + 4:pos + 4 + max(0, tamanho - 1)].decode("utf-8", "replace")
    return texto, pos + 4 + tamanho + (-tamanho % 4)


def caminho_do_socket(ambiente=None):
    """Socket do compositor: WAYLAND_DISPLAY absoluto ou dentro de XDG_RUNTIME_DIR; None se não houver."""
    ambiente = os.environ if ambiente is None else ambiente
    nome = ambiente.get("WAYLAND_DISPLAY") or ""
    if not nome:
        return None
    if nome.startswith("/"):
        return nome
    pasta = ambiente.get("XDG_RUNTIME_DIR") or ""
    return os.path.join(pasta, nome) if pasta else None


class Mensagens:
    """Separa o fluxo do socket em mensagens inteiras: (objeto, opcode, argumentos)."""

    def __init__(self):
        """Começa sem nada guardado."""
        self.buffer = b""

    def alimentar(self, dados):
        """Junta o que chegou e devolve as mensagens completas; o resto espera a próxima leitura."""
        self.buffer += dados
        saidas = []
        while len(self.buffer) >= 8:
            objeto, palavra = struct.unpack_from("=II", self.buffer, 0)
            tamanho = palavra >> 16
            if tamanho < 8:
                raise ValueError("mensagem do Wayland com tamanho inválido")
            if len(self.buffer) < tamanho:
                break
            saidas.append((objeto, palavra & 0xFFFF, self.buffer[8:tamanho]))
            self.buffer = self.buffer[tamanho:]
        return saidas


class OciosoWayland:
    """
    Ouve o compositor numa thread. `segundos()` diz há quanto tempo não há teclado nem mouse;
    `disponivel` fica False se o compositor não tiver o protocolo ou se a conexão cair.

    O aviso de "parado" chega depois de `limiar_ms` sem nada; abaixo disso o tempo é 0.
    """

    def __init__(self, limiar_ms=300, relogio=time.monotonic):
        """Ainda não conecta: veja iniciar()."""
        self.limiar_ms = int(limiar_ms)
        self.relogio = relogio
        self.disponivel = False
        self.versao = 0
        self._parado_desde = None
        self._sock = None
        self._pronto = threading.Event()

    def segundos(self):
        """Segundos sem teclado e mouse (0 enquanto há uso ou se o protocolo não está disponível)."""
        desde = self._parado_desde
        if desde is None or not self.disponivel:
            return 0.0
        return max(0.0, self.relogio() - desde)

    def iniciar(self, caminho=None, esperar=1.0):
        """Conecta e começa a ouvir; devolve True se o compositor aceitou o protocolo."""
        caminho = caminho or caminho_do_socket()
        if not caminho:
            return False
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM | socket.SOCK_CLOEXEC)
            sock.settimeout(2.0)
            sock.connect(caminho)
            sock.settimeout(None)
        except OSError:
            return False
        self._sock = sock
        threading.Thread(target=self._laco, name="ocioso-wayland", daemon=True).start()
        self._pronto.wait(esperar)
        return self.disponivel

    def parar(self):
        """Fecha a conexão (a thread termina sozinha)."""
        sock, self._sock = self._sock, None
        self.disponivel = False
        if sock is not None:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            sock.close()

    def _laco(self):
        """Pede a lista de globais, assina o aviso de ociosidade e fica ouvindo."""
        sock = self._sock
        globais = {}
        leitor = Mensagens()
        try:
            sock.sendall(mensagem(_DISPLAY, _DISPLAY_GET_REGISTRY, struct.pack("=I", _REGISTRY))
                         + mensagem(_DISPLAY, _DISPLAY_SYNC, struct.pack("=I", _SYNC)))
            while self._sock is sock:
                dados = sock.recv(4096)
                if not dados:
                    break
                for objeto, opcode, args in leitor.alimentar(dados):
                    if not self.tratar(objeto, opcode, args, globais, sock.sendall):
                        return self._encerrar()
        except (OSError, ValueError, struct.error):
            pass
        self._encerrar()

    def _encerrar(self):
        """A conexão acabou: o tempo ocioso volta a ser 0 (como sem o xprintidle)."""
        self.disponivel = False
        self._parado_desde = None
        self._pronto.set()

    def tratar(self, objeto, opcode, args, globais, enviar):
        """Uma mensagem do compositor; devolve False quando a conversa tem de parar."""
        if objeto == _REGISTRY and opcode == _REGISTRY_GLOBAL:
            nome = struct.unpack_from("=I", args, 0)[0]
            interface, pos = ler_string(args, 4)
            versao = struct.unpack_from("=I", args, pos)[0]
            if interface in (NOTIFIER, SEAT) and interface not in globais:
                globais[interface] = (nome, versao)
        elif objeto == _SYNC and opcode == _CALLBACK_DONE:
            self._assinar(globais, enviar)
            self._pronto.set()
            if not self.disponivel:
                return False
        elif objeto == _NOTIFICATION and opcode == _IDLED:
            self._parado_desde = self.relogio() - self.limiar_ms / 1000.0
        elif objeto == _NOTIFICATION and opcode == _RESUMED:
            self._parado_desde = None
        elif objeto == _DISPLAY and opcode == _DISPLAY_ERROR:
            return False
        return True

    def _assinar(self, globais, enviar):
        """Liga o assento (teclado e mouse) e pede o aviso de ociosidade."""
        if NOTIFIER not in globais or SEAT not in globais:
            return
        nome_seat, _ = globais[SEAT]
        nome_notifier, versao = globais[NOTIFIER]
        self.versao = min(versao, 2)
        bind_seat = struct.pack("=I", nome_seat) + string(SEAT) + struct.pack("=II", 1, _SEAT)
        bind_notifier = (struct.pack("=I", nome_notifier) + string(NOTIFIER)
                         + struct.pack("=II", self.versao, _NOTIFIER))
        # a versão 2 tem o aviso "só de teclado e mouse", que ignora os inibidores (vídeo tocando,
        # modo cafeína): aqui interessa se você está usando o computador, não se a tela pode apagar
        pedido = _GET_INPUT_IDLE if self.versao >= 2 else _GET_IDLE
        enviar(mensagem(_REGISTRY, _REGISTRY_BIND, bind_seat)
               + mensagem(_REGISTRY, _REGISTRY_BIND, bind_notifier)
               + mensagem(_NOTIFIER, pedido, struct.pack("=III", _NOTIFICATION, self.limiar_ms, _SEAT)))
        self.disponivel = True
