"""
Conteúdo do módulo de Feedback: itens de avaliação e guia do gestor.

Fica em arquivo separado de propósito. O MEC ainda está sendo construído, e
ajustar um item de avaliação ou o texto de uma orientação não deveria exigir
mexer no motor do sistema. Editar aqui e reiniciar o serviço já vale.

Base: MEC - Método de Execução Comercial, Vendedor Passini, versão 4.0 (31/07/2026).

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
     "hint": "2 Bronze/Prata, 2 Ouro/Diamante e 1 prospecção. São 5, não 8.",
     "evidence": "Missão do Dia: quantos dos 5 saem por dia."},
    {"id": "mec_ligacoes", "group": "Execução do MEC",
     "label": "Mantém o mínimo de ligações",
     "hint": "Pelo menos 3 ligações por dia e 60 no mês.",
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
        "titulo": "Ligações abaixo do mínimo do MEC",
        "leitura": "3 por dia e 60 no mês é o piso, não a meta. Abaixo disso o resto do funil não tem "
                   "matéria-prima, e nenhuma outra correção funciona.",
        "perguntar": [
            "Em que horário do dia você costuma ligar?",
            "O que atrapalha: balcão, cotação, falta de lista?",
        ],
        "combinar": "Bloco fixo de ligação na agenda, no mesmo horário todo dia. "
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
