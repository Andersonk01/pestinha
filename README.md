# Pestinha

Pets de tela para Windows, macOS e Linux, cada um com o próprio cérebro. São três personagens por enquanto:

- **Bryan**, o original: uma telinha com dois olhos que mora no seu monitor principal. Cai, quica, pousa nas
  barras de título das janelas, brinca com uma bolinha, trabalha num notebook quando você programa, apronta
  com memes e post-its, protesta contra o cursor quando fica bravo e aprende com o seu carinho.
- **Jorge**, um personagem de sátira: um "coach" de finanças e IA que vive tentando vender mentorias para
  quem está na frente do computador. **Jorge não é uma referência a nenhum coach, empresa ou pessoa real.**
  É um personagem inventado para fazer piada com a cultura de promessas de enriquecimento rápido. Não vende,
  cobra nem pede nada de ninguém.
- **Cypher**, um hacker de cibersegurança de capuz e headset, com a tela em ciano, chuva de código e glitch.
  Trabalha junto quando você programa e cola post-its de segurança. É brincadeira: não invade nem testa nada.

Os três têm a mesma rede neural, mas cada um tem seu temperamento, seu conteúdo e sua memória, separados.
Quem decide o que o pet sente e faz é uma **rede neural pulsada** de 470 neurônios (integração e disparo com
vazamento), alimentada pelo que acontece no seu computador e pelo que você faz com ele. Algumas regras
do programa (limiares, o que pode ou não acontecer) são escritas à mão; a seção
[Como a decisão funciona](docs/ARQUITETURA.md#como-a-decisão-funciona) explica o que é aprendido e o que é regra.

> Projeto em desenvolvimento. Algumas coisas podem não funcionar direito e o comportamento pode
> mudar entre versões.

## Personagens

Cada personagem é um `pets/<pet>.json` (quem ele é) mais uma pasta `pets/<pet>/` (as frases, cartazes e
memes dele). Todos usam a mesma rede neural, mas cada um tem a própria memória: o que um aprende não
passa para o outro. Você escolhe o personagem em **Configurações**; a troca vale na próxima vez que abrir.
Para criar um, veja [pets/README.md](pets/README.md).

O **estilo** (também em Configurações) troca as cores de qualquer personagem na hora, sem reabrir:
Original (as dele), Rosa, Cyber (ciano com chuva de código, scanlines e glitch, como a intro do Ryoku),
Matrix e Âmbar. Os acessórios continuam os do personagem. No Bolota, o estilo tinge o pelo e acende as pupilas.

| Personagem | Como ele é |
|---|---|
| **Bolota** | Uma bolinha de pelo marrom, de olhos enormes e patinhas curtas. É o mais brincalhão: anda rolando pela tela, corre com os pezinhos quando está feliz e acena quando acorda. Adora a bolinha (ele também é uma) e se derrete com carinho, que vira alegria na hora. Quase nunca fica bravo: o que irrita os outros nele vira tristeza. Uma batida forte ou ser arrastado o assustam, e a solidão pesa. Na revolução, atira tufos de pelo. O corpo é redondo e o pelo vem de uma imagem; olhos, patinhas e pezinhos são desenhados por cima, e os estilos tingem o pelo. Tem voz própria, de bichinho de pelúcia. Sem memes ainda. |
| **Bryan** | O original, de moldura verde. Curioso e brincalhão, é o que mais gosta da bolinha e fica triste de verdade quando tiram ela dele. Ser arrastado quase não o incomoda, mas bater com força ou ter as coisas dele dispensadas o deixa bravo: protesta contra o cursor, o Alt+F4 e o Gerenciador de Tarefas, faz greve e chega à revolução, atirando bolinhas de papel. |
| **Cypher** | Hacker de cibersegurança, de capuz e headset, com a tela em ciano, chuva de código e glitch. É o mais focado: quando você digita ou programa, senta no notebook dele e trabalha junto. Coisa nova, a web e uma cutucada o deixam curioso, e a solidão pesa menos nele. Se irrita quando o arrastam ou dispensam as coisas dele; carinho acalma. Entediado, prefere colar post-its de segurança ("2FA. ATIVE. AGORA.") a brincar de bola. Tem o próprio notebook cheio de adesivos e uma voz digital. É brincadeira: não invade nem testa nada. |
| **Jorge** | Coach de finanças e IA, trambiqueiro e confiante, de moldura dourada e gravata vermelha. Ignorado, insiste: o tédio vira curiosidade e brincadeira. Com atenção, se anima muito. Quase nunca fica triste, mas se desespera quando recusam ou dispensam as coisas dele. Os mesmos estágios viram prospecção, marketing agressivo, "assinatura premium" (só no cartaz) e colapso financeiro; ele atira panfletos de mentoria. Personagem de sátira: não é referência a nenhum coach, empresa ou pessoa real, e não vende, cobra nem bloqueia nada. Tem cinco memes felizes, contentes, curiosos e bravos próprios; as outras emoções ainda não têm. |

Um resumo de cada um fica no campo `descricao` do `pets/<pet>.json`, em inglês e em português. Aparece em
**Configurações**, embaixo da escolha do personagem, e, no Ryoku, em Hub > Desktop > Pestinha, que lista todos;
os dois no idioma do sistema.

## O que o pet faz

| | |
|---|---|
| **Corpo** | Gravidade, quique, giro, pouso nas barras de título. Você arrasta, joga e gira com a rodinha. |
| **Emoções** | Saem dos motores da rede: feliz, contente, curioso, observando, bravo, triste, assustado, dramático, dormindo. |
| **Carinho** | Passe o mouse de um lado para o outro em cima dele: fecha os olhinhos de felicidade e aprende com isso. |
| **Bolinha** | Ele chuta e arremessa uma bolinha de tênis; você pode pegar, levar embora (ele reage) ou guardar. |
| **Notebook** | Quando você trabalha (VS Code, Visual Studio, PyCharm, Claude, Codex), ele pode sentar atrás do notebook e trabalhar junto. Você também pode pedir; ele decide se quer. |
| **Travessuras** | Traz memes, fotos e post-its para a tela. Com que frequência é decidido pela rede (tédio, curiosidade). |
| **Protesto** | Bravo por muito tempo: reclamação, manifestação, greve e revolução contra o cursor, com cartazes e bolinhas de papel. |
| **Tristeza** | Sozinho ou ignorado, fica triste, vai para o cantinho e cola bilhetes tristes. |
| **Cantinho do castigo** | Uma placa que você arrasta para onde quiser. Solte ele na frente dela e ele fica de castigo: olha para você, vira de costas, xinga em cartazes e, se a frustração durar, foge. Carinho faz ele perdoar. |
| **Sono e fogos** | Dorme quando a energia acaba. Muito feliz, solta fogos de artifício. |
| **Sons** | Bipes quando você cutuca, faz carinho, ele bate, se assusta, fica bravo, triste ou curioso, e o barulhinho dele digitando enquanto trabalha no notebook. Tudo sintetizado (nada gravado), com volume baixo, médio ou alto, e dá para desligar em Configurações. |

Tudo o que ele aprende (carinho, condicionamento, o que deu certo nas travessuras, fugas do castigo)
fica salvo localmente e muda o jeito dele com o tempo.

## Requisitos

- Windows 10 ou 11, macOS (Quartz/pyobjc), Linux com X11 ou Linux com Hyprland (Wayland, ver abaixo).
- Python 3.11 ou mais novo, e o `git` para baixar.
- No Linux com X11, para as janelas e o tempo ocioso: `xdotool`, `wmctrl` e `xprintidle`. Sem eles, o pet
  continua andando, mas não enxerga as janelas.
- No Hyprland: o 0.55 ou mais novo com a config em Lua (testado no 0.57), ou do 0.53 ao 0.56 com o
  `hyprland.conf`, e o XWayland ligado (já vem ligado). Lá, `xdotool`, `wmctrl` e `xprintidle` não são
  usados.
- Cerca de 70 MB de RAM com ele rodando.

## Instalação e uso

Este é o fork [Andersonk01/pestinha](https://github.com/Andersonk01/pestinha), que traz o suporte ao Hyprland
no branch `anderson` (o `main` é igual ao projeto original). Baixe o branch e instale as dependências num
ambiente virtual (o Arch e outras distribuições não deixam o `pip` instalar no Python do sistema):

```bash
git clone -b anderson https://github.com/Andersonk01/pestinha.git
cd pestinha
python -m venv .venv
.venv/bin/pip install -r requirements.txt
```
```bash
.venv/bin/python main.py
```

No Windows, os mesmos comandos usam `.venv\Scripts\pip` e `.venv\Scripts\python`. Para atualizar depois,
`git pull` na pasta e, se o `requirements.txt` mudou, o `pip install` de novo.

Na primeira vez, um passo a passo explica o que ele vê e não vê, e depois abre a tela de permissões. Depois
de clicar em **Começar**, as próximas aberturas vão direto para o pet. A tela volta a aparecer se o pânico
tiver desligado o programa. Para abrir a tela de propósito:

```bash
python main.py --configurar
```

Com o programa aberto, as opções também ficam em **Configurações**, no ícone da bandeja. No Windows, é lá que
se marca **Abrir o Pestinha ao entrar no Windows**. Só uma cópia abre por vez.

### Linux com Hyprland

Dentro de uma sessão do Hyprland, o pet usa sozinho o backend do Hyprland. Falta só a config do Hyprland:

1. Instale como acima. Nos exemplos, troque `/caminho/do/pestinha` pela pasta do clone (por exemplo
   `/home/voce/pestinha`).
2. Na config do Hyprland, acrescente a regra das janelas do pet (flutuam em todas as áreas de trabalho, sem
   borda, sombra, blur nem animação, e nunca pegam o foco), o atalho de pânico e, se quiser, a abertura ao
   entrar na sessão. O Hyprland relê a config quando você salva.
3. Abra com `/caminho/do/pestinha/.venv/bin/python /caminho/do/pestinha/main.py` (ou saia e entre de novo
   na sessão, com a abertura automática). Na primeira vez aparecem as boas-vindas e as permissões.

**Hyprland 0.55 ou mais novo, config em Lua** (`~/.config/hypr/hyprland.lua`). Conferido com
`Hyprland --verify-config` no 0.57:

```lua
hl.window_rule({
    name  = "pestinha-janelas",
    match = { class = "^pestinha$", title = "^pestinha:janela(:.*)?$" },
    float = true, pin = true, no_focus = true, no_initial_focus = true,
    border_size = 0, rounding = 0, no_shadow = true, no_blur = true, no_anim = true, no_dim = true,
})
hl.bind("CTRL + ALT + SHIFT + B", hl.dsp.exec_cmd("python3 /caminho/do/pestinha/ferramentas/pestinha_ctl.py panico"))
-- abre o pet ao entrar na sessão (opcional)
hl.on("hyprland.start", function()
    hl.exec_cmd("/caminho/do/pestinha/.venv/bin/python /caminho/do/pestinha/main.py")
end)
```

**Hyprland 0.53 a 0.56, `hyprland.conf`** (sintaxe da wiki do Hyprland 0.54; não testada aqui, porque o 0.57
só lê Lua):

```ini
windowrule {
    name = pestinha-janelas
    match:class = ^pestinha$
    match:title = ^pestinha:janela(:.*)?$
    float = on
    pin = on
    no_focus = on
    no_initial_focus = on
    border_size = 0
    rounding = 0
    no_shadow = on
    no_blur = on
    no_anim = on
    no_dim = on
}
bind = CTRL ALT SHIFT, B, exec, python3 /caminho/do/pestinha/ferramentas/pestinha_ctl.py panico
# abre o pet ao entrar na sessão (opcional)
exec-once = /caminho/do/pestinha/.venv/bin/python /caminho/do/pestinha/main.py
```

Antes do 0.53, as regras de janela tinham outra sintaxe (`windowrulev2`); os efeitos são os mesmos e o pet
ainda funciona, mas a regra precisa ser adaptada.

Sem o atalho na config, o pet avisa ao abrir. Depois de um pânico, ele volta com
`python3 /caminho/do/pestinha/ferramentas/pestinha_ctl.py religar`; `pestinha_ctl.py -h` lista os outros
comandos (status, permissões, configurações, pausar, esconder, sair). No [Ryoku](https://github.com/Andersonk01/ryoku)
(branch `anderson`), nada disso é preciso: a regra, o atalho e a abertura já vêm prontos, e o pet se liga
e configura em Hub > Desktop > Pestinha.

Como funciona: no Wayland, um programa não pode posicionar as próprias janelas e os comandos do X11 não
enxergam as outras, então o Pestinha usa um backend próprio (`pestinha/plataforma/hyprland.py`):

- As janelas do pet rodam pelo **XWayland**, onde podem andar pela tela. Os títulos delas começam com
  `pestinha:janela` (`pestinha:janela:notebook`...), para as regras de janela do Hyprland as acharem; o
  notebook é posto na frente do pet pelo próprio Hyprland, porque o raise do X11 não muda a ordem lá.
- Janelas, janela ativa, tela cheia, cursor e a área livre das barras vêm do **socket do Hyprland** (o mesmo
  do `hyprctl`). O título das outras janelas vem junto e é descartado, como no X11.
- **Vários monitores:** o Hyprland (do 0.56 em diante) traduz a posição de cada janela do XWayland pelo
  monitor dela, o que tinha o foco quando ela abriu. Para todas as janelinhas do pet usarem a mesma conta,
  ele pede ao Hyprland (`hyprctl eval`, só no config em Lua) uma regra que as abre no primeiro monitor da
  lista, sem mudar o foco; a regra é renovada a cada 10 s, porque recarregar a config a apaga. Assim ele
  vê os monitores onde eles estão e passa de um para o outro pela borda que os une. No `hyprland.conf`,
  sem essa regra, ele pode sumir ao passar para o outro monitor (o log avisa).
- O tempo ocioso vem do protocolo **ext-idle-notify** do Wayland, que só diz "parou" e "voltou".
- O Hyprland não deixa um programa ouvir o teclado dos outros (o pynput não funciona lá): o pânico é um bind
  do próprio Hyprland que chama o **controle local**, um socket em `$XDG_RUNTIME_DIR/pestinha.sock`
  que só o seu usuário alcança. O `ferramentas/pestinha_ctl.py` fala com ele (status, perms, panico,
  religar, configuracoes, pausar, esconder, sair).
- `PESTINHA_PLATAFORMA=x11` volta ao backend do X11; `PESTINHA_QPA=wayland` tira o XWayland (o pet não anda).

`python main.py --pet jorge` troca o personagem antes de abrir.

### Como interagir

| Gesto | Efeito |
|---|---|
| Clique rápido | Cutucada |
| Passar o mouse de um lado para o outro em cima dele | Carinho |
| Segurar e arrastar / soltar rápido | Leva junto / arremessa |
| Rodinha do mouse | Gira |
| Botão direito | Menu: cutucar, carinho, bolinha, dormir, travessura, trabalhar, notebook, cantinho do castigo, painéis, configurações, esconder, fechar |

### Pânico

`Ctrl + Alt + Shift + B` desliga tudo na hora, e ele continua desligado até você religar em
Configurações (no Hyprland, com `ferramentas/pestinha_ctl.py religar` ou pelo Hub do Ryoku).

### Modo teste

Desligado por padrão. Ligado, os tempos ficam curtos (emoções, travessuras e protesto acontecem em
segundos), os painéis de desenvolvimento ficam na tela (monitor neural e painel de protesto) e o
terminal mostra as decisões.

## Privacidade

Ele roda só no seu computador e não envia nada para a internet. Lê o **nome** do programa em primeiro
plano, o tempo sem usar teclado e mouse, a posição do cursor e a geometria das janelas. **Nunca** lê
conteúdo nem título de janela. Tudo o que ele grava fica na pasta de dados e pode ser apagado pela tela de
configurações: `memory/`, rodando pelo código, ou `%LOCALAPPDATA%\Pestinha`, no executável do Windows.
Detalhes em [PRIVACIDADE.md](PRIVACIDADE.md).

## Idioma

O pet fala o idioma do sistema: português num sistema em português, inglês em qualquer outro. Vale para as
telas, a bandeja, o menu, os avisos, o comando `ferramentas/pestinha_ctl.py` e o que ele põe na tela
(recadinhos, cartazes, plaquinhas). Para escolher na mão, abra com `PESTINHA_IDIOMA=pt` ou `PESTINHA_IDIOMA=en`.

- Os textos do programa são escritos em português e traduzidos em `pestinha/idioma_en.py`.
- As frases de cada personagem têm a versão em inglês ao lado da original (`recadinhos.en.txt`,
  `cartazes.en.txt`...), explicada em [pets/README.md](pets/README.md).
- Os memes têm o texto dentro da imagem e continuam em português. Uma pasta `memes.en/` no personagem vale
  no lugar deles; sem ela, ficam os originais (ou desligue os memes em Configurações).
- PRIVACIDADE.md e a documentação só existem em português.

## Personalizar

- **Memes, recadinhos e cartazes do Bryan:** pasta `pets/bryan/`, explicada em [pets/README.md](pets/README.md).
  Pode editar com ele aberto.
- **Bolinhas, notebook, sons e suas fotos:** `assets/comum/`, valem para qualquer personagem
  ([assets/LEIA-ME.txt](assets/LEIA-ME.txt)). Um personagem pode ter os próprios (o Cypher tem notebook e
  voz próprios em `pets/cypher/`).
- **Forma, cores, acessórios e efeitos:** o campo `aparencia` do `pets/<pet>.json` (o monitorzinho ou a bola
  de pelo do Bolota; capuz, headset, óculos, gravata; chuva de código, scanlines, glitch), explicado em
  [pets/README.md](pets/README.md).
- **Programas que ele reconhece:** `assets/comum/programas.json` soma programas à lista de trabalho, jogo, música etc.
- **Personalidade:** `pets/<pet>.json` (descrição, semente da rede, temperamento, pesos de brincadeira, reação ao
  notebook).
- **Números do comportamento:** `pestinha/ajustes.py`, todos validados ao abrir.

## Estrutura

| Pasta | O que tem |
|---|---|
| `pestinha/` | O código, em camadas ([pestinha/README.md](pestinha/README.md)) |
| `assets/comum/` | Imagens da bolinha e do notebook, e suas fotos: valem para qualquer pet |
| `pets/` | Cada pet: `<pet>.json` (quem ele é) e `<pet>/` (frases, cartazes e memes dele) |
| `tests/` | Testes automáticos |
| `ferramentas/fuzz_pestinha.py` | Fuzzer: roda ações aleatórias e checa invariantes |
| `ferramentas/` | Geradores de documentação |
| `docs/` | Arquitetura, rede neural e relatórios ([docs/README.md](docs/README.md)) |
| `memory/` | Gerada em uso, com o que ele aprende. Não vai para o repositório |

## Documentação

- [docs/ARQUITETURA.md](docs/ARQUITETURA.md): como as partes conversam.
- [docs/REDE_NEURAL.md](docs/REDE_NEURAL.md): canais, interneurônios, motores e decisões da rede.
- [pestinha/README.md](pestinha/README.md) e o README de cada pasta: o que cada arquivo faz.
- [CONTRIBUTING.md](CONTRIBUTING.md): como rodar os testes e contribuir.
- [CHANGELOG.md](CHANGELOG.md): o que mudou.

## Desenvolvimento

```bash
pip install -r requirements-dev.txt
```
```bash
python -m pytest -q
```

Os testes rodam sem abrir janelas (Qt em modo offscreen). Mais detalhes em [CONTRIBUTING.md](CONTRIBUTING.md).

### Gerar o executável

Há duas formas: gerar no seu computador (só o sistema em que você está) ou deixar o GitHub gerar os três.
O PyInstaller só gera o executável do sistema onde roda, por isso um Windows não gera o de Mac.

#### Opção 1: no seu computador

1. Instale as dependências de desenvolvimento (inclui o PyInstaller):

   ```bash
   pip install -r requirements-dev.txt
   ```

2. Gere o executável, no Windows:

   ```bash
   python -m PyInstaller --noconfirm --onefile --windowed --name Pestinha --distpath build/onefile --workpath build/work --specpath build --hidden-import win32timezone main.py
   ```

   No macOS e no Linux, use o mesmo comando sem `--windowed` e sem `--hidden-import win32timezone`.

3. O resultado fica em `build/onefile/` (`Pestinha.exe` no Windows, `Pestinha` nos outros).

4. Monte a pasta de entrega: copie o executável e as pastas `assets/` e `pets/` para uma mesma pasta.
   O programa lê o conteúdo dessas pastas ao lado do executável. No Windows, a memória fica em
   `%LOCALAPPDATA%\Pestinha`, a menos que já exista uma pasta `memory/` ao lado dele. Nos outros sistemas, a
   `memory/` é criada sozinha na primeira execução, então não copie a sua.

5. Opcional, no Windows: gere o instalador com o [Inno Setup 6](https://jrsoftware.org/isinfo.php). Ele usa o
   executável do passo 3, instala só para o usuário atual e não pede administrador:

   ```bash
   ISCC instalador/pestinha.iss
   ```

   O resultado fica em `instalador/saida/`.

#### Opção 2: pelo GitHub (os três sistemas de uma vez)

O workflow `.github/workflows/executaveis.yml` gera Windows, macOS e Linux em máquinas do próprio GitHub.

1. Suba o repositório para o GitHub (`git push`).
2. Para gerar sem criar versão: na aba **Actions**, escolha **executáveis**, clique em **Run workflow**.
3. Para gerar e publicar uma versão: crie uma tag e envie. Por exemplo:

   ```bash
   git tag v0.8.0
   git push origin v0.8.0
   ```

4. Ao terminar (alguns minutos), a execução tem três artefatos, um por sistema, com a pasta pronta
   (executável + `assets/` + `pets/`). Baixe pela própria página da execução, na seção **Artifacts**.

Para distribuir para quem não é do projeto, publique esses artefatos na aba **Releases** (use "Draft a new release"
na tag criada), e não dentro do repositório: cada executável tem cerca de 60 MB.

#### Depois de gerar

- Para testar sem misturar com a sua memória, crie uma pasta `memory/` vazia ao lado do executável de teste.
- O executável não é assinado: o Windows e o macOS avisam na primeira execução. No macOS, a permissão de
  Acessibilidade é necessária para o atalho Ctrl+Alt+Shift+B; no Linux, o atalho e as janelas precisam de
  `xdotool`, `wmctrl` e `xprintidle`.

## Licença

O código do Pestinha é software livre, sob a [GNU General Public License v3.0 ou posterior](LICENSE)
(GPL-3.0-or-later). Você pode usar, estudar, modificar e redistribuir, mas toda versão distribuída,
modificada ou não, precisa continuar aberta e sob a mesma licença.

As imagens e os textos de `assets/` não estão cobertos por esta licença

## Limitações conhecidas

- macOS e Linux ainda não foram testados numa máquina real: a parte de leitura das janelas e do teclado foi
  escrita e testada só nas partes de texto (ver `tests/test_plataforma.py`).
- No macOS, o pet precisa da permissão de Acessibilidade para o atalho Ctrl+Alt+Shift+B funcionar.
- No Linux com Wayland fora do Hyprland, o pet não enxerga janelas nem o tempo ocioso, e o atalho global
  não funciona.
- No Hyprland, vários monitores foram conferidos no 0.57 (config em Lua), com escala 1. Com escala acima de 1
  e `force_zero_scaling`, o pet usa a escala do primeiro monitor também nos outros (fica do mesmo tamanho
  em pixels nos dois). No `hyprland.conf` (0.56 ou mais antigo), com mais de um monitor, ele pode sumir
  ao passar de um para o outro.
- Pouco testado com escala de tela acima de 100% e com vários monitores. A tela cheia num monitor esconde o
  pet em todos.
- Jogos em janela sem borda podem não ser detectados como tela cheia.
- O executável não é assinado; o Windows pode avisar na primeira execução.
