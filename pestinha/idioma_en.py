"""
IDIOMA EM INGLÊS - a tradução de cada texto do pet: a chave é o texto em português, como está no código.

Os {campos} da tradução são os mesmos do original. tests/test_idioma.py falha se um texto marcado com
tr() ou N_() não estiver aqui, se um {campo} mudar ou se uma tradução não for mais usada.
"""

TEXTOS = {
    # config.py
    'FELIZ':
        'HAPPY',
    'CONTENTE':
        'CONTENT',
    'OBSERVANDO':
        'WATCHING',
    'CURIOSO':
        'CURIOUS',
    'BRAVO':
        'ANGRY',
    'TRISTE':
        'SAD',
    'ASSUSTADO':
        'SCARED',
    'DRAMÁTICO':
        'DRAMATIC',
    'DORMINDO':
        'SLEEPING',
    'Original do personagem':
        "Character's own",
    'Rosa':
        'Pink',
    'Cyber':
        'Cyber',
    'Matrix':
        'Matrix',
    'Âmbar':
        'Amber',
    'Baixo':
        'Low',
    'Médio':
        'Medium',
    'Alto':
        'High',
    'Travessuras':
        'Mischief',
    'Interruptor geral: sem ele, nada de memes, fotos ou bilhetes.':
        'Main switch: without it, no memes, photos or notes.',
    'Trazer memes':
        'Bring memes',
    'Imagens de pets/<pet>/memes/<emoção>/.':
        'Images from pets/<pet>/memes/<emotion>/.',
    'Trazer fotos':
        'Bring photos',
    'Imagens de assets/comum/fotos/.':
        'Images from assets/comum/fotos/.',
    'Deixar bilhetes':
        'Leave notes',
    'Post-its com frases de pets/<pet>/recadinhos.txt.':
        'Sticky notes with lines from pets/<pet>/recadinhos.txt.',
    'Interação':
        'Interaction',
    'Cutucar':
        'Poke',
    'Clicar nele é uma cutucada, e ele reage.':
        'Clicking him is a poke, and he reacts.',
    'Carinho e aprendizado':
        'Petting and learning',
    'Passar o mouse para lá e para cá em cima dele é carinho. Ele aprende a gostar do que estava acontecendo quando ganhou carinho (e a desgostar de ser dispensado).':
        'Moving the mouse back and forth over him is petting. He learns to like what was going on when he was petted (and to dislike being dismissed).',
    'Arrastar e arremessar':
        'Drag and throw',
    'Segurar, girar com a rodinha e jogar longe.':
        'Hold him, spin him with the wheel and throw him far.',
    'Pousar em janelas':
        'Land on windows',
    'Solto no ar, ele pode cair em cima da barra de título.':
        'Dropped in the air, he can land on a title bar.',
    'Contexto':
        'Context',
    'Aparecer em tela cheia (experimental)':
        'Show over fullscreen (experimental)',
    'Por padrão ele some em jogos, vídeos e apresentações.':
        'By default he hides during games, videos and presentations.',
    'Rotina':
        'Routine',
    'Registrar minha rotina':
        'Record my routine',
    'Grava 1 linha por minuto em timeline.csv, na pasta de dados: hora, categoria de atividade, trocas de programa, ocioso. Nunca títulos, sites ou conteúdo. O pet ainda não usa esse histórico.':
        'Writes 1 line per minute to timeline.csv, in the data folder: time, activity category, program switches, idle. Never titles, sites or content. The pet does not use this history yet.',
    'Brincadeira':
        'Play',
    'Fogos de artifício':
        'Fireworks',
    'Quando ele fica muito feliz, a alegria da rede pode soltar um fogo.':
        "When he is very happy, the network's joy may set off a firework.",
    'Bolinha':
        'Ball',
    'Uma bolinha para ele brincar. Se você levar para longe, ele reage (pode ficar triste, bravo ou ir atrás).':
        'A ball for him to play with. If you take it away, he reacts (he may get sad, angry or go after it).',
    'Notebook':
        'Notebook',
    'Ele senta no notebook dele para trabalhar quando você programa. Desligado, o notebook some e ele não senta.':
        'He sits at his notebook to work while you code. Off, the notebook goes away and he does not sit.',
    'Sons':
        'Sounds',
    'Bipes quando você cutuca, faz carinho, ele se assusta, bate, fica bravo ou triste. Sem nada gravado: os sons são sintetizados (assets/comum/sons/).':
        'Beeps when you poke or pet him, when he gets scared, hits something, gets angry or sad. Nothing is recorded: the sounds are synthesized (assets/comum/sons/).',
    'Digitação no notebook':
        'Typing at the notebook',
    'Enquanto ele trabalha sentado no notebook, dá para ouvir ele digitando, de vez em quando.':
        'While he works at his notebook, you can hear him typing now and then.',
    'Teste':
        'Test',
    'Modo teste':
        'Test mode',
    'Tempos curtos: travessuras e emoções acontecem em segundos.':
        'Short timings: mischief and emotions happen in seconds.',
    'Mostrar nome da emoção':
        "Show the emotion's name",
    'Texto pequeno embaixo dele (só no modo teste).':
        'Small text under him (test mode only).',
    # ui/ui.py
    'Bem-vindo! O {app} vê só o nome dos programas, o tempo sem usar o teclado e as janelas para pousar. Nunca lê o conteúdo de nada. Detalhes em PRIVACIDADE.md.\nEscolha abaixo o que ele pode fazer e clique em Começar. Tudo pode ser mudado depois.':
        'Welcome! {app} only sees program names, how long the keyboard has been idle and the windows to land on. It never reads the content of anything. Details in PRIVACIDADE.md (in Portuguese).\nChoose below what he may do and click Start. Everything can be changed later.',
    'Escolha o que o pet pode fazer nesta sessão. Fica salvo para a próxima.':
        'Choose what the pet may do in this session. It is saved for the next one.',
    '{app} ligado':
        '{app} on',
    'Abrir o {app} ao entrar no {sistema}':
        'Open {app} when you log in to {sistema}',
    'O pânico desligou o {app} na última vez. Marque acima para religar.':
        'Panic turned {app} off last time. Tick the box above to turn it back on.',
    'Personagem:':
        'Character:',
    'Vale na próxima vez que abrir. Cada personagem tem a própria memória.':
        'Takes effect the next time it opens. Each character has its own memory.',
    'Estilo:':
        'Style:',
    'As cores dele (e os efeitos da tela). Vale na hora.':
        'His colours (and the screen effects). Applies at once.',
    'Volume:':
        'Volume:',
    'Apagar histórico':
        'Delete history',
    'Apagar todos os dados do {app}':
        'Delete all {app} data',
    'Pasta de dados: {pasta}':
        'Data folder: {pasta}',
    'Pânico (desliga tudo e fica desligado): {atalho}':
        'Panic (turns everything off and keeps it off): {atalho}',
    'Sair':
        'Quit',
    'Começar':
        'Start',
    'Fechar':
        'Close',
    'Conteúdo de {nome}: {memes} memes de emoção, {trabalho} de trabalho, {fotos} fotos, {recados} recadinhos e {tristes} bilhetes tristes.':
        "{nome}'s content: {memes} emotion memes, {trabalho} work memes, {fotos} photos, {recados} sticky notes and {tristes} sad notes.",
    'Histórico: {minutos} minutos ({horas:.1f} h) gravados.':
        'History: {minutos} minutes ({horas:.1f} h) recorded.',
    'Apagar todo o histórico da sua rotina ({arquivo})? Não dá para desfazer.':
        'Delete the whole history of your routine ({arquivo})? This cannot be undone.',
    'Não deu para apagar: {erro}':
        'Could not delete: {erro}',
    'Apagar todos os dados':
        'Delete all data',
    'Apagar tudo que o {app} guardou ({pasta}: a memória de todos os personagens, histórico, painéis, permissões)? O {app} vai fechar e deixa de abrir sozinho com o sistema. Não dá para desfazer.':
        'Delete everything {app} has kept ({pasta}: the memory of every character, history, panels, permissions)? {app} will close and stop opening with the system. This cannot be undone.',
    'O sistema não permitiu mudar essa opção.':
        'The system did not allow changing this option.',
    'Configurações...':
        'Settings...',
    'Monitor neural':
        'Neural monitor',
    'Painel de protesto':
        'Protest panel',
    'Esconder painéis de teste':
        'Hide test panels',
    'Pausar':
        'Pause',
    'Esconder':
        'Hide',
    'Limpar travessuras':
        'Clear mischief',
    'Pânico ({atalho})':
        'Panic ({atalho})',
    'Continuar':
        'Resume',
    'Mostrar':
        'Show',
    '  [MODO TESTE]':
        '  [TEST MODE]',
    # ui/rotulos.py
    'movimento':
        'motion',
    'digitação':
        'typing',
    'novidade':
        'novelty',
    'silêncio':
        'silence',
    'trabalho':
        'work',
    'jogo':
        'game',
    'música':
        'music',
    'social':
        'social',
    'navegador':
        'browser',
    'cansaço':
        'tiredness',
    'cutucada':
        'poke',
    'arraste':
        'drag',
    'dispensa':
        'dismissal',
    'solidão':
        'loneliness',
    'carinho':
        'petting',
    'arremesso':
        'throw',
    'batida':
        'impact',
    'antecipação':
        'anticipation',
    'bolinha perto':
        'ball nearby',
    'bolinha levada':
        'ball taken',
    'tédio':
        'boredom',
    'pedido de trabalho':
        'work request',
    'preso no canto':
        'stuck in the corner',
    'lembra de fugas':
        'remembers escapes',
    'recusou pedido':
        'refused a request',
    'placa do castigo':
        'time-out sign',
    'antecipa o canto':
        'anticipates the corner',
    'visita no canto':
        'corner visit',
    'receio de fugir':
        'afraid to escape',
    'rancor':
        'grudge',
    'alerta':
        'alert',
    'foco':
        'focus',
    'curiosidade':
        'curiosity',
    'brincadeira':
        'playfulness',
    'calma':
        'calm',
    'quietude':
        'quiet',
    'inibição':
        'inhibition',
    'frustração':
        'frustration',
    'desânimo':
        'gloom',
    'susto':
        'startle',
    'observar':
        'watch',
    'passear':
        'wander',
    'alegria':
        'cheer',
    'sossego':
        'settle',
    'sonolência':
        'drowsiness',
    'raiva':
        'anger',
    'tristeza':
        'sadness',
    'sentar no notebook':
        'sit at the notebook',
    'fugir do canto':
        'escape the corner',
    'colar cartaz':
        'put up a sign',
    'ir para o cantinho':
        'go to the corner',
    'aprontar':
        'get up to mischief',
    'atirar papel':
        'throw paper',
    'aceitar o castigo':
        'accept the time-out',
    'sentido':
        'sense',
    'interneurônio':
        'interneuron',
    'motor':
        'motor',
    # ui/monitor.py
    'velocidade, passeios':
        'speed, strolls',
    'fixa o cursor':
        'stares at the cursor',
    'pulinhos, giros':
        'hops, spins',
    'pulo de susto':
        'startled jump',
    'lentidão, pálpebras':
        'slowness, eyelids',
    'tremor':
        'shaking',
    'menos exploração':
        'less exploring',
    'balanço':
        'swaying',
    '{nome} · Monitor neural':
        '{nome} · Neural monitor',
    'Disparos · últimos 3 s · 1 coluna = 10 ms':
        'Spikes · last 3 s · 1 column = 10 ms',
    'agora':
        'now',
    'Entrada (azul) · eficácia sináptica / habituação (laranja)':
        'Input (blue) · synaptic efficacy / habituation (orange)',
    'Motores → o que controlam no corpo':
        'Motors → what they drive in the body',
    'velocidade {v:3.0f} px/s · pulinho {pulo:.0%} · altura {altura:3.0f} · tremor {tremor:.1f} px':
        'speed {v:3.0f} px/s · hop {pulo:.0%} · height {altura:3.0f} · shake {tremor:.1f} px',
    'balanço {balanco:.1f}° · pálpebra +{palpebra:.2f} · fixa cursor {olhar:.0%} · sobe janela {sobe:.0%}':
        'sway {balanco:.1f}° · eyelid +{palpebra:.2f} · cursor stare {olhar:.0%} · window climb {sobe:.0%}',
    'Estado':
        'State',
    'valência {valencia:+.2f} · ativação {ativacao:+.2f}':
        'valence {valencia:+.2f} · arousal {ativacao:+.2f}',
    'energia':
        'energy',
    'estimulação':
        'stimulation',
    'carência':
        'need for contact',
    'insatisfação {insatisfacao:.2f} · protesto: {estagio} · revoluções {revolucoes}':
        'grievance {insatisfacao:.2f} · protest: {estagio} · revolutions {revolucoes}',
    'última cutucada: resposta {resposta} · eficácia da cutucada {eficacia:.2f}':
        'last poke: response {resposta} · poke efficacy {eficacia:.2f}',
    '   · DORMINDO':
        '   · SLEEPING',
    # core/protesto.py
    'em paz':
        'at peace',
    'reclamação':
        'complaint',
    'manifestação':
        'demonstration',
    'greve':
        'strike',
    'revolução':
        'revolution',
    'ei.':
        'hey.',
    'reclamação formal':
        'formal complaint',
    'MAIS CARINHO':
        'MORE PETTING',
    'MENOS CLIQUES':
        'FEWER CLICKS',
    'EM GREVE':
        'ON STRIKE',
    'SEM CARINHO, SEM TRABALHO':
        'NO PETS, NO WORK',
    'CHEGA!':
        'ENOUGH!',
    'ISSO NÃO É JUSTO.':
        'THIS IS NOT FAIR.',
    'EU SÓ QUERIA BRINCAR.':
        'I JUST WANTED TO PLAY.',
    'ACORDO FECHADO':
        'DEAL CLOSED',
    '...tá. passou.':
        "...fine. it's over.",
    'alô?':
        'hello?',
    'tem alguém aí?':
        'anyone there?',
    'tô chorando :(':
        "i'm crying :(",
    'me visita?':
        'visit me?',
    'não vou sair daqui':
        "i'm not leaving",
    'VOLTEI!':
        "I'M BACK!",
    'saudade de você':
        'missed you',
    # ui/panel.py
    'não está subindo':
        'not rising',
    '{nome} · Painel de protesto':
        '{nome} · Protest panel',
    'PAINEL DE PROTESTO':
        'PROTEST PANEL',
    'revoluções: {n}':
        'revolutions: {n}',
    'até a greve':
        'until the strike',
    'greve ativa':
        'strike on',
    'tempo estimado com a raiva atual: {tempo}':
        'estimated time at the current anger: {tempo}',
    'raiva da rede {raiva:.2f}  ·  insatisfação {insatisfacao:.2f}  ·  sobe com dispensas, arremessos e batidas; cai com carinho e com o tempo.':
        'network anger {raiva:.2f}  ·  grievance {insatisfacao:.2f}  ·  rises with dismissals, throws and hits; falls with petting and with time.',
    # ui/onboarding.py
    'Este é um projeto em desenvolvimento. Algumas coisas podem não funcionar direito, ainda há bugs a corrigir e o comportamento pode mudar bastante entre versões. Obrigado por testar!':
        'This is a project in development. Some things may not work right, there are still bugs to fix and the behaviour may change a lot between versions. Thanks for testing!',
    'Projeto em desenvolvimento':
        'Project in development',
    'Oi, eu sou o {nome}':
        "Hi, I'm {nome}",
    'Sou uma telinha com dois olhinhos que mora no seu monitor principal. Eu caio, quico, pouso nas janelas, fico tristinho, brinco com a bolinha e, às vezes, apronto com post-its e memes.\n\nVocê pode me cutucar, me dar carinho, me jogar e abrir meu menu com o botão direito.':
        "I'm a little screen with two eyes who lives on your main monitor. I fall, bounce, land on windows, get a bit sad, play with the ball and, now and then, get up to mischief with sticky notes and memes.\n\nYou can poke me, pet me, throw me and open my menu with the right button.",
    'O que eu vejo (e o que não vejo)':
        "What I see (and what I don't)",
    'Eu vejo o nome do programa em primeiro plano, o tempo sem usar o teclado ou o mouse, e a posição das janelas para pousar nelas.\n\nNunca leio o conteúdo de nenhuma janela, página, documento ou conversa. Os detalhes estão em PRIVACIDADE.md.':
        'I see the name of the program in front, how long the keyboard and mouse have been idle, and where the windows are so I can land on them.\n\nI never read the content of any window, page, document or conversation. The details are in PRIVACIDADE.md (in Portuguese).',
    'Agora você escolhe':
        'Now you choose',
    'Na próxima tela você decide o que eu posso fazer: travessuras, bolinha, carinho e mais. Tudo pode ser mudado depois, pelo menu da bandeja ou pelo botão direito em mim.\n\nAtalho de pânico: Ctrl + Alt + Shift + B desliga tudo na hora.':
        'On the next screen you decide what I may do: mischief, the ball, petting and more. Everything can be changed later, from the tray menu or by right-clicking me.\n\nPanic shortcut: Ctrl + Alt + Shift + B turns everything off at once.',
    '{app} · primeira vez':
        '{app} · first time',
    'Pular':
        'Skip',
    'Voltar':
        'Back',
    'Próximo':
        'Next',
    '{atual} de {total}':
        '{atual} of {total}',
    # controle/interacao.py
    'Dar carinho':
        'Pet him',
    'Jogar a bolinha perto dele':
        'Toss the ball near him',
    'Guardar a bolinha':
        'Put the ball away',
    'Pedir para dormir':
        'Ask him to sleep',
    'Pedir para trabalhar':
        'Ask him to work',
    'Mostrar o notebook':
        'Show the notebook',
    'Esconder o notebook':
        'Hide the notebook',
    'Fazer uma travessura agora':
        'Do some mischief now',
    'Cantinho do castigo':
        'Time-out corner',
    'Esconder (volta pela bandeja)':
        'Hide (comes back from the tray)',
    # app.py
    'A memória ainda está no formato antigo (migração pendente: {resumo}). Nada foi apagado; veja memory/logs.':
        'The memory is still in the old format (migration pending: {resumo}). Nothing was deleted; see memory/logs.',
    'sem permissão para gravar em {pasta}: o que ele aprender será perdido ao fechar':
        'no permission to write to {pasta}: what he learns will be lost on quit',
    'atalho de pânico {atalho} já está em uso por outro programa':
        'the panic shortcut {atalho} is already used by another program',
    'Estou aqui. Pânico: {atalho}':
        "I'm here. Panic: {atalho}",
    # plataforma/hyprland.py
    'o Hyprland não tem o atalho de pânico: adicione um bind de {teclas} que rode `ferramentas/pestinha_ctl.py panico`':
        'Hyprland has no panic shortcut: add a {teclas} bind that runs `ferramentas/pestinha_ctl.py panico`',
    # controle/sessao.py
    'Pânico: {app} desligado. Religue em Configurações.':
        'Panic: {app} is off. Turn it back on in Settings.',
    'Não foi possível apagar tudo':
        'Could not delete everything',
    'Alguns dados continuam em {pasta}. O programa vai fechar; feche o que possa estar usando esses arquivos e tente de novo.\n\nArquivos que falharam:\n{lista}':
        'Some data is still in {pasta}. The program will close; close anything that may be using those files and try again.\n\nFiles that failed:\n{lista}',
    # config.py (avisos)
    'sem corpo.png em {pasta}: o pelo é desenhado por código':
        'no corpo.png in {pasta}: the fur is drawn by code',
    'sem pasta memes/ em {pasta} nem em assets/comum/: sem memes':
        'no memes/ folder in {pasta} or in assets/comum/: no memes',
    'a pasta {pasta} está vazia: sem memes':
        'the folder {pasta} is empty: no memes',
    'sem recadinhos.txt em {pasta}: sem post-its':
        'no recadinhos.txt in {pasta}: no sticky notes',
    'sem cartazes.txt em {pasta}: usando frases neutras':
        'no cartazes.txt in {pasta}: using neutral signs',
    # mind/castigo_ctl.py
    'CANTINHO\nDO CASTIGO':
        'TIME-OUT\nCORNER',
    # world/notebook.py
    'Notebook do {nome}':
        "{nome}'s notebook",
    # world/objetos.py
    'clique para fechar':
        'click to close',
    # controle/remoto.py
    'o pedido precisa ser um objeto JSON':
        'the request must be a JSON object',
    "faltou 'valores'":
        "missing 'valores'",
    'comando desconhecido: {comando!r}':
        'unknown command: {comando!r}',
    'o pedido não é JSON':
        'the request is not JSON',
    # main.py
    'pula a tela de permissões':
        'skips the permission screen',
    'mostra a tela de permissões':
        'shows the permission screen',
    'fecha sozinho após N segundos (teste)':
        'quits by itself after N seconds (test)',
    'personagem (o id em pets/, ex.: bryan ou jorge)':
        'character (the id in pets/, e.g. bryan or jorge)',
    'O {app} já está aberto. Procure o ícone na bandeja.':
        '{app} is already open. Look for its icon in the tray.',
    '\n\nArquivos que falharam: {lista}':
        '\n\nFiles that failed: {lista}',
    'Alguns dados continuam em {pasta}. Feche programas que possam estar usando esses arquivos e tente novamente.{detalhe}':
        'Some data is still in {pasta}. Close any program that may be using those files and try again.{detalhe}',
    # ferramentas/pestinha_ctl.py
    'Fala com o Pestinha que está rodando, pelo controle local.\n\n    pestinha_ctl.py status                    estado e permissões (JSON)\n    pestinha_ctl.py perms bolinha=off fogos=on muda permissões (as da tela de configurações)\n    pestinha_ctl.py perms estilo=rosa volume=baixo   as escolhas também (o pet confere as opções)\n    pestinha_ctl.py panico                    o mesmo que Ctrl+Alt+Shift+B\n    pestinha_ctl.py religar                   liga de novo depois do pânico\n    pestinha_ctl.py configuracoes             abre a tela de configurações\n    pestinha_ctl.py pausar | esconder         alterna\n    pestinha_ctl.py sair                      salva e fecha\n\nSaída: a resposta em JSON. Código de saída 0 se deu certo, 1 se o pet não está rodando, 2 se o pedido\nfoi recusado.':
        'Talks to the running Pestinha through its local control socket.\n\n    pestinha_ctl.py status                    state and permissions (JSON)\n    pestinha_ctl.py perms bolinha=off fogos=on changes permissions (the ones in the Settings window)\n    pestinha_ctl.py perms estilo=rosa volume=baixo   the choices too (the pet checks the options)\n    pestinha_ctl.py panico                    the same as Ctrl+Alt+Shift+B\n    pestinha_ctl.py religar                   turns it back on after a panic\n    pestinha_ctl.py configuracoes             opens the Settings window\n    pestinha_ctl.py pausar | esconder         toggles pause | hide\n    pestinha_ctl.py sair                      saves and quits\n\nOutput: the answer as JSON. Exit code 0 when it worked, 1 when the pet is not running, 2 when the\nrequest was refused.',
    'faltou o comando':
        'missing command',
    '{comando} não recebe argumentos':
        '{comando} takes no arguments',
    'use chave=valor: {item!r}':
        'use key=value: {item!r}',
    'opção inválida para {chave}: {valor!r}':
        'invalid option for {chave}: {valor!r}',
    'valor de {chave} precisa ser on/off: {valor!r}':
        '{chave} must be on or off: {valor!r}',
    'perms precisa de pelo menos um chave=valor':
        'perms needs at least one key=value',
    'resposta inválida':
        'invalid answer',
}
