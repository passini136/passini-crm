# Backlog Tecnico - CRM Passini

## Objetivo
Traduzir a especificacao funcional em entregas tecnicas executaveis para desenvolvimento do MVP.

## Ordem de execucao recomendada
1. Fundacao tecnica
2. Importacao e consolidacao de dados
3. Autenticacao e perfis
4. Cliente 360 e carteira
5. Agenda inteligente
6. Registro de interacoes e follow-up
7. Painel do vendedor
8. Painel gerencial
9. Ranking e gamificacao
10. Parametrizacao administrativa

## EPIC 1 - Fundacao tecnica

### Historia 1.1
Como time tecnico, quero estruturar a base do projeto para suportar modulos, autenticacao, importacao e dashboards.

Tarefas:
- definir stack final do MVP
- estruturar pastas backend/frontend
- criar arquivo de configuracoes por ambiente
- configurar ORM/migracoes
- configurar logs
- configurar tratamento padrao de erros
- configurar base inicial de rotas/API

Criterios de aceite:
- projeto sobe localmente
- banco inicial criado via migracao
- padrao de logs e erros funcionando

### Historia 1.2
Como time tecnico, quero preparar design system minimo para uso consistente nas telas.

Tarefas:
- definir tokens visuais
- criar componentes base
- criar layout responsivo principal
- criar tabela, card, modal, filtro e formulario padrao

Criterios de aceite:
- componentes base reutilizaveis disponiveis
- responsividade base validada

## EPIC 2 - Importacao e consolidacao de dados

### Historia 2.1
Como administrador, quero importar a base de vendas para alimentar historico, carteira e indicadores.

Tarefas:
- criar parser da base `base vendas faturamento`
- mapear colunas para `compra` e `compra_item`
- tratar duplicidade de carga
- registrar lote e log de importacao
- validar chaves de cliente, vendedor e unidade

Criterios de aceite:
- carga cria compras e itens corretamente
- duplicidade controlada
- erros ficam registrados em log

### Historia 2.2
Como administrador, quero importar a base `CARTEIRA DE CLIENTES` para gerar cadastro enriquecido e snapshot diario.

Tarefas:
- mapear colunas da carteira
- alimentar `cliente`
- alimentar `carteira_cliente`
- alimentar `cliente_classificacao`
- alimentar `cliente_snapshot_metricas`
- tratar campos de classe, status, alerta, faturamento e medias

Criterios de aceite:
- cadastro e snapshot ficam coerentes com a base original
- classe e status conferem com o Excel

### Historia 2.3
Como administrador, quero importar dados do `PAINEL` para validar indicadores gerenciais.

Tarefas:
- mapear consolidado por unidade
- mapear consolidado por vendedor
- comparar com snapshots calculados
- criar rotina de reconciliacao

Criterios de aceite:
- totais batem com tolerancia definida

### Historia 2.4
Como sistema, quero executar importacao automatica diaria D-1 e manual de contingencia.

Tarefas:
- criar job agendado
- criar tela/upload manual
- criar reprocessamento de lote
- criar status da ultima carga

Criterios de aceite:
- importacao automatica executa diariamente
- contingencia manual funciona

## EPIC 3 - Autenticacao e perfis

### Historia 3.1
Como usuario, quero autenticar no sistema para acessar minha area.

Tarefas:
- login
- logout
- sessao/token
- recuperacao de acesso

Criterios de aceite:
- usuario entra com seguranca
- sessao expira corretamente

### Historia 3.2
Como sistema, quero aplicar perfis e permissoes por papel.

Tarefas:
- middleware/autorizacao
- regras de acesso vendedor/gerente/admin
- controle de rotas
- controle de acoes na API

Criterios de aceite:
- vendedor nao acessa dados indevidos
- gerente enxerga equipe
- admin enxerga tudo

## EPIC 4 - Cliente 360 e carteira

### Historia 4.1
Como vendedor, quero listar meus clientes com filtros comerciais.

Tarefas:
- endpoint de listagem
- filtros por status, classe, unidade, segmento, queda, compra no mes
- busca por nome, documento, codigo
- ordenacao por prioridade

Criterios de aceite:
- lista responde rapido
- filtros funcionam em desktop e mobile

### Historia 4.2
Como vendedor, quero abrir a ficha 360 do cliente para entender historico e proximo passo.

Tarefas:
- endpoint resumo do cliente
- endpoint historico de compras
- endpoint ultimos itens/pedidos
- endpoint mix e oportunidades
- endpoint historico de interacoes
- endpoint tarefas do cliente

Criterios de aceite:
- ficha mostra resumo completo
- blocos carregam separadamente sem travar a tela

### Historia 4.3
Como gerente, quero enxergar carteira por vendedor e unidade.

Tarefas:
- tela consolidada de carteiras
- filtros por vendedor/unidade/status/classe
- totais e contagens

Criterios de aceite:
- gerente navega entre vendedor e cliente facilmente

## EPIC 5 - Agenda inteligente

### Historia 5.1
Como sistema, quero gerar a agenda diaria do vendedor com TOP 5 e fila estendida.

Tarefas:
- implementar regra de priorizacao
- materializar `agenda_diaria`
- materializar `agenda_item`
- distinguir `TOP5` e `ESTENDIDA`
- guardar motivo principal e secundarios

Criterios de aceite:
- agenda respeita ordem de prioridade definida
- TOP 5 e fila estendida sao gerados corretamente

### Historia 5.2
Como vendedor, quero visualizar cards de agenda com contexto completo.

Tarefas:
- endpoint da agenda do dia
- card com classe, status, ultima compra, dias sem compra
- motivo principal e secundarios
- oferta principal
- pergunta principal

Criterios de aceite:
- card entrega contexto suficiente para agir

### Historia 5.3
Como vendedor, quero adiar ou reordenar itens com justificativa obrigatoria.

Tarefas:
- modal de justificativa
- persistencia de justificativa
- auditoria da alteracao
- reordenacao da fila

Criterios de aceite:
- sistema nao permite concluir a acao sem justificativa

### Historia 5.4
Como sistema, quero repor automaticamente o TOP 5 ao concluir um contato.

Tarefas:
- detectar conclusao elegivel
- promover item da fila estendida
- recalcular ordem visual

Criterios de aceite:
- TOP 5 permanece com 5 itens ativos quando houver fila disponivel

## EPIC 6 - Recomendacoes e perguntas sugeridas

### Historia 6.1
Como sistema, quero gerar recomendacoes comerciais por cliente.

Tarefas:
- regra de recompra
- regra de complementaridade
- regra de linha estrategica
- regra por segmento
- priorizacao das recomendacoes

Criterios de aceite:
- cliente recebe 1 oferta principal e ate 3 secundarias
- motivo da sugestao sempre presente

### Historia 6.2
Como sistema, quero sugerir perguntas dinamicas para o contato.

Tarefas:
- motor simples por contexto
- vinculo com status/historico/linha/segmento/objetivo
- retorno de 1 principal e ate 3 de apoio

Criterios de aceite:
- perguntas mudam conforme contexto do cliente

## EPIC 7 - Registro de interacoes e follow-up

### Historia 7.1
Como vendedor, quero registrar um contato de forma rapida.

Tarefas:
- formulario de registro
- validacao de campos obrigatorios
- tipos de contato
- resultados de contato
- salvar observacao obrigatoria

Criterios de aceite:
- vendedor registra contato com poucos passos

### Historia 7.2
Como vendedor, quero marcar pergunta utilizada e se houve avanço.

Tarefas:
- campo pergunta utilizada
- campo houve avancao
- persistencia no historico

Criterios de aceite:
- dado fica vinculado a interacao

### Historia 7.3
Como sistema, quero criar follow-up automatico conforme resultado.

Tarefas:
- regras para `pediu retorno`
- regras para `gerou orcamento`
- regras para `falou com cliente + proxima acao`
- regras para `nao atendeu`

Criterios de aceite:
- tarefa nasce automaticamente quando a regra exigir

### Historia 7.4
Como vendedor, quero visualizar e concluir tarefas/retornos.

Tarefas:
- tela de tarefas
- filtro por hoje/atrasadas/proximas/concluidas
- concluir
- reagendar
- abrir cliente

Criterios de aceite:
- vendedor consegue trabalhar fila de retornos separadamente

## EPIC 8 - Painel do vendedor

### Historia 8.1
Como vendedor, quero ver meus KPIs diarios e de periodo.

Tarefas:
- score do dia
- ranking
- contatos
- contatos com sucesso
- orcamentos
- pedidos
- reativacoes
- execucao TOP 5
- tarefas abertas/atrasadas

Criterios de aceite:
- painel abre com dados do usuario logado

### Historia 8.2
Como vendedor, quero visualizar graficos de evolucao.

Tarefas:
- contatos por dia
- score por dia
- reativacoes por periodo
- execucao de missoes

Criterios de aceite:
- graficos carregam com performance adequada

## EPIC 9 - Painel gerencial

### Historia 9.1
Como gerente, quero acompanhar indicadores da equipe.

Tarefas:
- KPIs consolidados por unidade
- KPIs por vendedor
- execucao do TOP 5
- reativacoes
- positivacao
- carteira por status e classe

Criterios de aceite:
- gerente enxerga time e consegue filtrar por unidade e periodo

### Historia 9.2
Como gerente, quero auditar justificativas e baixa execucao.

Tarefas:
- tela de justificativas recentes
- ranking de adiamentos/reordenacoes
- clientes criticos sem contato
- retornos vencidos por vendedor

Criterios de aceite:
- gargalos ficam identificaveis em uma unica tela

## EPIC 10 - Ranking e gamificacao

### Historia 10.1
Como sistema, quero pontuar acoes comerciais com score ponderado.

Tarefas:
- parametrizar pesos
- gerar `pontuacao_evento`
- consolidar `score_diario_vendedor`

Criterios de aceite:
- score reflete eventos comerciais definidos

### Historia 10.2
Como vendedor, quero ver ranking diario, semanal e mensal.

Tarefas:
- consolidacao por periodo
- tela de ranking
- destaque da posicao do usuario

Criterios de aceite:
- ranking ordena corretamente

### Historia 10.3
Como sistema, quero gerar missoes, conquistas e niveis.

Tarefas:
- catalogo de missoes
- instancia por vendedor
- progresso
- conclusao
- bonus de pontuacao
- conquistas e niveis

Criterios de aceite:
- vendedor ve progresso e historico de conquistas

## EPIC 11 - Parametros administrativos

### Historia 11.1
Como administrador, quero manter regras e catalogos do sistema.

Tarefas:
- CRUD tipos de contato
- CRUD resultados
- CRUD motivos de justificativa
- CRUD regras de pontuacao
- CRUD linhas estrategicas
- CRUD missoes

Criterios de aceite:
- alteracoes de parametro refletem no comportamento do sistema

## APIs recomendadas
- `POST /auth/login`
- `GET /me`
- `GET /dashboard/vendedor`
- `GET /agenda/hoje`
- `POST /agenda/item/{id}/adiar`
- `POST /agenda/item/{id}/reordenar`
- `POST /agenda/item/{id}/concluir`
- `GET /clientes`
- `GET /clientes/{id}/resumo`
- `GET /clientes/{id}/compras`
- `GET /clientes/{id}/mix`
- `GET /clientes/{id}/interacoes`
- `GET /clientes/{id}/tarefas`
- `POST /interacoes`
- `GET /tarefas`
- `POST /tarefas/{id}/concluir`
- `POST /tarefas/{id}/reagendar`
- `GET /ranking`
- `GET /gamificacao`
- `GET /gerencial/dashboard`
- `GET /gerencial/equipe`
- `POST /importacoes`
- `GET /importacoes`

## Dependencias criticas
- importacao concluida antes da agenda
- agenda depende de snapshot consolidado
- ficha 360 depende de compras e carteira
- ranking depende de interacoes e eventos de score
- painel gerencial depende de consolidacoes diarias

## Ordem recomendada de sprints

### Sprint 1
- fundacao tecnica
- banco e migracoes
- autenticacao
- importacao manual inicial

### Sprint 2
- carteira/lista de clientes
- ficha 360 resumo
- historico de compras

### Sprint 3
- agenda inteligente
- recomendacoes
- perguntas sugeridas

### Sprint 4
- registro de interacoes
- follow-up automatico
- tarefas e retornos

### Sprint 5
- painel do vendedor
- painel gerencial inicial

### Sprint 6
- ranking
- gamificacao
- parametros administrativos

## Riscos tecnicos
- qualidade e padronizacao da base de importacao
- correspondencia entre cliente da carteira e cliente da venda
- deduplicacao de pedidos/importacoes
- latencia se consultas usarem base transacional crua sem snapshots
- clareza das regras de recomendacao de mix na fase 1

## Mitigacoes
- usar snapshots diarios
- manter log detalhado de importacao
- validar regras com amostras reais da carteira
- parametrizar pesos e regras desde o inicio
