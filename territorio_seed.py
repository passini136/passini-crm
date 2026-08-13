"""Mapa de territórios da Passini — conteúdo, não motor.

Porto Alegre passou a ter duas unidades em 24/08/2026 e a cidade sozinha deixou
de dizer de quem é o cliente. Este arquivo guarda a divisão por bairro aprovada
por Felipe em 10/08/2026, com vigência a partir de setembro/2026.

O mapa decide PROSPECÇÃO, ROTEIRO DE VISITA e o território mostrado na ficha.
Ele NÃO decide faturamento: a venda continua contando para a unidade do
vendedor que a fez. Foi decisão do Felipe e é o que impede um vendedor de
faturar para a meta de outra unidade.

Para mudar a divisão, edite aqui ou pela tela Administração → Territórios.
Nomes são comparados sem acento e em maiúsculas, então a grafia do cadastro
do Alfa não precisa bater exatamente.
"""

# Vigência do MAPA DE TERRITÓRIO — não confundir com a vigência de resultado.
#
# Felipe definiu setembro/2026 para a nova divisão, para agosto fechar inteiro
# na estrutura atual. Essa decisão vale para o FATURAMENTO, que continua
# contando pela unidade do vendedor e não é tocado por este mapa.
#
# O território decide outra coisa: de quem é o cliente AINDA SEM VENDEDOR na
# carteira, para onde vai o prospect e como se agrupa o roteiro de visita.
# Segurar isso até setembro deixaria os vendedores da Zona Norte sem enxergar
# os clientes do bairro deles justamente nas semanas de montagem da carteira,
# antes da inauguração em 24/08. Por isso vale desde agosto.
TERRITORIO_VIGENCIA = "2026-08-01"

# Cidades atendidas por uma unidade só. Regra de cidade inteira, sem bairro.
CIDADES_EXCLUSIVAS = {
    "GRAVATAI": "ZONA NORTE",
    "ALVORADA": "ZONA NORTE",
    "CACHOEIRINHA": "ZONA NORTE",
}

# Cidades atendidas pelas duas unidades, DE PROPÓSITO sem mapa: quem define é o
# vendedor que já atende o cliente. Canoas é a maior das cinco em volume — é a
# primeira candidata a ganhar mapa próprio quando gerar atrito entre as equipes.
CIDADES_COMPARTILHADAS = ["CANOAS", "VIAMAO"]

# 50 bairros de Porto Alegre atendidos pela Zona Norte.
BAIRROS_ZONA_NORTE = [
    "ANCHIETA",
    "ARQUIPÉLAGO",
    "AUXILIADORA",  # fronteira decidida na revisão
    "BELA VISTA",  # fronteira decidida na revisão
    "BOA VISTA",
    "BOM FIM",  # fronteira decidida na revisão
    "BOM JESUS",  # fronteira decidida na revisão
    "CHÁCARA DAS PEDRAS",  # fronteira decidida na revisão
    "COSTA E SILVA",
    "CRISTO REDENTOR",
    "FARRAPOS",
    "FARROUPILHA",  # fronteira decidida na revisão
    "FLORESTA",  # fronteira decidida na revisão
    "HIGIENÓPOLIS",
    "HUMAITÁ",
    "INDEPENDÊNCIA",  # fronteira decidida na revisão
    "JARDIM CARVALHO",  # fronteira decidida na revisão
    "JARDIM DO SALSO",  # fronteira decidida na revisão
    "JARDIM EUROPA",  # fronteira decidida na revisão
    "JARDIM FLORESTA",
    "JARDIM ITU",
    "JARDIM LEOPOLDINA",
    "JARDIM LINDÓIA",
    "JARDIM SABARÁ",
    "JARDIM SÃO PEDRO",
    "MARCÍLIO DIAS",
    "MOINHOS DE VENTO",  # fronteira decidida na revisão
    "MONT'SERRAT",  # fronteira decidida na revisão
    "MORRO SANTANA",  # fronteira decidida na revisão
    "MÁRIO QUINTANA",
    "NAVEGANTES",
    "PARQUE SANTA FÉ",
    "PASSO DA AREIA",
    "PASSO DAS PEDRAS",
    "PETRÓPOLIS",  # fronteira decidida na revisão
    "PROTÁSIO ALVES",  # fronteira decidida na revisão
    "RIO BRANCO",  # fronteira decidida na revisão
    "RUBEM BERTA",
    "SANTA CECÍLIA",  # fronteira decidida na revisão
    "SANTA MARIA GORETTI",
    "SANTA ROSA DE LIMA",
    "SANTANA",  # fronteira decidida na revisão
    "SARANDI",
    "SÃO GERALDO",
    "SÃO JOÃO",
    "SÃO SEBASTIÃO",
    "TRÊS FIGUEIRAS",  # fronteira decidida na revisão
    "VILA IPIRANGA",
    "VILA JARDIM",
    "VILA JOÃO PESSOA",  # fronteira decidida na revisão
]

# 46 bairros de Porto Alegre atendidos pela Zona Sul.
BAIRROS_ZONA_SUL = [
    "ABERTA DOS MORROS",
    "AGRONOMIA",
    "AZENHA",
    "BELÉM NOVO",
    "BELÉM VELHO",
    "CAMAQUÃ",
    "CAMPO NOVO",
    "CASCATA",
    "CAVALHADA",
    "CENTRO HISTÓRICO",
    "CHAPÉU DO SOL",
    "CIDADE BAIXA",
    "CORONEL APARÍCIO BORGES",
    "CRISTAL",
    "ESPÍRITO SANTO",
    "EXTREMA",
    "GLÓRIA",
    "GUARUJÁ",
    "HÍPICA",
    "IPANEMA",
    "JARDIM BOTÂNICO",
    "JARDIM ISABEL",
    "LAGEADO",
    "LAMI",
    "LOMBA DO PINHEIRO",
    "MEDIANEIRA",
    "MENINO DEUS",
    "NONOAI",
    "PARTENON",
    "PEDRA REDONDA",
    "PITINGA",
    "PONTA GROSSA",
    "PRAIA DE BELAS",
    "RESTINGA",
    "SANTA TEREZA",
    "SANTO ANTÔNIO",
    "SERRARIA",
    "SÃO CAETANO",
    "SÃO JOSE",
    "SÉTIMO CÉU",
    "TERESÓPOLIS",
    "TRISTEZA",
    "VILA ASSUNÇÃO",
    "VILA CONCEIÇÃO",
    "VILA NOVA",
    "VILA SÃO JOSE",
]

BAIRROS_POA = {
    **{b: "ZONA NORTE" for b in BAIRROS_ZONA_NORTE},
    **{b: "ZONA SUL" for b in BAIRROS_ZONA_SUL},
}
