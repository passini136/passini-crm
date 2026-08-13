"""
Conteúdo do assistente: tutorial guiado, FAQ e biblioteca de dicas.

Arquivo separado do motor, como o mec_feedback.py. Texto de ajuda envelhece
rápido — cada tela nova pede um ajuste aqui — e mudar uma frase não deveria
exigir mexer no backend. Editar e reiniciar o serviço já vale.

O admin também cria conteúdo pela tela; o que está aqui é a base que já nasce
pronta, para o sistema não estrear vazio.
"""

# ─────────────────────────────────────────────────────────────────────────────
# Tutorial de primeiro acesso
#
# Um roteiro por perfil. Cada passo aponta para uma tela real e responde três
# coisas: o que é, por que importa e o que fazer nos primeiros dias. Texto curto
# de propósito — tutorial que exige leitura longa é pulado.
# ─────────────────────────────────────────────────────────────────────────────

TOUR_VENDEDOR = [
    {
        "tab": None,
        "icon": "👋",
        "title": "Bem-vindo ao CRM da Passini",
        "body": "Este sistema existe para uma coisa: te mostrar quem contatar hoje e por quê. "
                "Ele não substitui o seu jeito de vender — organiza o que você já faz para "
                "nenhuma oportunidade se perder no caminho.",
        "hint": "São 8 telas. Leva 3 minutos.",
    },
    {
        "tab": "crm-agenda",
        "icon": "📅",
        "title": "Missão do Dia — comece sempre por aqui",
        "body": "Todo dia o sistema monta sua fila: 5 contatos prioritários, com 2 clientes "
                "Bronze/Prata, 2 Ouro/Diamante e 1 de prospecção. Cada card já diz o motivo do "
                "contato e o que oferecer. Quem você contatou sai da fila e só volta depois que "
                "a carteira inteira girar — assim você não fica orbitando os mesmos nomes.",
        "hint": "Regra do MEC: abra o CRM, faça a primeira tarefa da fila, registre e marque o próximo passo.",
    },
    {
        "tab": "crm-clientes",
        "icon": "👥",
        "title": "Carteira — e a coluna de sinais",
        "body": "Seus clientes separados por situação: ativo, espaçando pedidos, parado. Na coluna "
                "Sinais, quatro marcas contam a história de cada um num relance — bolinha verde é "
                "contato ativo nos últimos 30 dias, cinza é contato antigo, losango é visita, seta "
                "é retorno pendente e círculo vermelho vazio é cliente que nunca foi tocado.",
        "hint": "Passe o mouse em cada marca para ver a data. Os vermelhos são onde há dinheiro parado.",
    },
    {
        "tab": "crm-interacao",
        "icon": "📝",
        "title": "Registrar contato — o que faz tudo funcionar",
        "body": "Depois de cada ligação, registre o que aconteceu de verdade: com quem falou, o "
                "que o cliente precisa, o que ficou combinado. Registro fraco é 'falei com o "
                "cliente'. Registro válido diz nome, necessidade, horário e próximo passo.",
        "hint": "Contato sem registro não conta. E é o registro que faz o cliente sair da sua fila.",
    },
    {
        "tab": "crm-clientes",
        "icon": "📌",
        "title": "Registro receptivo — quando o cliente procura você",
        "body": "Ligação que você recebeu, WhatsApp que chegou, informação que vale guardar: na "
                "ficha do cliente, o botão Registro receptivo grava isso no histórico. Ele NÃO "
                "conta na sua meta de ligações, e é proposital — a meta mede o que você foi "
                "buscar, não o que chegou sozinho.",
        "hint": "Use sem medo: o histórico completo do cliente vale mais do que um número inflado.",
    },
    {
        "tab": "contatos",
        "icon": "📇",
        "title": "Contatos — seu histórico e seu ritmo",
        "body": "Tudo que você registrou, com filtro de período, tipo e resultado. No topo, quatro "
                "números: ligações ativas contra o esperado ATÉ HOJE (não contra os 60 do mês "
                "fechado), quanto você conseguiu falar de fato, quanto virou orçamento ou pedido "
                "e com quantos clientes diferentes você falou.",
        "hint": "Muita ligação com pouca conversa é sinal de horário errado, não de falta de esforço.",
    },
    {
        "tab": "crm-tarefas",
        "icon": "✅",
        "title": "Tarefas — nada fica só na memória",
        "body": "Todo retorno que você marca vira tarefa com data. Aqui também chegam as cobranças "
                "do gerente, as ações combinadas nas visitas e o aviso quando um colega atendeu um "
                "cliente da sua carteira.",
        "hint": "Comece o dia resolvendo o que está atrasado, antes de pegar a fila nova.",
    },
    {
        "tab": "prospeccao",
        "icon": "🌱",
        "title": "Prospecção — o quinto contato do dia",
        "body": "Uma oficina nova por dia. Cadastre a oficina aqui mesmo, sem esperar o cadastro do "
                "Alfa: quatro perguntas revelam o potencial e três gatilhos fecham. Quando ela "
                "vira cliente, o histórico da prospecção vai junto para a ficha.",
        "hint": "Sem um dos 3 gatilhos no fim, a prospecção não conta como válida no funil.",
    },
    {
        "tab": "biblioteca",
        "icon": "📚",
        "title": "Biblioteca, Visitas e Meu Placar",
        "body": "Na Biblioteca estão mensagens de WhatsApp, abordagens e respostas a objeções. Em "
                "Visitas você pede ao gerente para visitar um cliente — precisa de ligação "
                "registrada antes. No Meu Placar acompanha pontos e premiação.",
        "hint": "Atendeu cliente de outro vendedor? Busque pelo código na Carteira: dá para ver a ficha e registrar.",
    },
]

TOUR_GERENTE = [
    {
        "tab": None,
        "icon": "👋",
        "title": "Bem-vindo ao CRM da Passini",
        "body": "Como gerente, você tem duas frentes aqui: acompanhar o resultado da unidade e "
                "desenvolver a equipe. O sistema te dá os números e o método — a condução é sua.",
        "hint": "São 9 telas. Leva 4 minutos.",
    },
    {
        "tab": "executivo",
        "icon": "📊",
        "title": "Executivo — o painel da sua unidade",
        "body": "Faturamento contra meta, margem, devolução, desconto e ticket. Os faróis mostram "
                "o que está no ritmo e o que precisa de atenção, comparando com o esperado para o "
                "dia do mês — não com o mês fechado.",
        "hint": "Ao entrar, o sistema já abre na sua unidade. Você pode trocar para comparar.",
    },
    {
        "tab": "vendedores",
        "icon": "👤",
        "title": "Vendedores — quem precisa de você esta semana",
        "body": "Ranking da equipe com meta, ticket, mix, devolução e cobertura de carteira. "
                "Serve para escolher onde investir seu tempo, não para expor ninguém.",
        "hint": "Compare cada vendedor com a média da unidade antes de tirar conclusão.",
    },
    {
        "tab": "contatos",
        "icon": "📇",
        "title": "Contatos — produtividade por vendedor",
        "body": "O histórico de todos os registros da equipe, com quatro indicadores por vendedor: "
                "ligações no ritmo da meta, taxa de conversa efetiva, conversão em orçamento ou "
                "pedido e quantos clientes distintos ele tocou. Esse último denuncia quem liga "
                "sempre para os mesmos.",
        "hint": "Ligação alta com conversa baixa é problema de lista ou horário. Cobre a causa, não o número.",
    },
    {
        "tab": "crm-agenda",
        "icon": "📣",
        "title": "Missão do Dia e cobrança de contato",
        "body": "Você vê o que a equipe tem para fazer hoje e o que ficou atrasado. Na ficha de "
                "qualquer cliente, o botão Cobrar contato cria a tarefa para o vendedor "
                "responsável — com motivo e prazo.",
        "hint": "Cobrança com motivo escrito funciona. 'Liga nesse cliente' não.",
    },
    {
        "tab": "crm-clientes",
        "icon": "🤝",
        "title": "Cobertura de carteira — férias e ausências",
        "body": "Na Carteira você autoriza um vendedor a enxergar a carteira de outro, com data de "
                "início e fim. Para ele, aparecem dois botões no topo: a carteira dele e a que "
                "está cobrindo — nunca misturadas. Fora do período, o acesso fecha sozinho.",
        "hint": "Sempre defina a data final. Sem prazo, a cobertura não expira.",
    },
    {
        "tab": "visitas",
        "icon": "🗺️",
        "title": "Visitas — o roteiro sai pronto",
        "body": "O sistema sugere quem visitar, agrupado por bairro e rua para você não cruzar a "
                "cidade duas vezes. Só entra cliente que já recebeu ligação do vendedor. "
                "Dá para imprimir o roteiro ou mandar no WhatsApp.",
        "hint": "Depois da visita, registre o que ficou combinado — vira tarefa do vendedor.",
    },
    {
        "tab": "reunioes",
        "icon": "🗓️",
        "title": "Reuniões — ata com ciência da equipe",
        "body": "Registre a reunião ou o treinamento, marque os presentes e publique. Cada um dá "
                "ciência e pode responder. Fica o histórico do que foi combinado, com anexo.",
        "hint": "Rascunho só você vê. A equipe só é avisada quando você publica.",
    },
    {
        "tab": "feedback",
        "icon": "🎯",
        "title": "Feedback e PDI — o rito mensal",
        "body": "Uma vez por mês, com cada vendedor. A tela já abre com os números dele e um guia "
                "do que perguntar e combinar. Entre um feedback e outro, use o Registro rápido "
                "para anotar o que acontece no dia a dia.",
        "hint": "No máximo 2 pontos no PDI. Plano com cinco frentes não sai do lugar.",
    },
]

TOUR_DIRETOR = [
    {
        "tab": None,
        "icon": "👋",
        "title": "Bem-vindo ao CRM da Passini",
        "body": "Você enxerga a empresa inteira: todas as unidades, todas as equipes e todos os "
                "registros. Este roteiro mostra onde estão as respostas que a diretoria costuma "
                "procurar.",
        "hint": "São 8 telas. Leva 4 minutos.",
    },
    {
        "tab": "executivo",
        "icon": "📊",
        "title": "Executivo — o consolidado e o detalhe",
        "body": "Resultado da empresa com abertura por unidade, vendedor e cidade. Faturamento "
                "líquido já separa devolução comercial de devolução em garantia, que não entra no "
                "resultado do vendedor.",
        "hint": "Os faróis comparam com o ritmo esperado para o dia do mês, não com o mês fechado.",
    },
    {
        "tab": "unidades",
        "icon": "🏢",
        "title": "Unidades — comparação justa entre praças",
        "body": "Cada unidade contra a própria meta, com margem, desconto e devolução lado a lado. "
                "Unidade em implantação aparece marcada e fica isenta de meta até a competência "
                "que você definir — assim ela não polui a comparação nem pinta tudo de vermelho.",
        "hint": "Desconto alto com meta batida costuma esconder margem sendo queimada.",
    },
    {
        "tab": "administracao",
        "icon": "🗺️",
        "title": "Territórios — de quem é cada bairro",
        "body": "Porto Alegre tem duas unidades, então a cidade sozinha não diz mais de quem é o "
                "cliente. Em Administração → Territórios você define a divisão por bairro. Isso "
                "decide a prospecção, o roteiro de visita e o território na ficha — o faturamento "
                "continua contando para a unidade do vendedor que vendeu.",
        "hint": "O painel 'bairros sem dono' mostra onde há cliente e ninguém responde pelo território.",
    },
    {
        "tab": "contatos",
        "icon": "📇",
        "title": "Contatos — a execução comercial da empresa",
        "body": "Todos os registros, de todas as unidades, com os indicadores por vendedor. É onde "
                "se vê se a rotina do MEC está acontecendo de verdade ou se o número de vendas "
                "está vindo de outra coisa.",
        "hint": "Compare a taxa de conversa efetiva entre unidades: costuma revelar diferença de método.",
    },
    {
        "tab": "feedback",
        "icon": "🎯",
        "title": "Feedback de gerente — direcionamento tático",
        "body": "O feedback Diretor × Gerente usa a estrutura GROW: objetivo, realidade, caminhos "
                "e compromisso. Os indicadores incluem os ritos: quantos feedbacks o gerente fez, "
                "reuniões registradas e PDIs vencidos.",
        "hint": "Só a diretoria conduz esse feedback. Gerente não avalia gerente.",
    },
    {
        "tab": "acessos",
        "icon": "🔑",
        "title": "Usuários e Perfis — quem vê o quê",
        "body": "Cada perfil define as telas e o alcance dos dados. O campo Pessoa vinculada liga a "
                "conta ao nome do cadastro e vale para TODOS os perfis — é por ele que o gerente "
                "recebe ciência de ata e feedback. A busca é obrigatória: digitar à mão quebra o "
                "vínculo em silêncio.",
        "hint": "Vendedor precisa também da unidade, que é gravada no cadastro de pessoas.",
    },
    {
        "tab": "importacoes",
        "icon": "📥",
        "title": "Importações — de onde vêm os números",
        "body": "Faturamento, custo, cadastro de clientes e devoluções entram por aqui. Atenção ao "
                "cadastro de clientes: o Alfa exporta em DOIS arquivos e a importação substitui a "
                "base inteira. Mandar um só apaga o outro — os dois têm de estar na pasta juntos.",
        "hint": "Depois de importar, confira a cobertura: abaixo de 85% o sistema avisa que faltou arquivo.",
    },
]

# Versão do roteiro. Entra na chave que marca "já vi o tutorial", então subir
# este número faz o tour aparecer UMA vez para quem já tinha visto o anterior.
# Suba quando a mudança for grande o bastante para valer a interrupção — foi o
# caso da v2, que acrescentou Contatos, sinais na carteira, registro receptivo,
# rodízio da fila, territórios e cobertura de carteira.
TOUR_VERSION = "v2"

TOURS = {
    "VENDEDOR": TOUR_VENDEDOR,
    "GERENTE": TOUR_GERENTE,
    "DIRETOR": TOUR_DIRETOR,
}


# ─────────────────────────────────────────────────────────────────────────────
# FAQ
#
# `keywords` é o que a busca usa. Escreva como a pessoa perguntaria, não como o
# sistema chama a coisa: alguém digita "não achei meu cliente", não "filtro de
# carteira". `roles` vazio = vale para todos.
# ─────────────────────────────────────────────────────────────────────────────

FAQ_CATEGORIES = [
    {"id": "primeiros-passos", "label": "Primeiros passos", "icon": "🚀"},
    {"id": "dia-a-dia", "label": "Dia a dia", "icon": "📅"},
    {"id": "clientes", "label": "Clientes e carteira", "icon": "👥"},
    {"id": "gestao", "label": "Gestão de equipe", "icon": "🎯"},
    {"id": "numeros", "label": "Números e indicadores", "icon": "📊"},
    {"id": "problemas", "label": "Quando algo dá errado", "icon": "🔧"},
]

FAQ_SEED = [
    # ── Telas e regras criadas depois da primeira versão ────────────────
    {
        "category": "dia-a-dia",
        "question": "Contatei o cliente e ele sumiu da Missão do Dia. Está certo?",
        "answer": "Está. Quem você contatou entra em descanso e só volta depois que a carteira "
                  "prioritária girar inteira — a janela é calculada pelo tamanho da sua carteira "
                  "no ritmo de 5 contatos por dia. É o que impede a fila de ficar orbitando os "
                  "mesmos nomes. Quando todos já rodaram, o ciclo recomeça pelos mais antigos e "
                  "a tela avisa.",
        "keywords": "sumiu da fila cliente saiu missao do dia nao aparece mais contatado descanso rodizio",
        "roles": "",
    },
    {
        "category": "dia-a-dia",
        "question": "O cliente me ligou. Como registro sem inflar minha meta?",
        "answer": "Na ficha do cliente, use o botão Registro receptivo. Ele grava ligação "
                  "recebida, mensagem recebida ou anotação no histórico, mas fica FORA da meta de "
                  "ligações ativas. A meta mede o que você foi buscar; o que chega sozinho conta "
                  "como histórico, não como esforço de prospecção.",
        "keywords": "cliente ligou recebi ligacao whatsapp mensagem anotacao registro receptivo nao conta meta",
        "roles": "",
    },
    {
        "category": "clientes",
        "question": "O que significam as bolinhas na coluna Sinais da carteira?",
        "answer": "São quatro marcas: bolinha verde = contato ativo nos últimos 30 dias; bolinha "
                  "cinza = último contato ativo mais antigo que isso; losango = visita registrada; "
                  "seta = retorno pendente. Círculo vermelho vazio é o mais importante: cliente que "
                  "nunca recebeu nenhum registro nem visita. Passe o mouse para ver a data.",
        "keywords": "bolinha sinal marca coluna sinais circulo vermelho losango seta o que significa",
        "roles": "",
    },
    {
        "category": "dia-a-dia",
        "question": "Preciso atender um cliente que não é da minha carteira. Como faço?",
        "answer": "Na Carteira, busque pelo CÓDIGO do cliente — o próprio cliente informa. A ficha "
                  "abre completa, com histórico e vendas, e você registra o atendimento "
                  "normalmente. O registro entra como apoio: não conta na sua meta de ligações, "
                  "mas fica no histórico, o gerente enxerga e o vendedor responsável recebe uma "
                  "tarefa para retomar o contato.",
        "keywords": "cliente de outro vendedor nao e da minha carteira atender colega ferias apoio codigo",
        "roles": "VENDEDOR",
    },
    {
        "category": "dia-a-dia",
        "question": "Apareceram dois botões de carteira no topo da tela. O que é isso?",
        "answer": "É cobertura: o gerente autorizou você a enxergar a carteira de um colega por um "
                  "período, normalmente férias. Um botão mostra a sua carteira e o outro a que você "
                  "está cobrindo — nunca as duas juntas. Terminado o prazo, o acesso fecha sozinho "
                  "e os botões somem.",
        "keywords": "dois botoes carteira cobertura ferias carteira do colega apareceu outro nome",
        "roles": "VENDEDOR",
    },
    {
        "category": "gestao",
        "question": "Como libero um vendedor para cobrir a carteira de outro nas férias?",
        "answer": "Na Carteira, no painel Cobertura de carteira, clique em Autorizar: escolha quem "
                  "cobre, qual carteira e o período. Sempre defina a data final — sem prazo a "
                  "cobertura não expira sozinha. O vendedor passa a ver a carteira do colega em uma "
                  "aba separada, sem misturar com a dele.",
        "keywords": "ferias cobertura liberar carteira outro vendedor autorizar substituto ausencia",
        "roles": "GERENTE DIRETOR",
    },
    {
        "category": "numeros",
        "question": "O que é 'ligações no ritmo' na tela Contatos?",
        "answer": "É a comparação com o esperado ATÉ HOJE, não com a meta fechada do mês. O piso do "
                  "MEC é 60 ligações no mês; no dia 6 de um mês de 22 dias úteis, o esperado é 16, "
                  "não 60. Cobrar o número cheio no começo do mês marcaria todo mundo como "
                  "irregular e o painel perderia a credibilidade.",
        "keywords": "ligacoes no ritmo meta 60 esperado ate hoje barra colorida contatos indicador",
        "roles": "",
    },
    {
        "category": "numeros",
        "question": "Um vendedor tem muita ligação e pouca conversa. O que isso indica?",
        "answer": "A taxa de conversa efetiva separa esforço de resultado. Volume alto com conversa "
                  "baixa costuma ser lista ruim, telefone desatualizado ou horário errado — não "
                  "falta de trabalho. Antes de cobrar mais ligação, olhe a qualidade da lista e o "
                  "horário em que ele liga.",
        "keywords": "conversa efetiva taxa baixa muita ligacao pouco resultado nao atende qualidade",
        "roles": "GERENTE DIRETOR",
    },
    {
        "category": "clientes",
        "question": "O cliente aparece no faturamento mas não na carteira, e diz 'sem cadastro'.",
        "answer": "O nome do relatório de vendas não casou com o cadastro. O sistema tenta três "
                  "caminhos: nome exato, documento embutido no nome e razão social sem o sufixo "
                  "(LTDA, ME, EPP). Falhando os três, use o botão Conciliar na tela Sem Vendedor e "
                  "informe o código do cliente. Se muitos clientes estiverem assim, o provável é "
                  "que falte um dos dois arquivos do cadastro na última importação.",
        "keywords": "sem cadastro nao achei o cliente conciliar codigo nome diferente faturamento carteira",
        "roles": "GERENTE DIRETOR",
    },
    {
        "category": "numeros",
        "question": "De qual unidade é um cliente?",
        "answer": "Vale a unidade do VENDEDOR que atende — é a mesma regra do faturamento, para a "
                  "venda e a carteira não contarem em lugares diferentes. Quando o cliente não tem "
                  "vendedor, vale o território: primeiro o bairro, depois a cidade. Cidade "
                  "compartilhada entre duas unidades fica sem mapa de propósito, e aí quem manda é "
                  "quem já atende.",
        "keywords": "unidade do cliente porque esta em outra unidade zona norte zona sul territorio bairro",
        "roles": "",
    },
    # ── Primeiros passos ────────────────────────────────────────────────
    {
        "category": "primeiros-passos",
        "question": "Como começo o meu dia no CRM?",
        "answer": "Abra a Missão do Dia. Primeiro resolva o que está atrasado em Tarefas, depois "
                  "siga a fila dos 5 contatos prioritários. Depois de cada contato, registre o que "
                  "aconteceu e marque o próximo passo. É o ciclo do MEC: abrir, preparar, fazer, "
                  "registrar, marcar, concluir.",
        "keywords": "começar dia rotina primeira tarefa fila missão do dia por onde começo",
        "roles": "VENDEDOR",
    },
    {
        "category": "primeiros-passos",
        "question": "Esqueci minha senha. E agora?",
        "answer": "O sistema não envia senha por e-mail. Fale com o administrador — ele redefine "
                  "a sua senha em Usuários e Perfis.",
        "keywords": "senha esqueci login não entro acesso bloqueado trocar senha",
        "roles": "",
    },
    {
        "category": "primeiros-passos",
        "question": "Posso rever o tutorial de primeiro acesso?",
        "answer": "Sim. Abra o assistente no canto da tela e clique em Rever tutorial. Ele mostra "
                  "o roteiro do seu perfil quantas vezes você quiser.",
        "keywords": "tutorial rever treinamento inicial passo a passo apresentação",
        "roles": "",
    },

    # ── Dia a dia ───────────────────────────────────────────────────────
    {
        "category": "dia-a-dia",
        "question": "Registrei o contato mas o cliente continua na minha fila. Por quê?",
        "answer": "O cliente sai da fila assim que a interação é salva e só volta depois que a "
                  "carteira girar. Se continuar aparecendo, confira três coisas: se você clicou em "
                  "Salvar, se registrou no cliente certo e se não usou o Registro receptivo — o "
                  "receptivo grava o histórico mas não tira o cliente da fila, porque quem procurou "
                  "foi ele, não você.",
        "keywords": "cliente não sai da fila top 5 continua aparecendo registrei mas não sumiu",
        "roles": "VENDEDOR",
    },
    {
        "category": "dia-a-dia",
        "question": "O que é um registro válido?",
        "answer": "Precisa responder quatro coisas: com quem você falou, o que o cliente precisa, "
                  "o que aconteceu e o que será feito depois. 'Falei com o cliente' não é registro. "
                  "'Falei com o João, das compras, às 10h. Precisa de freio até 14h. Prefere marca "
                  "A, aceita equivalente. Retorno marcado para 14h10' é registro.",
        "keywords": "registro válido observação como registrar anotar contato o que escrever",
        "roles": "",
    },
    {
        "category": "dia-a-dia",
        "question": "Como agendo um retorno para um cliente?",
        "answer": "Na ficha do cliente, use Agendar contato. Escolha a data (tem atalhos de "
                  "amanhã, 3, 7 e 15 dias), o horário e o motivo. Vira tarefa sua, com prazo. "
                  "Ao registrar um contato com resultado 'pediu retorno', o sistema também cria a "
                  "tarefa automaticamente.",
        "keywords": "agendar retorno lembrete ligar depois marcar contato futuro",
        "roles": "VENDEDOR",
    },
    {
        "category": "dia-a-dia",
        "question": "Como peço uma visita do gerente?",
        "answer": "Só é possível depois de registrar uma ligação para aquele cliente nos últimos "
                  "30 dias — o telefone vem antes da rua. Com a ligação registrada, marque 'Pedir "
                  "visita do gerente' no formulário de contato ou use o botão na ficha do cliente. "
                  "Escreva o motivo: é o que o gerente lê para montar a rota da semana.",
        "keywords": "pedir visita gerente solicitar visita cliente difícil não atende",
        "roles": "VENDEDOR",
    },

    {
        "category": "dia-a-dia",
        "question": "Como faço uma prospecção do jeito da Passini?",
        "answer": "São quatro perguntas: se ele compra mais manutenção rápida ou corretiva pesada; "
                  "quantos carros atende por semana; se gira mais suspensão, freio ou motor; e se "
                  "compra à vista, cartão ou faturado. Com isso você estima o potencial e escolhe "
                  "o mix certo. No fim, feche com um dos três gatilhos. O roteiro completo está na "
                  "Biblioteca, aba Prospecção.",
        "keywords": "prospecção prospectar cliente novo primeira ligação abordagem 4 perguntas",
        "roles": "",
    },
    {
        "category": "dia-a-dia",
        "question": "Quais são os 3 gatilhos de fechamento da prospecção?",
        "answer": "1) 'Posso te atender no próximo orçamento e te mostrar nosso atendimento?' "
                  "2) 'Posso te incluir nas próximas cotações dessa linha?' "
                  "3) 'Qual dia da semana você costuma comprar para eu te chamar?' "
                  "Sem um deles, a prospecção não entra como válida no funil — vira só uma conversa.",
        "keywords": "gatilho fechamento prospecção como fechar encerrar ligação cliente novo funil",
        "roles": "",
    },
    {
        "category": "dia-a-dia",
        "question": "Que dados preciso para cadastrar um cliente novo?",
        "answer": "Para pagamento à vista, PIX ou cartão, só três: CNPJ, telefone e e-mail — envie "
                  "para crédito e cobrança pelo Skype. Para compra faturada no boleto, preencha a "
                  "ficha para o cliente, mande só para ele assinar e ele envia direto ao setor, "
                  "que analisa e pede mais dados se precisar.",
        "keywords": "cadastro cliente novo dados cnpj ficha crédito boleto faturado abrir cliente",
        "roles": "",
    },

    # ── Clientes e carteira ─────────────────────────────────────────────
    {
        "category": "dia-a-dia",
        "question": "Minha unidade é nova e não tem meta. Como sou avaliado?",
        "answer": "Enquanto a unidade está em implantação, o painel não cobra meta de faturamento — "
                  "os indicadores aparecem como 'em implantação'. O que vale são as metas de "
                  "atividade: ligações, oficinas novas cadastradas, cadastros concluídos e "
                  "primeiras compras. Elas ficam na tela de Prospecção.",
        "keywords": "unidade nova sem meta implantação como sou avaliado zona norte inauguração",
        "roles": "",
    },
    {
        "category": "dia-a-dia",
        "question": "Como registro uma oficina que ainda não é cliente?",
        "answer": "Na tela de Prospecção, use Nova oficina. Anote pelo menos o nome, o telefone e "
                  "o CNPJ — o CNPJ é o que permite o sistema reconhecer sozinho quando ela for "
                  "cadastrada no Alfa e levar seu histórico de ligações para a ficha do cliente. "
                  "Depois é só registrar o contato como você faria com qualquer cliente.",
        "keywords": "prospect oficina nova sem cadastro cliente novo registrar contato prospecção cnpj",
        "roles": "",
    },
    {
        "category": "clientes",
        "question": "O que significa cliente ativo, pré-inativo e inativo?",
        "answer": "É calculado pelos dias sem compra. Ativo compra dentro do prazo esperado; "
                  "pré-inativo está espaçando os pedidos e é o momento de agir; inativo parou. "
                  "Recuperar um pré-inativo custa muito menos do que recuperar um inativo.",
        "keywords": "ativo inativo pré-inativo status cliente classificação parou de comprar",
        "roles": "",
    },
    {
        "category": "clientes",
        "question": "Como encontro quem compra uma peça específica?",
        "answer": "Na Carteira existe o campo de busca por item. Digite o código do fabricante ou "
                  "o código interno e o sistema mostra quem comprou nos últimos 12 meses, com a "
                  "data da última compra, quantidade e o preço praticado.",
        "keywords": "buscar peça item gtin código quem comprou produto específico",
        "roles": "",
    },
    {
        "category": "clientes",
        "question": "As sugestões de oferta na ficha do cliente são confiáveis?",
        "answer": "Elas usam o histórico real. Recompra é item que o cliente comprava e parou — o "
                  "gancho mais forte. Oportunidade é item que outras oficinas da mesma praça "
                  "compram e ele nunca pediu. O sistema confere o histórico inteiro antes de "
                  "chamar um item de novidade.",
        "keywords": "sugestão oferta recompra oportunidade o que oferecer item sugerido",
        "roles": "",
    },
    {
        "category": "clientes",
        "question": "Por que o mesmo cliente aparece com dois códigos?",
        "answer": "É cadastro duplicado no Alfa. A ficha avisa quando detecta, mostrando em qual "
                  "código o faturamento está contabilizado. Vale unificar os cadastros na origem — "
                  "enquanto existirem dois, o histórico fica dividido.",
        "keywords": "cliente duplicado dois códigos cadastro repetido mesmo cliente",
        "roles": "",
    },

    # ── Gestão de equipe ────────────────────────────────────────────────
    {
        "category": "gestao",
        "question": "Com que frequência devo dar feedback?",
        "answer": "Uma vez por mês, depois de fechar o mês, com cada vendedor. Entre um feedback e "
                  "outro, use o Registro rápido para anotar o que acontece no dia a dia — quando "
                  "chegar a conversa mensal, os registros aparecem na tela e você não escreve de "
                  "memória.",
        "keywords": "feedback frequência quando dar mensal periodicidade avaliação",
        "roles": "GERENTE DIRETOR",
    },
    {
        "category": "gestao",
        "question": "Por que meu vendedor não recebeu a ata da reunião?",
        "answer": "Duas causas possíveis. A ata pode estar como rascunho — só o autor vê rascunho, "
                  "a equipe só é avisada quando você publica. Ou a conta dele não está ligada ao "
                  "nome do cadastro: em Usuários e Perfis, preencha o campo Pessoa vinculada com "
                  "exatamente o nome que aparece na lista de presença.",
        "keywords": "ata não apareceu vendedor não recebeu reunião ciência não chegou",
        "roles": "GERENTE DIRETOR",
    },
    {
        "category": "gestao",
        "question": "Como funciona o roteiro de visitas?",
        "answer": "O sistema sugere clientes com queda, inativos ou pedidos pelo vendedor, "
                  "agrupados por cidade, bairro e rua. Só entra quem recebeu ligação registrada nos "
                  "últimos 30 dias, e quem foi visitado há menos de 60 dias fica de fora. Dá para "
                  "imprimir em PDF ou copiar para o WhatsApp.",
        "keywords": "roteiro visita como funciona sugestão rota bairro imprimir",
        "roles": "GERENTE DIRETOR",
    },
    {
        "category": "gestao",
        "question": "Como sei se a visita deu resultado?",
        "answer": "O sistema compara o faturamento do cliente nos 60 dias antes e nos 60 dias "
                  "depois da visita, sozinho. O resultado aparece na lista de visitas e na ficha do "
                  "cliente. Enquanto a janela não fecha, mostra 'efeito em apuração' — número "
                  "parcial daria a impressão errada.",
        "keywords": "visita resultado efeito adiantou funcionou medir retorno",
        "roles": "GERENTE DIRETOR",
    },
    {
        "category": "gestao",
        "question": "Posso criar tarefa para a equipe toda?",
        "answer": "Sim, em Tarefas, botão Nova tarefa. Cliente é opcional — dá para direcionar algo "
                  "como 'revisar os orçamentos do dia e levantar os motivos de desistência'. "
                  "Escolhendo várias pessoas, cada uma recebe a sua tarefa e conclui "
                  "separadamente: tarefa coletiva não é de ninguém.",
        "keywords": "tarefa equipe criar direcionamento atribuir todos vendedores",
        "roles": "GERENTE DIRETOR",
    },

    # ── Números ─────────────────────────────────────────────────────────
    {
        "category": "numeros",
        "question": "Como o farol decide a cor?",
        "answer": "Ele compara com o ritmo esperado para o dia do mês, não com o mês fechado. "
                  "No dia 3 de 21, esperar 100% da meta pintaria tudo de vermelho e a equipe "
                  "aprenderia a ignorar o alerta. Toda cor vem com ícone e texto, para quem não "
                  "distingue vermelho de verde também entender.",
        "keywords": "farol cor verde amarelo vermelho indicador como calcula ritmo",
        "roles": "",
    },
    {
        "category": "numeros",
        "question": "Devolução em garantia entra no meu resultado?",
        "answer": "Não. A devolução em garantia é separada da devolução comercial e não é "
                  "descontada do resultado do vendedor nem da unidade. O faturamento líquido que "
                  "aparece já considera essa separação.",
        "keywords": "devolução garantia desconta resultado comercial líquido",
        "roles": "",
    },
    {
        "category": "numeros",
        "question": "De onde vem a média de faturamento do cliente?",
        "answer": "É a soma dos 3 meses anteriores dividida por 3 — sempre por 3, mesmo que o "
                  "cliente tenha comprado em apenas um deles. A ficha mostra a memória do cálculo, "
                  "mês a mês, para você conferir o número.",
        "keywords": "média faturamento cliente cálculo trimestre como calcula",
        "roles": "",
    },

    # ── Problemas ───────────────────────────────────────────────────────
    {
        "category": "problemas",
        "question": "O botão de copiar mensagem não funciona.",
        "answer": "O sistema roda em HTTP na rede interna, e o navegador bloqueia a área de "
                  "transferência nesse caso. Quando isso acontece, abre uma janela com o texto "
                  "selecionado para você copiar na mão com Ctrl+C.",
        "keywords": "copiar não funciona botão copiar erro clipboard mensagem whatsapp",
        "roles": "",
    },
    {
        "category": "problemas",
        "question": "A tela está desatualizada depois de uma mudança.",
        "answer": "Atualize com Ctrl+Shift+R. Isso força o navegador a baixar a versão nova em vez "
                  "de usar a que ele guardou.",
        "keywords": "tela antiga desatualizada não atualizou cache versão nova",
        "roles": "",
    },
    {
        "category": "problemas",
        "question": "Não consigo acessar o CRM de fora da Passini.",
        "answer": "O acesso externo é pela VPN Tailscale. Com ela ligada, use o endereço interno do "
                  "servidor. Sem VPN, o sistema só responde dentro da rede da empresa.",
        "keywords": "acesso remoto fora casa vpn tailscale não abre externo",
        "roles": "",
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# Biblioteca de dicas do assistente
#
# `kind` separa o uso:
#   MENSAGEM   — mensagem do dia, tom de abertura
#   MEC        — execução do método
#   DESEMPENHO — como melhorar um número
#   LEMBRETE   — rotina e prazos
#
# `trigger` liga a dica a uma situação real. Quando preenchido, a dica só
# aparece para quem está naquela situação — dica genérica vira paisagem.
# ─────────────────────────────────────────────────────────────────────────────

TIP_KINDS = [
    {"id": "MENSAGEM", "label": "Mensagem do dia", "icon": "💬"},
    {"id": "MEC", "label": "Execução do MEC", "icon": "🎯"},
    {"id": "DESEMPENHO", "label": "Melhorar resultado", "icon": "📈"},
    {"id": "LEMBRETE", "label": "Lembrete", "icon": "⏰"},
]

TIPS_SEED = [
    # ── Mensagem do dia ─────────────────────────────────────────────────
    {"kind": "MENSAGEM", "roles": "", "trigger": "",
     "title": "O dia começa pela fila",
     "body": "Quem escolhe o que fazer trabalha o que gosta. Quem segue a fila trabalha o que "
             "precisa. A diferença aparece no dia 30."},
    {"kind": "MENSAGEM", "roles": "", "trigger": "",
     "title": "Vender é consequência",
     "body": "Ninguém controla se o cliente compra hoje. Todo mundo controla quantas ligações fez, "
             "quantos orçamentos retornou e quantos registros deixou completos."},
    {"kind": "MENSAGEM", "roles": "", "trigger": "",
     "title": "O cliente lembra de quem voltou",
     "body": "A maior parte das vendas perdidas não foi para o concorrente mais barato. Foi para "
             "quem retornou a ligação no horário combinado."},
    {"kind": "MENSAGEM", "roles": "", "trigger": "",
     "title": "Peça pequena, conta grande",
     "body": "O cliente que compra R$ 80 por semana vale mais no ano que o pedido de R$ 2.000 que "
             "aparece uma vez. Frequência é o que sustenta a carteira."},

    # ── Execução do MEC ─────────────────────────────────────────────────
    {"kind": "MEC", "roles": "VENDEDOR", "trigger": "",
     "title": "Prepare antes de ligar",
     "body": "Trinta segundos olhando a ficha mudam a conversa: veja o motivo do contato, o que ele "
             "comprava e parou, e escolha uma oferta. Ligar sem proposta é desperdício."},
    {"kind": "MEC", "roles": "VENDEDOR", "trigger": "",
     "title": "Orçamento enviado não é orçamento terminado",
     "body": "Ligue em até 10 minutos para confirmar o recebimento e pergunte: 'o que falta para "
             "fecharmos esse pedido agora?'. É a pergunta que separa cotação de venda."},
    {"kind": "MEC", "roles": "VENDEDOR", "trigger": "",
     "title": "Toda conversa termina com data",
     "body": "'Depois eu vejo' não é próximo passo. Combine dia e horário antes de desligar, e "
             "registre — atendimento sem próxima ação continua aberto."},
    {"kind": "MEC", "roles": "VENDEDOR", "trigger": "",
     "title": "O quinto contato é cliente novo",
     "body": "Prospecção não é o que sobra do dia. É um dos cinco. Uma empresa nova por dia são "
             "vinte por mês na sua carteira."},
    {"kind": "MEC", "roles": "VENDEDOR", "trigger": "",
     "title": "Quatro perguntas antes de oferecer",
     "body": "Manutenção rápida ou corretiva pesada? Quantos carros por semana? Suspensão, freio "
             "ou motor? À vista, cartão ou faturado? Com essas respostas você para de fazer "
             "abordagem rasa e passa a oferecer o que a oficina realmente gira."},
    {"kind": "MEC", "roles": "VENDEDOR", "trigger": "",
     "title": "Prospecção sem gatilho não conta",
     "body": "Termine sempre com um dos três: participar do próximo orçamento, entrar nas cotações "
             "da linha, ou saber o dia da semana em que ele compra. Conversa boa que acaba sem "
             "compromisso não é prospecção — é ligação perdida."},
    {"kind": "MEC", "roles": "VENDEDOR", "trigger": "",
     "title": "Não deixe a venda travar no cadastro",
     "body": "À vista, PIX ou cartão: CNPJ, telefone e e-mail resolvem e você fatura hoje. "
             "Faturado: preencha a ficha para o cliente e mande só para assinar — ficha em branco "
             "quase nunca volta."},
    {"kind": "MEC", "roles": "GERENTE DIRETOR", "trigger": "",
     "title": "Cobrança precisa de motivo",
     "body": "'Liga nesse cliente' não muda comportamento. 'Este cliente caiu 60% e você não fala "
             "com ele há 40 dias' muda. Escreva o motivo na cobrança."},

    # ── Desempenho ──────────────────────────────────────────────────────
    {"kind": "DESEMPENHO", "roles": "VENDEDOR", "trigger": "CALLS_LOW",
     "title": "Suas ligações estão abaixo do mínimo",
     "body": "O MEC pede 3 por dia e 60 no mês. Abaixo disso, o resto do funil não tem "
             "matéria-prima e nenhuma outra correção funciona. Reserve um bloco fixo na agenda, "
             "no mesmo horário todo dia."},
    {"kind": "DESEMPENHO", "roles": "VENDEDOR", "trigger": "GOAL_LOW",
     "title": "Meta fora do ritmo — escolha uma alavanca",
     "body": "Volume de ligação, retorno de orçamento ou recuperação de inativo. Escolha UMA para "
             "este mês e defina o número. Três frentes ao mesmo tempo não sai do lugar."},
    {"kind": "DESEMPENHO", "roles": "VENDEDOR", "trigger": "INACTIVE_HIGH",
     "title": "Sua carteira tem muito cliente parado",
     "body": "Cliente inativo é venda que já foi conquistada e está sendo perdida — custa menos "
             "recuperar do que prospectar. Faça uma lista dos 10 maiores e descubra o motivo real "
             "de cada um."},
    {"kind": "DESEMPENHO", "roles": "VENDEDOR", "trigger": "TICKET_LOW",
     "title": "Ticket abaixo da unidade",
     "body": "Ticket baixo costuma ser venda de item único: atende o pedido e não oferece o "
             "complemento. Use a sugestão de recompra que já aparece na ficha — uma oferta por "
             "atendimento."},
    {"kind": "DESEMPENHO", "roles": "VENDEDOR", "trigger": "RETURNS_HIGH",
     "title": "Devolução acima do aceitável",
     "body": "Quase sempre é erro de aplicação ou pressa para fechar. Confirme veículo, motor e ano "
             "antes de faturar peça de linha crítica. Perder a venda custa menos que devolver."},
    {"kind": "DESEMPENHO", "roles": "GERENTE", "trigger": "FEEDBACK_PENDING",
     "title": "Feedbacks do mês em aberto",
     "body": "Ainda falta gente da sua equipe sem feedback neste mês. O acompanhamento mensal é o "
             "rito que sustenta o resto — sem ele, a correção só acontece quando o problema já "
             "custou dinheiro."},

    # ── Lembretes ───────────────────────────────────────────────────────
    {"kind": "DESEMPENHO", "roles": "VENDEDOR", "trigger": "DEPLOYMENT",
     "title": "Unidade em implantação — seu placar é o esforço",
     "body": "Aqui ainda não existe meta de faturamento, e isso não quer dizer que não exista alvo. "
             "O que conta agora é oficina nova contatada, cadastro concluído e primeira compra. "
             "A carteira que você montar nestes meses é a que vai te sustentar o ano inteiro."},
    {"kind": "MEC", "roles": "VENDEDOR", "trigger": "DEPLOYMENT",
     "title": "Anote o CNPJ na primeira ligação",
     "body": "É o CNPJ que faz o sistema reconhecer sozinho quando a oficina virar cliente — e leva "
             "todo o seu histórico de prospecção para a ficha dela. Sem CNPJ, o vínculo vira "
             "trabalho manual e costuma se perder."},

    {"kind": "LEMBRETE", "roles": "VENDEDOR", "trigger": "TASKS_OVERDUE",
     "title": "Você tem tarefas atrasadas",
     "body": "Comece por elas. Cliente esperando retorno vencido é o jeito mais rápido de perder "
             "uma conta que já era sua."},
    {"kind": "LEMBRETE", "roles": "", "trigger": "",
     "title": "Fim do dia leva 5 minutos",
     "body": "Confira o que ficou aberto, remarque o que não terminou, avise o gerente dos "
             "bloqueios e deixe a primeira tarefa de amanhã pronta."},
    {"kind": "LEMBRETE", "roles": "GERENTE DIRETOR", "trigger": "",
     "title": "Reunião sem ata não aconteceu",
     "body": "Registre a reunião no mesmo dia, com os presentes e o que ficou combinado. Duas "
             "semanas depois ninguém lembra o que foi decidido — e o combinado vira discussão."},
    {"kind": "LEMBRETE", "roles": "GERENTE DIRETOR", "trigger": "VISITS_PENDING",
     "title": "Pedidos de visita esperando você",
     "body": "Sua equipe pediu presença em clientes. Responda, mesmo que seja para recusar com o "
             "motivo — pedido ignorado ensina o vendedor a parar de pedir."},
]
