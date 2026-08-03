"""
Conteúdo inicial da biblioteca comercial do CRM Passini.

Escrito para a realidade de distribuição de autopeças: quem fala é o vendedor
interno/televendas, quem ouve é o dono de oficina ou o balconista da revenda.
Linguagem direta, sem jargão de vendas, focada em resolver o dia do mecânico.

Placeholders substituídos em tempo de exibição:
  {cliente}  {vendedor}  {item}  {dias}  {unidade}
"""

CONTENT_SEED = [
    # ─────────────────────────────────────────────────────────────────────
    # LIGAÇÃO ATIVA
    # ─────────────────────────────────────────────────────────────────────
    {
        "category": "ligacao", "situation": "INATIVO", "sort_order": 1,
        "title": "Reativação — cliente parado há mais de 60 dias",
        "hint": "Objetivo: descobrir o motivo real da parada. Não empurre preço na primeira frase.",
        "body": (
            "Abertura:\n"
            "\"{cliente}, aqui é {vendedor} da Passini. Vi que faz {dias} dias que a gente não "
            "atende vocês e liguei pra entender o que aconteceu — sem enrolação.\"\n\n"
            "Pergunta que abre o jogo (escolha uma):\n"
            "• \"Foi preço, prazo de entrega ou faltou peça na hora que você precisou?\"\n"
            "• \"Vocês passaram a comprar de outro fornecedor ou o movimento da oficina caiu?\"\n\n"
            "Se foi ENTREGA/FALTA:\n"
            "\"Entendi. Hoje o que a gente tem de pronta entrega pra sua região é {item}. "
            "Se você precisar hoje, eu consigo separar agora e sai no próximo carro.\"\n\n"
            "Se foi PREÇO:\n"
            "\"Justo. Me passa qual peça e qual valor você está comprando, que eu vejo o que "
            "consigo fazer. Se eu não cobrir, eu te falo na hora e não te faço perder tempo.\"\n\n"
            "Fechamento (sempre marque o retorno):\n"
            "\"Vou te mandar no WhatsApp agora. Posso te ligar {dia_retorno} pra saber se serviu?\""
        ),
    },
    {
        "category": "ligacao", "situation": "PRE_INATIVO", "sort_order": 1,
        "title": "Preventivo — cliente espaçando os pedidos",
        "hint": "Ele ainda compra, mas está comprando menos ou mais espaçado. Aja antes de virar inativo.",
        "body": (
            "Abertura:\n"
            "\"{cliente}, {vendedor} da Passini. Não é cobrança, é acompanhamento: notei que o "
            "ritmo de pedido mudou e queria saber se está tudo certo aí na oficina.\"\n\n"
            "Perguntas úteis:\n"
            "• \"O movimento está mais fraco ou vocês estão comprando parcelado em mais lugares?\"\n"
            "• \"Tem alguma linha que eu deixei de te atender bem?\"\n"
            "• \"Qual dia da semana é melhor pra você receber? Consigo alinhar a entrega.\"\n\n"
            "Gancho de recompra:\n"
            "\"Você levava {item} com frequência e faz um tempo que não sai. Ainda usa? "
            "Se quiser eu já deixo reservado.\"\n\n"
            "Fechamento:\n"
            "\"Fecho um pedido pequeno agora só pra não te deixar na mão, e a gente ajusta o "
            "resto na semana. Pode ser?\""
        ),
    },
    {
        "category": "ligacao", "situation": "SEM_COMPRA_MES", "sort_order": 1,
        "title": "Cliente ativo que ainda não comprou este mês",
        "hint": "Ele compra normalmente, só não pediu ainda. Contato curto, de reposição.",
        "body": (
            "Abertura curta:\n"
            "\"{cliente}, {vendedor} da Passini, rapidinho. Fechando o mês e vi que vocês ainda "
            "não fizeram pedido. Precisa repor alguma coisa?\"\n\n"
            "Se ele disser que está abastecido:\n"
            "\"Beleza. Só pra eu não te deixar quebrado: {item} você costuma girar. "
            "Tem estoque aí ou já foi?\"\n\n"
            "Se ele estiver sem serviço:\n"
            "\"Entendo. Deixa eu te avisar quando entrar campanha da linha que você mais usa? "
            "Aí você aproveita quando o movimento voltar.\"\n\n"
            "Fechamento:\n"
            "\"Fecho o pedido até {hora_corte} e sai hoje. Depois disso só amanhã.\""
        ),
    },
    {
        "category": "ligacao", "situation": "QUEDA", "sort_order": 1,
        "title": "Cliente comprando menos que a média dele",
        "hint": "O volume caiu. Descubra se perdeu participação ou se a oficina caiu de movimento.",
        "body": (
            "Abertura honesta:\n"
            "\"{cliente}, {vendedor} da Passini. Olhando aqui, vocês estão comprando menos do "
            "que costumavam. Queria entender se o problema é comigo ou se o movimento caiu.\"\n\n"
            "Perguntas:\n"
            "• \"Que linha vocês passaram a comprar em outro lugar?\"\n"
            "• \"Teve alguma peça que eu demorei a entregar e te queimei?\"\n"
            "• \"Tem serviço que vocês passaram a não fazer mais?\"\n\n"
            "Se perdeu para concorrente:\n"
            "\"Fico sabendo agora. Me dá uma chance de cotar essa linha: manda dois ou três "
            "códigos que você mais compra lá e eu te devolvo hoje ainda.\"\n\n"
            "Fechamento:\n"
            "\"Combinado assim: você me manda os códigos, eu cotó e te ligo {dia_retorno}.\""
        ),
    },
    {
        "category": "ligacao", "situation": "MIX", "sort_order": 1,
        "title": "Ampliar mix — cliente compra pouca variedade",
        "hint": "Ele é fiel mas compra sempre a mesma coisa. Abra linha nova ligada ao serviço dele.",
        "body": (
            "Abertura:\n"
            "\"{cliente}, {vendedor} da Passini. Você compra bem {item} comigo, mas tem linha "
            "que você nunca pediu e as oficinas da sua região giram bastante.\"\n\n"
            "Pergunta de diagnóstico (a mais importante):\n"
            "\"Que tipo de serviço vocês mais fazem hoje? Suspensão, freio, motor, elétrica?\"\n\n"
            "Depois que ele responder, conecte:\n"
            "\"Então faz sentido você ter {item} em estoque. Quem faz esse serviço quase sempre "
            "precisa e é chato parar o carro esperando peça.\"\n\n"
            "Oferta de teste (baixe a barreira):\n"
            "\"Leva uma quantidade pequena pra testar giro. Se não sair, você não repete e "
            "tudo bem — eu prefiro que você compre certo do que compre demais.\""
        ),
    },
    {
        "category": "ligacao", "situation": "NOVO", "sort_order": 1,
        "title": "Primeiro contato — cliente novo ou recém-cadastrado",
        "hint": "Objetivo aqui não é vender tudo, é entender a oficina e fazer o primeiro pedido dar certo.",
        "body": (
            "Abertura:\n"
            "\"{cliente}, {vendedor} da Passini. Vocês estão começando a comprar com a gente e "
            "eu queria me apresentar antes de te empurrar qualquer coisa.\"\n\n"
            "Perguntas para mapear a oficina:\n"
            "• \"Vocês atendem mais que tipo de carro? Popular, importado, linha pesada?\"\n"
            "• \"Que serviço vocês mais fazem no dia a dia?\"\n"
            "• \"Quantos elevadores/box vocês têm?\"\n"
            "• \"Qual horário é melhor pra receber peça?\"\n\n"
            "Combinado de atendimento:\n"
            "\"Meu compromisso: se eu não tiver a peça, eu te falo na hora, não te deixo "
            "esperando. E se eu prometer entrega, eu cumpro.\"\n\n"
            "Fechamento:\n"
            "\"Vou te mandar meu contato. Salva aí como {vendedor} Passini — qualquer urgência "
            "você chama direto.\""
        ),
    },

    # ─────────────────────────────────────────────────────────────────────
    # WHATSAPP
    # ─────────────────────────────────────────────────────────────────────
    {
        "category": "whatsapp", "situation": "INATIVO", "sort_order": 1,
        "title": "Reativação — mensagem curta",
        "hint": "Curta e sem cara de robô. Uma pergunta só, fácil de responder.",
        "body": (
            "Oi {cliente}, aqui é o {vendedor} da Passini 👋\n\n"
            "Faz um tempo que a gente não atende vocês e fiquei na dúvida se foi alguma coisa "
            "que a gente deixou a desejar.\n\n"
            "Foi preço, entrega ou faltou peça?\n\n"
            "Se quiser me mandar dois ou três códigos que vocês mais usam, eu coto e te devolvo hoje."
        ),
    },
    {
        "category": "whatsapp", "situation": "PRE_INATIVO", "sort_order": 1,
        "title": "Preventivo — retomar frequência",
        "hint": "Tom leve. Ele ainda é cliente, não trate como perdido.",
        "body": (
            "Oi {cliente}, {vendedor} da Passini!\n\n"
            "Vi que faz alguns dias que vocês não pedem nada. Precisa repor alguma coisa "
            "essa semana?\n\n"
            "Se quiser, eu já separo e mando junto com a próxima entrega da região 🚚"
        ),
    },
    {
        "category": "whatsapp", "situation": "SEM_COMPRA_MES", "sort_order": 1,
        "title": "Reposição do mês",
        "hint": "Use quando falta pouco para fechar o mês e ele ainda não pediu.",
        "body": (
            "Oi {cliente}! {vendedor} da Passini.\n\n"
            "Passando pra ver se falta alguma coisa aí — vocês ainda não fizeram pedido esse mês.\n\n"
            "Me manda a lista que eu separo. Pedido até {hora_corte} sai hoje 👍"
        ),
    },
    {
        "category": "whatsapp", "situation": "MIX", "sort_order": 1,
        "title": "Sugestão de item que ele não compra",
        "hint": "Justifique pelo serviço da oficina dele, não pela promoção.",
        "body": (
            "Oi {cliente}, {vendedor} aqui.\n\n"
            "Reparei que vocês não compram {item} comigo. As oficinas aqui da região giram "
            "bastante esse item.\n\n"
            "Vale a pena deixar uma quantidade pequena em estoque pra não parar carro esperando peça.\n\n"
            "Quer que eu te passe o preço?"
        ),
    },
    {
        "category": "whatsapp", "situation": "GERAL", "sort_order": 2,
        "title": "Confirmação de pedido e entrega",
        "hint": "Reduz ligação de cobrança e passa segurança.",
        "body": (
            "{cliente}, pedido confirmado ✅\n\n"
            "Itens: {itens}\n"
            "Previsão de entrega: {previsao}\n\n"
            "Qualquer coisa me chama por aqui. Se der qualquer problema na peça, fala comigo "
            "antes de instalar que a gente resolve."
        ),
    },
    {
        "category": "whatsapp", "situation": "GERAL", "sort_order": 3,
        "title": "Pós-venda — 3 dias após a entrega",
        "hint": "Contato rápido que previne devolução e gera recompra.",
        "body": (
            "Oi {cliente}, tudo certo com as peças que chegaram?\n\n"
            "Serviu direitinho no carro?\n\n"
            "Se sobrou alguma dúvida de aplicação me chama, e se precisar repor é só falar 🔧"
        ),
    },

    # ─────────────────────────────────────────────────────────────────────
    # OBJEÇÕES
    # ─────────────────────────────────────────────────────────────────────
    {
        "category": "objecao", "situation": "GERAL", "sort_order": 1,
        "title": "\"Está caro / achei mais barato\"",
        "hint": "Nunca discuta o preço no vazio. Peça o número e compare peça a peça.",
        "body": (
            "Não faça: baixar preço na hora sem entender o que ele comparou.\n\n"
            "Faça:\n"
            "\"Qual peça e qual valor? Porque às vezes é marca diferente e aí não dá pra comparar.\"\n\n"
            "Se for a mesma marca e realmente mais barato:\n"
            "\"Tá certo, esse tá abaixo do meu. Não vou te enrolar. O que eu consigo é "
            "{condicao}. Se não fechar pra você, sem problema — fica pra próxima.\"\n\n"
            "Se for marca inferior:\n"
            "\"Aí muda. Essa que você cotou é linha mais simples. Se o carro é de cliente e "
            "volta com problema, quem paga a mão de obra de novo é você. "
            "Vale a diferença pra não retrabalhar.\"\n\n"
            "Fechamento:\n"
            "\"Se preço for o problema, me fala qual item é crítico pra você. "
            "Eu prefiro te atender no que é importante do que perder você inteiro.\""
        ),
    },
    {
        "category": "objecao", "situation": "GERAL", "sort_order": 2,
        "title": "\"Já tenho fornecedor\"",
        "hint": "Não peça exclusividade. Peça um pedaço.",
        "body": (
            "\"Imaginei que sim, você não ia ficar parado esperando eu ligar 😄\n\n"
            "Não quero tirar seu fornecedor. Quero ser o segundo — aquele que você liga "
            "quando o primeiro não tem.\n\n"
            "Me deixa cotar duas ou três peças que você compra sempre. Se eu for melhor, "
            "você compra. Se não for, pelo menos você fica sabendo que tem opção.\"\n\n"
            "Complemento útil:\n"
            "\"Quantas vezes esse mês você deixou de fazer um serviço porque a peça não chegou? "
            "É pra essas horas que eu sirvo.\""
        ),
    },
    {
        "category": "objecao", "situation": "GERAL", "sort_order": 3,
        "title": "\"Vou ver e te retorno\"",
        "hint": "Sem retorno marcado, essa frase significa não. Marque data e hora.",
        "body": (
            "\"Tranquilo. Só pra eu não te encher: te ligo {dia_retorno} de manhã ou de tarde?\"\n\n"
            "Se ele desconversar:\n"
            "\"Tem alguma coisa que ficou faltando eu explicar? Pode falar direto, "
            "não me ofendo não.\"\n\n"
            "Alternativa:\n"
            "\"Deixa eu te mandar por escrito no WhatsApp. Aí você olha com calma e "
            "me responde quando der.\"\n\n"
            "Registre a tarefa no sistema para o retorno não se perder."
        ),
    },
    {
        "category": "objecao", "situation": "GERAL", "sort_order": 4,
        "title": "\"Estoque cheio / não preciso agora\"",
        "hint": "Aceite, mas descubra quando ele vai precisar.",
        "body": (
            "\"Perfeito, melhor assim do que comprar demais.\n\n"
            "Quando você acha que vai precisar repor? Pra eu te ligar na hora certa e "
            "não ficar te incomodando à toa.\"\n\n"
            "Se ele der um prazo, agende a tarefa no sistema para essa data.\n\n"
            "Gancho:\n"
            "\"Tem alguma peça que você usa e sempre falta na hora que precisa? "
            "Essa eu posso deixar reservada pra você.\""
        ),
    },
    {
        "category": "objecao", "situation": "GERAL", "sort_order": 5,
        "title": "\"Última vez atrasou a entrega\"",
        "hint": "Reconheça sem inventar desculpa. O que resolve é compromisso concreto.",
        "body": (
            "\"Você tem razão e eu não vou inventar desculpa.\n\n"
            "O que eu posso fazer é o seguinte: nesse pedido eu te falo a data real, não a "
            "otimista. E se atrasar, eu te aviso antes de você descobrir sozinho.\"\n\n"
            "Não prometa prazo que você não controla.\n\n"
            "\"Faz um teste comigo com um pedido pequeno. Se eu cumprir, você aumenta. "
            "Se eu falhar de novo, você tem razão de não comprar mais.\""
        ),
    },

    # ─────────────────────────────────────────────────────────────────────
    # DEVOLUÇÃO E GARANTIA
    # ─────────────────────────────────────────────────────────────────────
    {
        "category": "garantia", "situation": "GERAL", "sort_order": 1,
        "title": "Prazos legais — o que o vendedor precisa saber",
        "hint": "Orientação geral. Valide com o jurídico da Passini antes de usar como regra oficial.",
        "body": (
            "GARANTIA LEGAL (Código de Defesa do Consumidor)\n\n"
            "Prazo para reclamar de defeito aparente (que dá pra ver):\n"
            "• Produto durável, como peça automotiva: 90 dias\n"
            "• Produto não durável: 30 dias\n"
            "O prazo conta da entrega do produto. (CDC, art. 26)\n\n"
            "Defeito oculto (só aparece com o uso):\n"
            "O prazo começa a contar do dia em que o defeito ficou evidente, "
            "não da data da compra. (CDC, art. 26, §3º)\n\n"
            "Prazo para resolver:\n"
            "O fornecedor tem até 30 dias para sanar o defeito. Se não resolver nesse prazo, "
            "o consumidor escolhe entre: troca por outro produto, devolução do valor pago "
            "corrigido, ou abatimento proporcional do preço. (CDC, art. 18)\n\n"
            "Garantia contratual (do fabricante):\n"
            "É adicional à legal, nunca substitui. Somam-se. (CDC, art. 50)\n\n"
            "ATENÇÃO — venda entre empresas:\n"
            "Quando a oficina compra para revender ou aplicar em serviço, ela não é "
            "necessariamente 'consumidor final', e o CDC pode não se aplicar automaticamente. "
            "Nesses casos vale o Código Civil e o contrato entre as partes. "
            "Os tribunais às vezes aplicam o CDC mesmo assim quando reconhecem "
            "vulnerabilidade técnica do comprador.\n\n"
            "Este material é orientação prática, não parecer jurídico. "
            "Casos concretos devem ser validados com o jurídico da Passini."
        ),
    },
    {
        "category": "garantia", "situation": "GERAL", "sort_order": 2,
        "title": "Atendimento de reclamação de peça",
        "hint": "Roteiro de conversa. O processo interno da Passini será detalhado neste espaço.",
        "body": (
            "Como conduzir a conversa:\n\n"
            "1. Ouça antes de julgar\n"
            "\"Me conta o que aconteceu com a peça. Que sintoma o carro apresentou?\"\n\n"
            "2. Levante os dados objetivos\n"
            "• Nota fiscal e data da compra\n"
            "• Código da peça e marca\n"
            "• Veículo: modelo, ano, motorização\n"
            "• Quilometragem ou tempo de uso da peça\n"
            "• O defeito apareceu na instalação ou depois de rodar?\n\n"
            "3. Nunca prometa o que não depende de você\n"
            "\"Vou registrar e acionar o fabricante. Não vou te prometer prazo que eu não "
            "controlo, mas vou te dar retorno mesmo que a resposta ainda não tenha chegado.\"\n\n"
            "4. Oriente sobre a peça\n"
            "Peça não deve ser descartada nem desmontada antes da análise — "
            "isso pode inviabilizar a garantia junto ao fabricante.\n\n"
            "5. Registre a interação no CRM\n"
            "Sem registro não há acompanhamento, e cliente com garantia mal resolvida "
            "é o que mais vira inativo.\n\n"
            "[ESPAÇO PARA O PROCESSO INTERNO DA PASSINI — prazos, formulário, "
            "responsáveis e regras por fabricante]"
        ),
    },
    {
        "category": "garantia", "situation": "GERAL", "sort_order": 3,
        "title": "Situações que normalmente não têm cobertura",
        "hint": "Explique com cuidado. Confirme sempre com o fabricante antes de negar.",
        "body": (
            "Casos em que o fabricante costuma recusar a garantia:\n\n"
            "• Instalação incorreta ou fora da especificação do fabricante\n"
            "• Peça aplicada em veículo diferente do catálogo\n"
            "• Dano por outro componente do sistema (ex.: pastilha nova em disco empenado)\n"
            "• Uso do veículo fora da condição normal (competição, sobrecarga)\n"
            "• Peça violada, usinada ou modificada\n"
            "• Desgaste natural dentro da vida útil esperada\n\n"
            "Como comunicar sem perder o cliente:\n"
            "\"Pelo que você descreveu, é possível que o fabricante aponte causa externa. "
            "Mesmo assim eu vou abrir a análise — não vou negar por conta própria. "
            "Se der negativa, eu te mostro o laudo.\"\n\n"
            "Postura importante:\n"
            "Negar garantia no telefone, sem análise, é a forma mais rápida de perder a "
            "oficina. Abra o processo, mostre o caminho e dê retorno."
        ),
    },
]
