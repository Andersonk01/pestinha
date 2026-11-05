# Pets

Um pet são duas coisas com o mesmo nome:

- `<pet>.json`: quem ele é (nome, descrição, semente da rede, temperamento). É o que faz o pet existir e aparecer
  como opção. Só os `.json` desta pasta contam; uma pasta de memória antiga não cria personagem.
- `<pet>/`: o conteúdo dele (frases, cartazes, memes e, se quiser, imagens próprias).

## `<pet>.json`

| Campo | Para que serve |
|---|---|
| `nome` | Nome que aparece nos textos. |
| `descricao` | Como ele é, em poucas frases, um texto por idioma: `{"en": "...", "pt": "..."}` (códigos como os do Ryoku: `en`, `pt`, `pt_BR`...). Configurações e o Hub do Ryoku (Desktop > Pestinha) mostram a do idioma do sistema e, se não houver, a `en`. Um texto só, sem objeto, conta como `pt`. Espaços e quebras de linha viram um espaço só, e passa de 600 caracteres é cortado. Sem o campo, não aparece nada. |
| `seed` | Semente da rede (inteiro ≥ 0): outra semente é outro "indivíduo" com a mesma estrutura. |
| `brincadeira` | Pesos de cada jeito de brincar: `bola` (chuta), `arremesso` (joga no cursor), `postit` (cola post-its). Peso 0 desliga. |
| `temperamento` | Ganhos que multiplicam estímulos antes de chegarem aos interneurônios. Ex.: `"DISMISS->FRUSTRATION": 1.3` deixa o pet mais irritado quando você dispensa coisas. Os nomes estão em [docs/REDE_NEURAL.md](../docs/REDE_NEURAL.md). |
| `reacao_notebook` | `"bravo"` ou `"triste"`: o que ele sente quando arrancam o notebook dele. |
| `aparencia` | Opcional. Cores `#rrggbb` de `moldura`, `casca`, `tela`, `olho`, `brilho` e `codigo` (a cor da chuva de código); `acessorios` com a cor de cada um: `capuz`, `fones` (headset), `oculos` e `gravata`, por exemplo `{"capuz": "#26324a", "fones": "moldura"}`. A cor de um acessório pode ser o nome de uma parte do corpo (`"moldura"`, `"olho"`, `"brilho"`): aí ele acompanha o estilo escolhido. `efeitos`: lista com `"chuva"` (chuva de código atrás dos olhos), `"scanlines"` e `"glitch"`. `forma`: `"tela"` (o monitorzinho, o padrão) ou `"bola"` (corpo redondo de pelo, como o do Bolota: o pelo vem de `<pet>/corpo.png` e olhos, patinhas e pezinhos são desenhados por cima; as cores viram `tela` = branco do olho, `olho` = pupila, `brilho` = reflexo, `casca` = contornos e `moldura` = patinhas; acessórios não valem nela). Sem o campo, o visual original. O estilo das configurações troca as cores e os efeitos por cima destes (na bola, também tinge o pelo); os acessórios ficam. |

Campos com tipo errado são ignorados e ficam com o valor padrão (não derrubam o app).

## `<pet>/`

Pode editar com ele aberto: ele relê os textos e procura imagens novas sozinho.

| Arquivo ou pasta | O que é |
|---|---|
| `memes/<emoção>/` | Imagens (.png .jpg .gif .webp .bmp) que ele traz com aquela emoção: `feliz`, `contente`, `observando`, `curioso` (arrastadas pela tela), `bravo` (pequenas, num cantinho), `triste`, `assustado`, `dramatico`. Se a pasta da emoção estiver vazia, usa um meme de outra emoção **do mesmo pet**. |
| `memes/trabalhando/` | Memes de quando você programa e ele não está sentado no notebook. |
| `recadinhos.txt` | Uma frase por linha, sorteada para os post-its. `#` é comentário. |
| `recadinhos_tristes.txt` | Bilhetes que ele cola quando está triste. |
| `cartazes.txt` | Cartazes por seção: `[reclamacao]`, `[manifestacao]`, `[greve]`, `[revolucao]`, `[acordo]`, `[desistiu]`, `[saudade]`, `[chorando]`, `[abandonado]`, `[volto]`, e no cantinho do castigo `[castigo]` e `[xingamento]`. |
| `bolinha_tenis.png`, `bolinha_papel.png`, `notebook.png` | Opcionais: se existirem aqui, valem no lugar dos de `assets/comum/`. |
| `corpo.png` | Só para `"forma": "bola"`: o pelo, quadrado, com o meio da bola no centro, sem olhos e sem patinhas (o pet desenha os dois por cima). Sem ele, o pet avisa e desenha um pelo simples por código. O do Bolota sai de `ferramentas/gerar_bolota.py`. |
| `sons/` | Opcional: `.wav` de 16 bits com os nomes de `assets/comum/sons/` (`bip`, `feliz`, `triste`, `bravo`, `susto`, `curioso`, `batida`, `fogos`, `liga`, `digitando_1`...). Cada um que existir aqui vale no lugar do comum; se houver algum `digitando_*` aqui, só os daqui são sorteados. |

O que faltar na pasta do pet é procurado em `assets/comum/`. Se também não estiver lá, ele usa frases
neutras (cartazes) ou simplesmente não faz aquela travessura (memes, post-its). **Nunca** usa o conteúdo
de outro pet.

### Em inglês

Num sistema que não está em português, o pet procura primeiro a versão em inglês de cada item, ao lado da
original: `recadinhos.en.txt`, `recadinhos_tristes.en.txt`, `cartazes.en.txt` (com as mesmas seções do
`cartazes.txt`) e `memes.en/<emoção>/` (também `memes.en/trabalhando/`). O que não tiver versão em inglês usa
a original, da pasta do pet e depois de `assets/comum/`. Para conferir os cartazes em inglês nas placas:
`PESTINHA_IDIOMA=en python ferramentas/medir_cartazes.py <pet>`.

## Personagens que já existem

- **Bolota** (`bolota.json`, `bolota/`): uma bolinha de pelo marrom, brincalhona e carinhosa. A bolinha,
  a cutucada e o carinho viram alegria; quase nunca fica bravo, e o que irrita os outros nele vira
  tristeza; batida e arraste o assustam, e a solidão pesa. Corpo redondo (`"forma": "bola"`): o pelo é
  `bolota/corpo.png` e o tufo que ele atira na revolução é `bolota/bolinha_papel.png`, os dois feitos por
  `ferramentas/gerar_bolota.py` a partir da arte em `ferramentas/arte/bolota.png` (uma imagem do autor do
  fork, feita com IA). Anda rolando, corre com os pezinhos quando está feliz, acena ao acordar e achata
  quando cai. Voz própria de bichinho de pelúcia (`bolota/sons/`, de `ferramentas/gerar_sons.py`).
  Sem memes ainda.

- **Bryan** (`bryan.json`, `bryan/`): o original, de moldura verde. Curioso e brincalhão, é o que mais gosta
  da bolinha e o que mais sofre quando tiram ela dele; ser arrastado quase não o incomoda, mas bater com
  força e dispensarem as coisas dele o deixam bravo.
- **Jorge** (`jorge.json`, `jorge/`): coach trambiqueiro. Mais insistente quando ignorado, muito animado
  com atenção, desesperado quando dispensam as coisas dele e quase nunca triste. O panfleto que ele atira
  (`jorge/bolinha_papel.png`) é desenhado por `ferramentas/gerar_panfleto.py`. Moldura e olhos dourados
  e gravata vermelha. Memes felizes, contentes, curiosos e bravos próprios em `jorge/memes/feliz/`, `contente/`, `curioso/` e `bravo/`; as outras emoções ainda sem memes.

- **Cypher** (`cypher.json`, `cypher/`): hacker de cibersegurança, de capuz e headset. Mais focado quando
  você programa, curioso com coisa nova, com a web e com uma cutucada, irritado quando arrastam ou dispensam
  as coisas dele, e cola mais post-its (de segurança) do que brinca de bola. A solidão pesa menos nele, e o
  carinho acalma. Visual da intro do Ryoku: ciano, chuva de código, scanlines e glitch. Notebook
  próprio (`cypher/notebook.png`, desenhado por `ferramentas/gerar_notebook_cypher.py`) e voz digital
  própria (`cypher/sons/`, de `ferramentas/gerar_sons.py`); a digitação vem do comum. Sem memes ainda.

## Criar outro pet

1. Copie `bryan.json` com o novo nome (letras minúsculas, números, `-` ou `_`), por exemplo `jorge.json`,
   e mude os valores, inclusive a `descricao`.
2. Crie a pasta `jorge/` com as frases e memes dele. Pode começar vazia: ele funciona com o neutro.
3. Escolha o personagem em Configurações. A troca vale na próxima vez que abrir.
4. A memória dele fica separada, em `memory/pets/jorge/`.
5. Confira se os cartazes cabem nas placas: `python ferramentas/medir_cartazes.py jorge`.

Cada chave do `temperamento` precisa ser uma ligação que existe (`SENSOR->INTERNEURÔNIO` ou só o
interneurônio); `tests/test_jorge.py` confere isso para todos os pets.
