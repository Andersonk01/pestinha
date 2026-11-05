#!/usr/bin/env python3
"""
Fala com o Pestinha que está rodando, pelo controle local (pestinha/controle/remoto.py).
Só usa a biblioteca padrão: roda com o Python do sistema, sem o venv e sem o Qt.

    pestinha_ctl.py status                    estado e permissões (JSON)
    pestinha_ctl.py perms bolinha=off fogos=on muda permissões (as da tela de configurações)
    pestinha_ctl.py perms estilo=rosa volume=baixo   as escolhas também (o pet confere as opções)
    pestinha_ctl.py panico                    o mesmo que Ctrl+Alt+Shift+B
    pestinha_ctl.py religar                   liga de novo depois do pânico
    pestinha_ctl.py configuracoes             abre a tela de configurações
    pestinha_ctl.py pausar | esconder         alterna
    pestinha_ctl.py sair                      salva e fecha

Saída: a resposta em JSON. Código de saída 0 se deu certo, 1 se o pet não está rodando, 2 se o pedido
foi recusado.
"""

import json
import os
import re
import socket
import sys

SIMPLES = {"status", "panico", "religar", "configuracoes", "pausar", "esconder", "sair"}
VERDADE = {"1", "true", "on", "sim", "yes"}
MENTIRA = {"0", "false", "off", "nao", "não", "no"}
ESCOLHAS = {"estilo", "volume"}              # as permissões que são uma opção, não liga/desliga
OPCAO = re.compile(r"[a-z0-9_-]{1,24}")      # o valor de uma escolha (estilo=cyber, volume=alto)


def caminho_do_socket(ambiente=None):
    """A mesma regra do pestinha/controle/remoto.py."""
    ambiente = os.environ if ambiente is None else ambiente
    pasta = ambiente.get("XDG_RUNTIME_DIR") or f"/run/user/{os.getuid()}"
    return os.path.join(pasta, "pestinha.sock")


def montar_pedido(args):
    """O pedido em dict a partir dos argumentos; ValueError se não fizer sentido."""
    if not args:
        raise ValueError("faltou o comando")
    cmd, resto = args[0], args[1:]
    if cmd in SIMPLES:
        if resto:
            raise ValueError(f"{cmd} não recebe argumentos")
        return {"cmd": cmd}
    if cmd == "perms":
        valores = {}
        for item in resto:
            chave, sep, valor = item.partition("=")
            if not sep or not chave:
                raise ValueError(f"use chave=valor: {item!r}")
            texto = valor.strip().lower()
            if chave in ESCOLHAS:
                if not OPCAO.fullmatch(texto):
                    raise ValueError(f"opção inválida para {chave}: {valor!r}")
                valores[chave] = texto              # quem confere se a opção existe é o pet
            elif texto in VERDADE:
                valores[chave] = True
            elif texto in MENTIRA:
                valores[chave] = False
            else:
                raise ValueError(f"valor de {chave} precisa ser on/off: {valor!r}")
        if not valores:
            raise ValueError("perms precisa de pelo menos um chave=valor")
        return {"cmd": "perms", "valores": valores}
    raise ValueError(f"comando desconhecido: {cmd!r}")


def enviar(pedido, caminho=None, tempo=3.0):
    """Manda o pedido e devolve a resposta (dict); None se o pet não está rodando."""
    caminho = caminho or caminho_do_socket()
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.settimeout(tempo)
            sock.connect(caminho)
            sock.sendall((json.dumps(pedido) + "\n").encode("utf-8"))
            partes = []
            while True:
                bloco = sock.recv(65536)
                if not bloco:
                    break
                partes.append(bloco)
                if b"\n" in bloco:
                    break
    except (FileNotFoundError, ConnectionRefusedError):
        return None
    except OSError as erro:
        return {"ok": False, "erro": str(erro)}
    try:
        return json.loads(b"".join(partes).decode("utf-8"))
    except ValueError:
        return {"ok": False, "erro": "resposta inválida"}


def main(argv=None):
    """Linha de comando."""
    args = sys.argv[1:] if argv is None else argv
    if not args or args[0] in ("-h", "--help"):
        print(__doc__.strip())
        return 0
    try:
        pedido = montar_pedido(args)
    except ValueError as erro:
        print(json.dumps({"ok": False, "erro": str(erro)}, ensure_ascii=False))
        return 2
    resposta = enviar(pedido)
    if resposta is None:
        print(json.dumps({"ok": False, "rodando": False}))
        return 1
    print(json.dumps(resposta, ensure_ascii=False))
    return 0 if resposta.get("ok") else 2


if __name__ == "__main__":
    sys.exit(main())
