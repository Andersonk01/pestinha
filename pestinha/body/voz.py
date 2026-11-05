"""
VOZ - os sons do pet: acha o arquivo (pets/<pet>/sons/ e depois assets/comum/sons/), aplica o volume e
toca pelo tocador do sistema (plataforma.Tocador). Não decide quando tocar: isso é mind/sons.py.

O volume vai no próprio arquivo: na primeira vez, grava uma cópia com o ganho do nível escolhido em
memory/cache/sons/ (some junto com "apagar todos os dados"). Um som que não existe, ou não abre, vira
silêncio: nunca derruba o pet.
"""

import hashlib
import random
import wave
from pathlib import Path

import numpy as np

from .. import plataforma
from ..log import log

GANHO = {"baixo": 0.22, "medio": 0.45, "alto": 0.85}     # os níveis de config.VOLUMES
PASTA = "sons"


def duracao(caminho):
    """Segundos de um .wav."""
    with wave.open(str(caminho), "rb") as w:
        return w.getnframes() / w.getframerate()


class Voz:
    """Toca os sons de um personagem, no volume escolhido, em canais que dá para parar (ex.: a digitação)."""

    def __init__(self, conteudo, cache, tocador=None, rng=None):
        """`conteudo`: ConteudoPaths do pet; `cache`: onde guardar as cópias com volume."""
        self.conteudo = conteudo
        self.cache = Path(cache)
        self.tocador = tocador if tocador is not None else plataforma.Tocador()
        self.rng = rng or random.Random()
        self.ligada = True
        self.volume = "medio"
        self._canais = {}           # canal -> identificador do som tocando nele
        self._duracoes = {}         # arquivo original -> segundos
        self._ruins = set()         # arquivos que não abriram: não tenta de novo a cada som

    def configurar(self, ligada, volume):
        """Liga ou desliga e escolhe o volume; desligar para o que estiver tocando."""
        self.ligada = bool(ligada)
        if volume in GANHO:
            self.volume = volume
        if not self.ligada:
            self.parar_tudo()

    def arquivo(self, nome):
        """O .wav do som `nome` (o do pet, senão o comum), ou None."""
        caminho = self.conteudo.resolver(f"{PASTA}/{nome}.wav")
        return caminho if caminho.is_file() else None

    def variantes(self, prefixo):
        """Os sons `prefixo_1`, `prefixo_2`... que existem; se o pet tiver os dele, valem no lugar dos comuns."""
        for pasta in self.conteudo.pastas(PASTA):
            nomes = sorted(p.stem for p in pasta.glob(f"{prefixo}_*.wav")) if pasta.is_dir() else []
            if nomes:
                return nomes
        return []

    def tocar(self, nome, canal=None):
        """Toca o som `nome`. Devolve quantos segundos ele dura (0 se ficou em silêncio)."""
        if not self.ligada or not self.tocador.disponivel:
            return 0.0
        origem = self.arquivo(nome)
        pronto = self._com_volume(origem) if origem is not None else None
        if pronto is None:
            return 0.0
        if canal is not None:
            self.parar(canal)
        identificador = self.tocador.tocar(pronto)
        if identificador is None:
            return 0.0
        if canal is not None:
            self._canais[canal] = identificador
        return self._duracoes.get(origem, 0.0)

    def tocar_um_de(self, prefixo, canal=None):
        """Toca uma das variantes de `prefixo`, sorteada."""
        nomes = self.variantes(prefixo)
        return self.tocar(self.rng.choice(nomes), canal) if nomes else 0.0

    def parar(self, canal):
        """Para o som do canal (se ainda estiver tocando)."""
        self.tocador.parar(self._canais.pop(canal, None))

    def parar_tudo(self):
        """Silêncio."""
        self._canais.clear()
        self.tocador.parar_todos()

    def _com_volume(self, origem):
        """A cópia de `origem` com o ganho do volume atual, gravada uma vez no cache."""
        if origem in self._ruins:
            return None
        try:
            info = origem.stat()
            chave = hashlib.sha1(f"{origem.resolve()}|{info.st_mtime_ns}|{info.st_size}".encode()).hexdigest()[:12]
            destino = self.cache / f"{origem.stem}-{chave}-{self.volume}.wav"
            if destino.is_file():
                self._duracoes.setdefault(origem, duracao(destino))
                return destino
            with wave.open(str(origem), "rb") as w:
                params = w.getparams()
                if params.sampwidth != 2:
                    raise ValueError("só .wav de 16 bits")
                amostras = np.frombuffer(w.readframes(params.nframes), dtype="<i2")
            escalado = np.clip(amostras.astype(np.float32) * GANHO[self.volume], -32768, 32767).astype("<i2")
            self.cache.mkdir(parents=True, exist_ok=True)
            temporario = destino.with_name(destino.name + ".tmp")
            with wave.open(str(temporario), "wb") as w:
                w.setnchannels(params.nchannels)
                w.setsampwidth(2)
                w.setframerate(params.framerate)
                w.writeframes(escalado.tobytes())
            temporario.replace(destino)
            self._duracoes[origem] = params.nframes / params.framerate
            return destino
        except (OSError, EOFError, ValueError, wave.Error) as erro:
            self._ruins.add(origem)
            log(f"[som] não deu para tocar {origem.name}: {erro}")
            return None
