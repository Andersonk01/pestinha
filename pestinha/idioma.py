"""
IDIOMA - em que idioma o pet fala: o do sistema, português ou inglês.

Os textos do código são escritos em português e passam por `tr()`. Em inglês, `tr` devolve a tradução
de `idioma_en.TEXTOS`, cuja chave é o próprio texto em português. Um texto guardado numa constante
(rótulos, permissões, nomes de emoção) é marcado com `N_()` onde nasce e traduzido com `tr()` onde
aparece, porque o idioma só é decidido quando o programa abre. tests/test_idioma.py confere que todo
texto marcado tem tradução, com os mesmos {campos}, e que nenhuma tradução sobra.

O conteúdo dos personagens (cartazes, recadinhos, memes) tem uma versão por idioma ao lado da original:
`cartazes.en.txt` junto do `cartazes.txt`, `memes.en/` junto de `memes/` (paths.py).

PESTINHA_IDIOMA=pt|en escolhe na mão. Sem ela, vale o idioma do sistema: LC_ALL, LC_MESSAGES ou LANG
e, sem nenhuma (Windows, macOS), o que o Qt informa. Qualquer idioma que não seja português vira inglês.
"""
import os

ORIGINAL = "pt"                      # o idioma em que os textos são escritos
IDIOMAS = ("pt", "en")
_VARIAVEIS = ("LC_ALL", "LC_MESSAGES", "LANG")
_atual = None


def escolher(nome):
    """'pt_BR.UTF-8', 'pt-PT', 'Portuguese_Brazil' -> 'pt'; outro idioma -> 'en'; vazio, 'C', 'POSIX' -> None."""
    n = (nome or "").strip().lower()
    if not n or n in ("c", "posix") or n.startswith("c."):
        return None
    return "pt" if n.startswith(("pt", "portug")) else "en"


def do_sistema(nome_qt=""):
    """O idioma a usar: o de PESTINHA_IDIOMA, senão o das variáveis do sistema, senão o do Qt, senão inglês."""
    pedido = os.environ.get("PESTINHA_IDIOMA", "").strip().lower()
    if pedido in IDIOMAS:
        return pedido
    for variavel in _VARIAVEIS:
        achado = escolher(os.environ.get(variavel, ""))
        if achado:
            return achado
    return escolher(nome_qt) or "en"


def definir(codigo):
    """Fixa o idioma ('pt' ou 'en'); o programa chama ao abrir, com o que do_sistema escolheu."""
    global _atual
    if codigo not in IDIOMAS:
        raise ValueError(f"idioma desconhecido: {codigo!r}")
    _atual = codigo


def atual():
    """O idioma em uso. Antes de definir(), o das variáveis do sistema."""
    global _atual
    if _atual is None:
        _atual = do_sistema()
    return _atual


def tr(texto, **valores):
    """O texto no idioma atual (a chave é o texto em português); `valores` preenchem os {campos}."""
    if atual() != ORIGINAL:
        from .idioma_en import TEXTOS
        texto = TEXTOS.get(texto, texto)
    return texto.format(**valores) if valores else texto


def N_(texto):
    """Marca um texto para traduzir: ele fica em português na constante e passa por tr() onde aparece."""
    return texto
