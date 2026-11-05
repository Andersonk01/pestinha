# `ferramentas/` — geradores de documentação

> Gerado por `ferramentas/gerar_readmes.py` a partir das docstrings. Não edite à mão: rode o script.

Rode depois de mudar módulos ou a rede, para a documentação não desatualizar:

```bash
python ferramentas/gerar_readmes.py
python ferramentas/gerar_doc_rede.py
```

- `fuzz_pestinha.py` roda o app com ações aleatórias e checa invariantes:
  `python -B ferramentas/fuzz_pestinha.py 150 80` (rodadas, ações por rodada).
- `medir_cartazes.py` confere se cada frase cabe na placa (rode no Windows, com as fontes reais);
  `PESTINHA_IDIOMA=en` mede os cartazes em inglês (`cartazes.en.txt`).
- `gerar_sons.py` sintetiza os sons (`assets/comum/sons/`, `pets/cypher/sons/` e `pets/bolota/sons/`),
  sempre iguais; `gerar_notebook_cypher.py` desenha `pets/cypher/notebook.png`.
- `gerar_bolota.py` tira os olhos e as patinhas da arte do Bolota (`ferramentas/arte/bolota.png`) e grava
  o pelo em `pets/bolota/corpo.png` e o tufo que ele atira em `pets/bolota/bolinha_papel.png`.

| Arquivo | O que faz |
|---|---|
| `fuzz_pestinha.py` | Roda o app inteiro com relógio virtual e ações aleatórias, checando invariantes. |
| `gerar_bolota.py` | Prepara o corpo do Bolota (pets/bolota/corpo.png) a partir da arte original (ferramentas/arte/bolota.png): só o pelo, sem os olhos e sem as patinhas, que o pet desenha por código por cima (body/desenho_bola.py) para piscar, mudar de expressão, acenar, correr e rolar. |
| `gerar_doc_rede.py` | Gera docs/REDE_NEURAL.md a partir do código (canais, interneurônios, motores, conexões e limiares). |
| `gerar_notebook_cypher.py` | Desenha o notebook do Cypher (pets/cypher/notebook.png): o verso da tampa, escuro, com um cadeado ciano brilhando no meio e adesivos de hacker. |
| `gerar_panfleto.py` | Desenha pets/jorge/bolinha_papel.png: um panfleto de mentoria amassado, que o Jorge atira na revolução. |
| `gerar_readmes.py` | Gera pestinha/README.md e o README de cada camada a partir das docstrings dos módulos. |
| `gerar_sons.py` | Sintetiza os sons do Pestinha do zero (sem gravação nenhuma, então sem licença de terceiros): |
| `medir_cartazes.py` | Mede se cada frase do cartazes.txt de cada pet cabe na placa em que aparece, com as fontes de verdade. |
| `pestinha_ctl.py` | Fala com o Pestinha que está rodando, pelo controle local (pestinha/controle/remoto.py). |
