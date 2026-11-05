"""
SOM - toca um .wav sem travar o pet, com o tocador que o sistema tiver.

Linux: pw-play (PipeWire), paplay (PulseAudio) ou aplay (ALSA), o primeiro que existir. macOS: afplay.
Windows: winsound (um som por vez: um novo corta o anterior). Cada som é um processo curto que termina
sozinho. O volume já vem no próprio arquivo (body/voz.py grava cópias com o volume escolhido), então
nenhum tocador precisa saber de volume. PESTINHA_SEM_SOM=1 deixa tudo mudo (os testes usam).
"""

import os
import shutil
import subprocess
import sys

TOCADORES_LINUX = (("pw-play",), ("paplay",), ("aplay", "-q"))
MAX_SIMULTANEOS = 4                 # mais que isso é barulho: o som novo fica de fora


class Tocador:
    """Começa e para sons. `tocar` devolve um identificador para `parar`, ou None se não tocou."""

    def __init__(self, sistema=sys.platform, ambiente=None, which=shutil.which, popen=subprocess.Popen):
        """Escolhe o tocador do sistema (ou nenhum, com PESTINHA_SEM_SOM)."""
        ambiente = os.environ if ambiente is None else ambiente
        self._popen = popen
        self._tocando = []          # processos que ainda podem estar tocando
        self.comando = None
        self._winsound = None
        if ambiente.get("PESTINHA_SEM_SOM"):
            return
        if sistema == "win32":
            try:
                import winsound
                self._winsound = winsound
            except ImportError:
                pass
        elif sistema == "darwin":
            if which("afplay"):
                self.comando = ("afplay",)
        else:
            for comando in TOCADORES_LINUX:
                if which(comando[0]):
                    self.comando = comando
                    break

    @property
    def disponivel(self):
        """Há como tocar som aqui."""
        return self.comando is not None or self._winsound is not None

    def tocar(self, caminho):
        """Começa a tocar o arquivo e volta na hora."""
        if self._winsound is not None:
            flags = self._winsound.SND_FILENAME | self._winsound.SND_ASYNC | self._winsound.SND_NODEFAULT
            try:
                self._winsound.PlaySound(str(caminho), flags)
            except RuntimeError:
                return None
            return "winsound"
        if self.comando is None:
            return None
        self._recolher()
        if len(self._tocando) >= MAX_SIMULTANEOS:
            return None
        try:
            processo = self._popen([*self.comando, str(caminho)], stdin=subprocess.DEVNULL,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, close_fds=True)
        except OSError:
            return None
        self._tocando.append(processo)
        return processo

    def parar(self, identificador):
        """Para um som que ainda está tocando (o que já acabou é ignorado)."""
        if identificador is None:
            return
        if identificador == "winsound":
            if self._winsound is not None:
                self._winsound.PlaySound(None, 0)
            return
        if identificador.poll() is None:
            try:
                identificador.terminate()
            except OSError:
                pass
        self._recolher()

    def parar_todos(self):
        """Silêncio: para tudo que estiver tocando."""
        if self._winsound is not None:
            self._winsound.PlaySound(None, 0)
        for processo in list(self._tocando):
            self.parar(processo)

    def _recolher(self):
        """Esquece os processos que já terminaram (e evita processos zumbis)."""
        self._tocando = [p for p in self._tocando if p.poll() is None]
