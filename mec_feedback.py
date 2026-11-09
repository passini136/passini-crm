"""
Conteúdo do módulo de Feedback: itens de avaliação e guia do gestor.

Fica em arquivo separado de propósito. O MEC ainda está sendo construído, e
ajustar um item de avaliação ou o texto de uma orientação não deveria exigir
mexer no motor do sistema. Editar aqui e reiniciar o serviço já vale.

Base: MEC - Método de Execução Comercial, Vendedor Passini, versão 4.1 (15/09/2026),
com as decisões do MEC 2.0 de 21/10/2026 (blocos de ligação, cotações do dia).

Revisão de 09/11/2026: os gerentes não têm prática de feedback nem de PDI.
O sistema passa a CONDUZIR a conversa — escolhe o elogio e os 2 pontos a
desenvolver pelos números, entrega as falas prontas e monta o PDI com meta
medida pelo próprio CRM. O gerente confirma e ajusta; não precisa criar do zero.

Os três níveis foram escolhidos para não ter meio-termo confortável: ou a pessoa
supera, ou faz o combinado, ou precisa evoluir. Escala de 1 a 5 faz todo mundo
virar 3 e a nota rouba a atenção da conversa.
"""

FEEDBACK_LEVELS = [
    {"id": "SUPERA",  "label": "Supera",          "icon": "▲", "color": "#1e8e3e", "bg": "#e6f4ea",
     "hint": "Faz além do combinado e serve de exemplo para a equipe."},
    {"id": "ATENDE",  "label": "Atende",          "icon": "●", "color": "#1a5276", "bg": "#e8f0fe",
     "hint": "Cumpre o que o MEC pede, de forma consistente."},
    {"id": "EVOLUIR", "label": "Precisa evoluir", "icon": "▼", "color": "#c5221f", "bg": "#fce8e6",
     "hint": "Falha ou é irregular. Exige combinado com prazo."},
]
FEEDBACK_LEVEL_IDS = {n["id"] for n in FEEDBACK_LEVELS}


# ─────────────────────────────────────────────────────────────────────────────
# Itens avaliados no feedback do VENDEDOR
#
# "evidence" diz ao gerente onde conferir antes de marcar. Feedback baseado em
# impressão gera discussão; baseado em tela gera combinado.
# ─────────────────────────────────────────────────────────────────────────────

FEEDBACK_ITEMS_SELLER = [
    # ── Execução do MEC ──────────────────────────────────────────────────
    {"id": "mec_fila", "group": "Execução do MEC",
     "label": "Cumpre a fila do CRM",
     "hint": "Abre o dia pela fila e faz a primeira tarefa antes de escolher o que fazer.",
     "evidence": "Missão do Dia e Tarefas: retornos atrasados acumulados?"},
    {"id": "mec_top5", "group": "Execução do MEC",
     "label": "Faz o TOP 5 com a composição certa",
     "hint": "Os 4 primeiros da Missão do Dia + 1 prospecção na tela Prospecção. São 5, não 8.",
     "evidence": "Missão do Dia: quantos dos 5 saem por dia."},
    {"id": "mec_ligacoes", "group": "Execução do MEC",
     "label": "Mantém o mínimo de contatos ativos",
     "hint": "60 contatos ativos concluídos no mês (≈3 por dia útil), nos blocos de 8h40–9h20 e 16h30–17h10.",
     "evidence": "Indicador de ligações do mês, no quadro acima."},
    {"id": "mec_registro", "group": "Execução do MEC",
     "label": "Faz registro válido",
     "hint": "Com quem falou, o que o cliente precisa, o que aconteceu e o que será feito. "
             "'Falei com o cliente' não é registro.",
     "evidence": "Abra 3 interações recentes e leia."},
    {"id": "mec_proxima_acao", "group": "Execução do MEC",
     "label": "Marca a próxima ação com data e hora",
     "hint": "Atendimento sem próximo passo continua aberto.",
     "evidence": "Tarefas do vendedor: há follow-up marcado?"},
    {"id": "mec_orcamento", "group": "Execução do MEC",
     "label": "Acompanha o orçamento enviado",
     "hint": "Liga em até 10 minutos para confirmar o recebimento e pergunta o que falta para fechar.",
     "evidence": "Interações com resultado 'gerou orçamento' e o que veio depois."},
    {"id": "mec_prospeccao", "group": "Execução do MEC",
     "label": "Faz a prospecção diária",
     "hint": "O quinto contato do TOP 5 é cliente novo.",
     "evidence": "Clientes novos no mês."},
    {"id": "mec_prospeccao_qualidade", "group": "Execução do MEC",
     "label": "Prospecção com as 4 perguntas e fechamento",
     "hint": "Tipo de serviço, carros por semana, linha que mais gira e forma de pagamento — "
             "e termina com um dos 3 gatilhos. Sem gatilho, a prospecção não conta no funil.",
     "evidence": "Abra 2 registros de prospecção: as 4 respostas estão anotadas? Há gatilho aceito?"},
    {"id": "mec_carteira", "group": "Execução do MEC",
     "label": "Trabalha a carteira inteira",
     "hint": "Clientes sem compra, recuperação, recompra e aumento de mix — não só quem liga.",
     "evidence": "Carteira: inativos e pré-inativos sem contato no mês."},

    # ── Comportamento e postura (tabela de boas práticas × limites do MEC) ──
    {"id": "comp_tecnica", "group": "Comportamento e postura",
     "label": "Confirma a aplicação antes de vender",
     "hint": "Pede apoio na dúvida técnica. Não arrisca venda errada.",
     "evidence": "Devoluções por erro de aplicação."},
    {"id": "comp_retorno", "group": "Comportamento e postura",
     "label": "Não deixa cliente sem resposta",
     "hint": "Cumpre o horário prometido. Se não puder resolver, avisa a hora exata do retorno.",
     "evidence": "Reclamações e retornos vencidos."},
    {"id": "comp_veracidade", "group": "Comportamento e postura",
     "label": "Registra o que realmente aconteceu",
     "hint": "Não inventa contato, visita, resultado ou motivo de perda. Aqui não existe meio-termo.",
     "evidence": "Amostra de registros × o que o cliente confirma."},
    {"id": "comp_politica", "group": "Comportamento e postura",
     "label": "Respeita a política comercial",
     "hint": "Não cria desconto, prazo, frete, crédito ou exceção por conta própria.",
     "evidence": "% de desconto do vendedor × média da unidade."},
    {"id": "comp_equipe", "group": "Comportamento e postura",
     "label": "Avisa bloqueios cedo e colabora",
     "hint": "Meta em risco se avisa no começo, não no dia 30. Ajuda o colega, não disputa cliente.",
     "evidence": "Como reagiu ao último problema da unidade."},
]

FEEDBACK_ITEM_GROUPS_SELLER = ["Execução do MEC", "Comportamento e postura"]


# ─────────────────────────────────────────────────────────────────────────────
# Itens avaliados no feedback do GERENTE (Diretor × Gerente)
#
# Estrutura apoiada em dois modelos consagrados:
#   GROW (Whitmore) — organiza a conversa: onde queremos chegar, onde estamos,
#   que caminhos existem, o que você vai fazer. É o esqueleto do bloco tático.
#   SBI (Center for Creative Leadership) — Situação, Comportamento, Impacto:
#   descreve o fato observado em vez de rotular a pessoa. É como o campo de
#   comportamento deve ser preenchido.
# ─────────────────────────────────────────────────────────────────────────────

FEEDBACK_ITEMS_MANAGER = [
    {"id": "ger_resultado", "group": "Resultado da unidade",
     "label": "Entrega a meta com margem saudável",
     "hint": "Bater meta queimando desconto não é entrega.",
     "evidence": "Executivo da unidade: atingimento, margem e % de desconto."},
    {"id": "ger_carteira", "group": "Resultado da unidade",
     "label": "Cuida da cobertura da carteira",
     "hint": "Clientes sem compra, recuperação de inativos e distribuição justa entre a equipe.",
     "evidence": "Clientes: ativos, pré-inativos, inativos e sem vendedor."},
    {"id": "ger_devolucao", "group": "Resultado da unidade",
     "label": "Controla devolução e retrabalho",
     "hint": "Devolução alta é sintoma de processo, não de azar.",
     "evidence": "% de devolução da unidade × meta."},

    {"id": "ger_ritos", "group": "Gestão da equipe",
     "label": "Cumpre os ritos",
     "hint": "Acompanhamento diário, reunião semanal registrada e feedback mensal de cada vendedor.",
     "evidence": "Reuniões e Feedback: o que foi registrado no período."},
    {"id": "ger_pessoas", "group": "Gestão da equipe",
     "label": "Desenvolve as pessoas",
     "hint": "PDI ativo para quem precisa, com acompanhamento real — não plano parado no papel.",
     "evidence": "PDIs abertos, prazos vencidos e evolução registrada."},
    {"id": "ger_mec", "group": "Gestão da equipe",
     "label": "Garante a execução do MEC na unidade",
     "hint": "Fila em dia, registro com qualidade, TOP 5 acontecendo.",
     "evidence": "Amostra de registros da equipe e tarefas atrasadas."},

    {"id": "ger_dados", "group": "Postura de gestão",
     "label": "Decide por dado, não por percepção",
     "hint": "Traz número quando cobra e quando defende a equipe.",
     "evidence": "Como sustentou as últimas decisões."},
    {"id": "ger_antecipa", "group": "Postura de gestão",
     "label": "Antecipa problema em vez de reportar",
     "hint": "Chega com o problema e a proposta, antes de virar prejuízo.",
     "evidence": "Últimos problemas: vieram do gerente ou foram descobertos?"},
    {"id": "ger_alinhamento", "group": "Postura de gestão",
     "label": "Sustenta a decisão da empresa",
     "hint": "Pode discordar na discussão; depois de decidido, defende junto à equipe.",
     "evidence": "Como comunicou a última mudança de política."},
]

FEEDBACK_ITEM_GROUPS_MANAGER = ["Resultado da unidade", "Gestão da equipe", "Postura de gestão"]


# ─────────────────────────────────────────────────────────────────────────────
# Guia do gestor: orientação prática por indicador fora do esperado.
#
# Cada entrada responde três coisas que o gerente precisa na hora da conversa:
# o que o número provavelmente significa, o que perguntar, e o que combinar.
# ─────────────────────────────────────────────────────────────────────────────

INDICATOR_GUIDE = {
    "goal_low": {
        "titulo": "Atingimento de meta abaixo do ritmo",
        "leitura": "O problema quase nunca é 'esforço'. Ou faltou volume de contato, "
                   "ou o contato não estava virando proposta, ou a carteira está encolhendo.",
        "perguntar": [
            "Quantas ligações você fez por dia neste mês?",
            "Dos orçamentos que enviou, quantos você retornou?",
            "Quais clientes da sua carteira pararam de comprar e por quê?",
        ],
        "combinar": "Escolha UMA alavanca para o próximo mês — volume de ligação, retorno de orçamento "
                    "ou recuperação de inativo — e defina o número. Três frentes ao mesmo tempo não sai do lugar.",
    },
    "calls_low": {
        "titulo": "Contatos ativos abaixo do mínimo do MEC",
        "leitura": "60 contatos ativos concluídos no mês (≈3 por dia) é o piso, não a meta. Abaixo disso "
                   "o resto do funil não tem matéria-prima, e nenhuma outra correção funciona.",
        "perguntar": [
            "Em que horário do dia você costuma ligar?",
            "O que atrapalha: balcão, cotação, falta de lista?",
        ],
        "combinar": "Os dois blocos de ligação do MEC, todo dia: 8h40–9h20 e 16h30–17h10. "
                    "Combine o número diário e confira na segunda-feira seguinte.",
    },
    "returns_high": {
        "titulo": "Devolução acima do aceitável",
        "leitura": "Devolução alta é erro de aplicação, promessa que não se cumpre ou pressa para fechar. "
                   "É processo, não azar.",
        "perguntar": [
            "Quais foram as últimas 3 devoluções e o motivo real de cada uma?",
            "Você confirmou veículo, motor e ano antes de faturar?",
        ],
        "combinar": "Conferência obrigatória de aplicação antes de faturar peça de linha crítica. "
                    "Na dúvida, pedir apoio técnico — perder a venda custa menos que devolver.",
    },
    "discount_high": {
        "titulo": "Desconto acima da média da unidade",
        "leitura": "Desconto alto costuma ser atalho para fugir da negociação. "
                   "Vende hoje e destrói a margem e o preço de referência do cliente.",
        "perguntar": [
            "Em quais clientes você deu mais desconto e o que pediram em troca?",
            "Você tentou prazo, marca alternativa ou mix antes de baixar o preço?",
        ],
        "combinar": "Antes de dar desconto, oferecer duas alternativas: marca equivalente ou condição de prazo. "
                    "Desconto fora da política precisa de autorização.",
    },
    "clients_low": {
        "titulo": "Poucos clientes atendidos no mês",
        "leitura": "Faturamento concentrado em poucos clientes é resultado frágil: "
                   "basta um deles parar para o mês virar.",
        "perguntar": [
            "Quantos clientes da sua carteira você não falou nenhuma vez este mês?",
            "Qual porcentagem do seu faturamento vem dos 3 maiores?",
        ],
        "combinar": "Meta de cobertura: número mínimo de clientes distintos atendidos por semana.",
    },
    "inactive_high": {
        "titulo": "Muitos clientes inativos na carteira",
        "leitura": "Cliente inativo é venda que já foi conquistada e está sendo perdida. "
                   "Custa menos recuperar do que prospectar.",
        "perguntar": [
            "Você sabe o motivo real de cada um ter parado?",
            "Quantos você tentou recuperar nos últimos 30 dias?",
        ],
        "combinar": "Lista de recuperação com nome e prazo. Contato com motivo registrado, "
                    "não só 'liguei e não atendeu'.",
    },
    "ticket_low": {
        "titulo": "Ticket médio abaixo da unidade",
        "leitura": "Ticket baixo geralmente é venda de item único: atende o pedido e não oferece o complemento.",
        "perguntar": [
            "Nas últimas vendas, você ofereceu o item que acompanha a peça?",
            "Você usa as sugestões de recompra da ficha do cliente?",
        ],
        "combinar": "Uma oferta complementar por atendimento, usando a sugestão que o CRM já mostra.",
    },
    "deployment": {
        "titulo": "Unidade em implantação — o que cobrar agora",
        "leitura": "Sem meta de faturamento, o que mede o trabalho é o esforço: ligações feitas, "
                   "oficinas novas cadastradas e primeiras compras. Faturamento nesta fase é "
                   "consequência, não indicador de desempenho.",
        "perguntar": [
            "Quantas oficinas novas você cadastrou este mês?",
            "Dos prospects que você qualificou, quantos já compraram a primeira vez?",
            "Onde está travando: achar a oficina, falar com o dono, ou fechar o cadastro?",
        ],
        "combinar": "Um número de esforço por semana — quantas oficinas novas contatadas e quantos "
                    "cadastros concluídos. Volume agora vira carteira depois; sem volume, a "
                    "unidade inaugura sem ninguém para vender.",
    },
    "good_overall": {
        "titulo": "Resultado dentro ou acima do esperado",
        "leitura": "Feedback bom mal dado vira 'está tudo certo' e não ensina nada. "
                   "Nomeie o comportamento que gerou o resultado.",
        "perguntar": [
            "O que você fez diferente neste mês?",
            "Isso dá para transformar em rotina e ensinar para a equipe?",
        ],
        "combinar": "Um passo de crescimento: assumir cliente maior, ajudar a treinar um colega, "
                    "ou puxar uma linha nova. Quem entrega precisa de próximo desafio, não de elogio solto.",
    },
}


# Roteiro da conversa. Curto de propósito — cabe num cartão.
FEEDBACK_SCRIPT_SELLER = [
    {"etapa": "1. Abrir", "tempo": "2 min",
     "texto": "Diga o objetivo: 'é para você crescer, não é advertência'. "
              "Comece perguntando como ELE avalia o próprio mês."},
    {"etapa": "2. Reconhecer", "tempo": "3 min",
     "texto": "Comece pelo que foi bem, com fato: 'você recuperou 4 clientes inativos'. "
              "Elogio sem dado não é reconhecido como verdadeiro."},
    {"etapa": "3. Mostrar os números", "tempo": "5 min",
     "texto": "Abra os indicadores juntos, na tela. Número na mesa tira a conversa do 'eu acho'."},
    {"etapa": "4. Apontar o que precisa evoluir", "tempo": "5 min",
     "texto": "Descreva a situação, o comportamento e o efeito — não rotule a pessoa. "
              "'No dia 12 o orçamento ficou sem retorno e o cliente comprou fora' funciona; "
              "'você é desorganizado' não."},
    {"etapa": "5. Ouvir", "tempo": "5 min",
     "texto": "Pergunte o que atrapalha e cale. A causa quase sempre aparece aqui."},
    {"etapa": "6. Combinar", "tempo": "5 min",
     "texto": "No máximo 2 pontos no PDI, com ação, prazo e quem apoia. "
              "Cinco pontos é o mesmo que nenhum."},
    {"etapa": "7. Fechar", "tempo": "2 min",
     "texto": "Peça para ele repetir o combinado com as palavras dele. "
              "Marque a data da próxima conversa antes de sair."},
]

FEEDBACK_SCRIPT_MANAGER = [
    {"etapa": "1. Objetivo (Goal)", "tempo": "5 min",
     "texto": "Onde a unidade precisa chegar no próximo trimestre e por quê. "
              "Alinhe o destino antes de discutir o caminho."},
    {"etapa": "2. Realidade (Reality)", "tempo": "10 min",
     "texto": "Números da unidade sem filtro: meta, margem, devolução, cobertura de carteira, "
              "ritos cumpridos. Peça a leitura dele antes de dar a sua."},
    {"etapa": "3. Opções (Options)", "tempo": "10 min",
     "texto": "Que caminhos existem? Deixe ele propor primeiro — gerente que recebe o plano pronto executa; "
              "gerente que constrói o plano assume."},
    {"etapa": "4. Compromisso (Will)", "tempo": "10 min",
     "texto": "O que ele vai fazer, até quando, e o que precisa da diretoria. "
              "Sem o pedido de apoio explícito, o plano trava e ninguém fica sabendo."},
    {"etapa": "5. Comportamento", "tempo": "5 min",
     "texto": "Se houver ponto de postura, descreva situação, comportamento e impacto. "
              "Um ponto por conversa — mais que isso vira lista de defeitos."},
]


# ─────────────────────────────────────────────────────────────────────────────
# PDI GUIADO — biblioteca de focos de desenvolvimento do vendedor
#
# Cada foco é UM comportamento do MEC, medido por UM número que o CRM já tem.
# É isso que torna o PDI simples para quem nunca fez: o gerente não escreve o
# plano, escolhe o foco que o sistema sugeriu e ajusta o número.
#
# Ordem = prioridade do MEC. Sem contato não há venda; sem retorno o contato se
# perde; só depois vêm carteira, margem e qualidade. Quando vários estão fora,
# o sistema sugere os DOIS primeiros desta ordem, não os dois piores — corrigir
# desconto de quem não liga não muda o mês.
#
# Campos de texto aceitam {valor}, {alvo} e {alvoMes}, preenchidos com o número
# formatado. Edite as frases à vontade; reinicie o serviço para valer.
# ─────────────────────────────────────────────────────────────────────────────

PDI_FOCOS = [
    {
        "id": "contatos",
        "titulo": "Volume de contato ativo",
        "metrica": "contatos ativos registrados no mês",
        "formato": "num", "melhor": "maior",
        "porque": "Sem contato não existe venda nova. É a matéria-prima de todo o resto do MEC.",
        "acoes": [
            "Fazer os dois blocos de ligação, todo dia: 8h40–9h20 e 16h30–17h10.",
            "Seguir o TOP 5: os 4 primeiros da Missão do Dia + 1 prospecção.",
            "Registrar cada contato na hora, inclusive 'não atendeu' — o que não está no CRM não aconteceu.",
        ],
        "onde": "Meu Placar (ligações) e Missão do Dia",
        "perguntas": [
            "Em que horário do dia você costuma ligar?",
            "O que tira você do telefone: balcão, cotação, falta de lista?",
        ],
        "falaEvoluir": "Até agora foram {valor} contatos ativos registrados; o MEC pede {alvo} até esta data. "
                       "Sem esse volume, o resto não acontece.",
        "falaForca": "Você fez {valor} contatos ativos registrados, acima dos {alvo} que o MEC pede até aqui. "
                     "É isso que sustenta o resultado.",
        "combinar": "Fazer os dois blocos de ligação todo dia e chegar a {alvoMes} contatos ativos no mês.",
    },
    {
        "id": "retornos",
        "titulo": "Retorno no prazo combinado",
        "metrica": "tarefas de retorno vencidas e em aberto",
        "formato": "num", "melhor": "menor",
        "porque": "Retorno atrasado é cliente esperando. Ele compra de quem responde primeiro.",
        "acoes": [
            "Abrir o dia pela fila de Tarefas e zerar as atrasadas antes de qualquer contato novo.",
            "Se não puder resolver, avisar o cliente a hora exata do retorno — e cumprir.",
            "Ao registrar, marcar sempre a próxima ação com data e hora.",
        ],
        "onde": "Tarefas (filtro: atrasadas)",
        "perguntas": [
            "Por que essas tarefas ficaram para trás?",
            "Tem tarefa ali que não faz mais sentido e só precisa ser encerrada?",
        ],
        "falaEvoluir": "Hoje você tem {valor} retornos vencidos em aberto. Cada um é um cliente que ficou esperando.",
        "falaForca": "Sua fila de retornos está em dia: {valor} tarefas vencidas. Cliente seu não fica esperando.",
        "combinar": "Começar o dia pelas tarefas atrasadas e manter no máximo {alvo} vencidas.",
    },
    {
        "id": "cotacoes",
        "titulo": "Fechamento de cotação",
        "metrica": "cotações sem desfecho há mais de 1 dia",
        "formato": "num", "melhor": "menor",
        "porque": "Cotação sem retorno vira compra no concorrente. O MEC pede ligar em até 10 minutos.",
        "acoes": [
            "Depois de mandar o orçamento, ligar em até 10 minutos para confirmar e perguntar o que falta para fechar.",
            "Marcar no mesmo dia se fechou ou perdeu — e o motivo da perda.",
            "Perda por falta de peça: registrar a peça, para compras enxergar.",
        ],
        "onde": "Cotações do Dia",
        "perguntas": [
            "Das cotações em aberto, quais ainda dá para fechar hoje?",
            "Por que a última que você perdeu foi perdida?",
        ],
        "falaEvoluir": "Você tem {valor} cotações sem desfecho há mais de um dia. Cotação parada é venda indo para o concorrente.",
        "falaForca": "Suas cotações têm desfecho no prazo — {valor} paradas. Isso mostra controle do funil.",
        "combinar": "Retornar toda cotação em até 10 minutos e dar desfecho (fechou ou perdeu, com motivo) até o dia seguinte.",
    },
    {
        "id": "carteira",
        "titulo": "Recuperar a carteira parada",
        "metrica": "clientes da carteira pré-inativos ou inativos",
        "formato": "num", "melhor": "menor",
        "porque": "Cliente parado é venda já conquistada sendo perdida. Recuperar custa menos que prospectar.",
        "acoes": [
            "Separar na Carteira os pré-inativos (filtro de situação) e ligar primeiro para eles — ainda dá para segurar.",
            "Em cada ligação, descobrir e registrar o motivo real de ter parado.",
            "Usar a peça-isca sugerida na ficha para dar um motivo de compra.",
        ],
        "onde": "Carteira (situação: pré-inativo e inativo)",
        "perguntas": [
            "Você sabe por que cada um desses clientes parou?",
            "Quantos você conseguiu falar nos últimos 30 dias?",
        ],
        "falaEvoluir": "Hoje {valor} clientes da sua carteira estão parados (pré-inativos ou inativos). "
                       "Cada um já comprou de você.",
        "falaForca": "Sua carteira está ativa: só {valor} clientes parados. Você cuida de quem já é cliente.",
        "combinar": "Ligar para os pré-inativos primeiro e baixar a carteira parada para {alvo} clientes.",
    },
    {
        "id": "cobertura",
        "titulo": "Atender mais clientes",
        "metrica": "clientes diferentes atendidos no mês",
        "formato": "num", "melhor": "maior",
        "porque": "Faturamento em poucos clientes é frágil: basta um parar para o mês virar.",
        "acoes": [
            "Toda semana, falar com clientes da carteira que ainda não compraram no mês.",
            "Usar a Missão do Dia: ela já mostra quem está sem compra.",
        ],
        "onde": "Carteira (sem compra no mês) e Missão do Dia",
        "perguntas": [
            "Quantos clientes da sua carteira você não falou nenhuma vez este mês?",
            "Quanto do seu faturamento vem dos 3 maiores clientes?",
        ],
        "falaEvoluir": "Você atendeu {valor} clientes no mês; a média da sua unidade é {alvo}.",
        "falaForca": "Você atendeu {valor} clientes diferentes, acima da média da unidade ({alvo}). Seu resultado não depende de poucos.",
        "combinar": "Chegar a {alvo} clientes diferentes atendidos no mês.",
    },
    {
        "id": "desconto",
        "titulo": "Negociar antes de dar desconto",
        "metrica": "desconto médio concedido",
        "formato": "pct", "melhor": "menor",
        "porque": "Desconto alto vende hoje e destrói a margem e o preço de referência do cliente.",
        "acoes": [
            "Antes de baixar preço, oferecer duas alternativas: marca equivalente ou condição de prazo.",
            "Desconto fora da política só com autorização do gerente.",
        ],
        "onde": "Meu Placar (margem) e ficha do cliente",
        "perguntas": [
            "Em quais clientes você deu mais desconto e o que pediram em troca?",
            "Você tentou outra marca ou prazo antes de baixar o preço?",
        ],
        "falaEvoluir": "Seu desconto médio está em {valor}; a média da unidade é {alvo}.",
        "falaForca": "Seu desconto médio ({valor}) está abaixo da média da unidade ({alvo}). Você vende sem queimar margem.",
        "combinar": "Trazer o desconto médio para {alvo}, oferecendo marca ou prazo antes de baixar preço.",
    },
    {
        "id": "devolucao",
        "titulo": "Confirmar a aplicação antes de faturar",
        "metrica": "devolução sobre o faturamento",
        "formato": "pct", "melhor": "menor",
        "porque": "Devolução é erro de aplicação ou pressa. Custa frete, retrabalho e a confiança do cliente.",
        "acoes": [
            "Confirmar veículo, motor e ano antes de faturar peça de linha crítica.",
            "Na dúvida técnica, pedir apoio — perder a venda custa menos que devolver.",
        ],
        "onde": "Devoluções",
        "perguntas": [
            "Quais foram as últimas 3 devoluções e o motivo real de cada uma?",
            "Você confirmou a aplicação antes de faturar?",
        ],
        "falaEvoluir": "Sua devolução está em {valor} do faturamento; o limite é {alvo}.",
        "falaForca": "Sua devolução está em {valor}, dentro do limite de {alvo}. Você vende a peça certa.",
        "combinar": "Confirmar a aplicação em toda venda de linha crítica e ficar abaixo de {alvo} de devolução.",
    },
    {
        "id": "ticket",
        "titulo": "Oferecer o complemento",
        "metrica": "ticket médio por cliente",
        "formato": "brl", "melhor": "maior",
        "porque": "Ticket baixo é venda de item único: atende o pedido e não oferece o que acompanha a peça.",
        "acoes": [
            "Em todo atendimento, oferecer o item que acompanha a peça (kit, fluido, junta).",
            "Usar a sugestão de mix e de recompra que a ficha do cliente já mostra.",
        ],
        "onde": "Ficha do cliente (sugestões) e Meu Placar",
        "perguntas": [
            "Nas últimas vendas, você ofereceu o item que acompanha a peça?",
            "Você usa as sugestões da ficha do cliente?",
        ],
        "falaEvoluir": "Seu ticket médio está em {valor}; a média da unidade é {alvo}.",
        "falaForca": "Seu ticket médio ({valor}) está acima da unidade ({alvo}). Você oferece o complemento.",
        "combinar": "Uma oferta complementar por atendimento, chegando a {alvo} de ticket médio.",
    },
]


# Roteiro guiado: quatro passos, com a FALA pronta. Para quem nunca deu
# feedback, frase pronta vale mais que princípio. {forca} e {evoluir} são
# preenchidos com as falas do foco escolhido.
ROTEIRO_GUIADO = [
    {"passo": "Abrir", "tempo": "2 min",
     "fala": "Essa conversa é para você crescer, não é advertência. Antes de eu falar, "
             "como você avalia o seu mês?",
     "dica": "Deixe ele falar primeiro. Não interrompa."},
    {"passo": "Reconhecer", "tempo": "3 min",
     "fala": "{forca}",
     "dica": "Elogio com número. 'Bom trabalho' sozinho não é levado a sério."},
    {"passo": "Mostrar o ponto a desenvolver", "tempo": "5 min",
     "fala": "{evoluir} O que está atrapalhando?",
     "dica": "Mostre o número na tela. Fale do fato, nunca da pessoa ('você é desorganizado' não)."},
    {"passo": "Ouvir", "tempo": "5 min",
     "fala": "{pergunta}",
     "dica": "Pergunte e fique quieto. A causa aparece aqui. Anote."},
    {"passo": "Combinar", "tempo": "5 min",
     "fala": "Então combinamos: {combinar} Vou acompanhar com você toda segunda. Me fala com as suas palavras o que ficou combinado?",
     "dica": "No máximo 2 pontos. Ele repete o combinado — se não souber repetir, não entendeu."},
]

# O que fazer depois da conversa — a parte que mais se perde.
ACOMPANHAMENTO_DICAS = [
    "Toda segunda, 5 minutos: abra o PDI, olhe o número e marque se avançou.",
    "Avançou: elogie na hora, com o número. Parado: pergunte o que travou e ajude a destravar.",
    "Não espere o fim do mês para corrigir. O registro pontual serve para isso.",
]
