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
- `gerar_sons.py` sintetiza os sons (`assets/comum/sons/` e `pets/cypher/sons/`), sempre iguais;
  `gerar_notebook_cypher.py` desenha `pets/cypher/notebook.png`.

| Arquivo | O que faz |
|---|---|
| `fuzz_pestinha.py` | Roda o app inteiro com relógio virtual e ações aleatórias, checando invariantes. |
| `gerar_doc_rede.py` | Gera docs/REDE_NEURAL.md a partir do código (canais, interneurônios, motores, conexões e limiares). |
| `gerar_notebook_cypher.py` | Desenha o notebook do Cypher (pets/cypher/notebook.png): o verso da tampa, escuro, com um cadeado ciano brilhando no meio e adesivos de hacker. |
| `gerar_panfleto.py` | Desenha pets/jorge/bolinha_papel.png: um panfleto de mentoria amassado, que o Jorge atira na revolução. |
| `gerar_readmes.py` | Gera pestinha/README.md e o README de cada camada a partir das docstrings dos módulos. |
| `gerar_sons.py` | Sintetiza os sons do Pestinha do zero (sem gravação nenhuma, então sem licença de terceiros): |
| `medir_cartazes.py` | Mede se cada frase do cartazes.txt de cada pet cabe na placa em que aparece, com as fontes de verdade. |
| `pestinha_ctl.py` | Fala com o Pestinha que está rodando, pelo controle local (pestinha/controle/remoto.py). |
