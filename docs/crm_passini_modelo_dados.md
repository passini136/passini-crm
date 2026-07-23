# Modelo de Dados - CRM Passini

## Visao geral
O modelo foi estruturado para suportar:
- agenda inteligente do vendedor
- ficha 360 do cliente
- historico de compras por item/SKU
- recomendacoes comerciais
- registro de interacoes e follow-ups
- ranking, missões e gamificacao
- visao gerencial por vendedor, unidade, carteira, classe e status

## Principios de modelagem
- `compra` e `compra_item` preservam granularidade transacional
- `cliente_snapshot_metricas` concentra indicadores diarios em D-1 para resposta rapida
- `interacao` e `tarefa_followup` sustentam a operacao comercial
- `agenda_item` materializa a fila diaria do vendedor e sua auditabilidade
- tabelas de parametro mantem regras comerciais ajustaveis sem reescrever o sistema

## Entidades principais

### unidade
Representa filial ou carteira-unidade.

Campos:
- `id`
- `codigo`
- `nome`
- `ativo`
- `created_at`
- `updated_at`

### usuario
Conta de acesso ao sistema.

Campos:
- `id`
- `nome`
- `email`
- `login`
- `senha_hash`
- `perfil_id`
- `unidade_id`
- `ativo`
- `ultimo_login_at`
- `created_at`
- `updated_at`

### perfil
Perfis de acesso.

Campos:
- `id`
- `codigo` (`VENDEDOR`, `GERENTE`, `ADMIN`)
- `nome`
- `descricao`

### vendedor
Extensao operacional do usuario.

Campos:
- `id`
- `usuario_id`
- `codigo_externo`
- `nome_exibicao`
- `tipo_vendedor` (`VENDAS`, `TELEVENDAS`, `EXTERNO`)
- `unidade_id`
- `gestor_id`
- `ativo`
- `created_at`
- `updated_at`

### segmento
Grupo economico/segmento comercial do cliente.

Campos:
- `id`
- `codigo`
- `nome`
- `descricao`
- `ativo`

### cliente
Cadastro mestre do cliente.

Campos:
- `id`
- `codigo_externo`
- `razao_social`
- `nome_fantasia`
- `documento`
- `tipo_pessoa` (`PF`, `PJ`)
- `ie`
- `telefone_principal`
- `email_principal`
- `logradouro`
- `numero`
- `bairro`
- `cidade`
- `uf`
- `cep`
- `segmento_id`
- `limite_credito`
- `situacao_limite` (`C_LIMITE`, `S_LIMITE`, etc.)
- `forma_pagamento_preferencial`
- `preferencia_entrega`
- `primeira_venda_at`
- `ultima_venda_at`
- `ativo`
- `created_at`
- `updated_at`

### carteira_cliente
Historico de atribuicao do cliente a vendedor e unidade.

Campos:
- `id`
- `cliente_id`
- `vendedor_id`
- `unidade_id`
- `origem` (`IMPORTACAO`, `MANUAL`, `TROCA_GERENCIAL`)
- `inicio_at`
- `fim_at`
- `ativo`
- `motivo_alteracao`
- `created_at`
- `updated_at`

### cliente_classificacao
Snapshot diario de classe, status e indicadores-base.

Campos:
- `id`
- `cliente_id`
- `data_referencia`
- `classe_cliente_id`
- `status_cliente_id`
- `compra_no_mes`
- `dias_sem_compra`
- `ultima_compra_at`
- `media_ultimos_3_meses`
- `faturamento_mes_atual`
- `media_mes_ano_anterior`
- `variacao_mes_vs_trimestre_pct`
- `alerta_queda_id`
- `contagem_vendas_inativos`
- `periodo_cadastro`
- `created_at`

### classe_cliente
Faixa de classificacao comercial.

Campos:
- `id`
- `codigo`
- `nome` (`DIAMANTE`, `OURO`, `PRATA`, `BRONZE`, `NAO_CLASSIFICADO`)
- `faturamento_min`
- `faturamento_max`
- `ordem`
- `ativo`

### status_cliente
Status operacional do cliente.

Campos:
- `id`
- `codigo`
- `nome` (`ATIVO`, `PRE_INATIVO`, `INATIVO`)
- `dias_min`
- `dias_max`
- `ordem`
- `ativo`

### alerta_queda
Classificacao de queda de faturamento.

Campos:
- `id`
- `codigo`
- `nome`
- `variacao_min_pct`
- `variacao_max_pct`
- `prioridade_visual`
- `ativo`

### cliente_snapshot_metricas
Materializacao diaria de metricas detalhadas para agenda, ficha e dashboards.

Campos:
- `id`
- `cliente_id`
- `data_referencia`
- `vendedor_id`
- `unidade_id`
- `faturamento_jan`
- `faturamento_fev`
- `faturamento_mar`
- `faturamento_mes_atual`
- `media_trimestre`
- `media_ano_anterior`
- `variacao_trimestre_pct`
- `variacao_ano_pct`
- `qtd_pedidos_ultimos_90_dias`
- `qtd_itens_ultimos_90_dias`
- `qtd_skus_ultimos_90_dias`
- `ticket_medio_ultimos_90_dias`
- `classe_cliente_id`
- `status_cliente_id`
- `alerta_queda_id`
- `compra_no_mes`
- `dias_sem_compra`
- `tem_oportunidade_mix`
- `tem_reativacao`
- `tem_oportunidade_recompra`
- `prioridade_base`
- `created_at`

### compra
Cabecalho do pedido/faturamento.

Campos:
- `id`
- `origem_importacao_id`
- `pedido_externo_id`
- `cliente_id`
- `vendedor_id`
- `unidade_id`
- `data_compra_at`
- `valor_bruto`
- `valor_desconto`
- `valor_frete`
- `valor_devolucao`
- `valor_liquido`
- `qtd_itens`
- `qtd_total`
- `created_at`

### compra_item
Linha de item vendido.

Campos:
- `id`
- `compra_id`
- `produto_id`
- `sku_id`
- `marca_id`
- `referencia_fornecedor`
- `referencia_antiga`
- `codigo_fabricante`
- `quantidade`
- `valor_bruto`
- `valor_desconto`
- `valor_devolucao`
- `valor_liquido`
- `percentual_venda`
- `created_at`

### produto
Cadastro canonico de produto.

Campos:
- `id`
- `codigo_externo`
- `descricao`
- `linha_produto_id`
- `marca_id`
- `fabricante`
- `ativo`
- `created_at`
- `updated_at`

### sku
SKU vendavel, relacionado ao produto.

Campos:
- `id`
- `produto_id`
- `codigo_sku`
- `descricao_sku`
- `ativo`
- `created_at`
- `updated_at`

### linha_produto
Linha comercial para recomendacao e mix.

Campos:
- `id`
- `codigo`
- `nome`
- `estrategica`
- `ativo`

### marca
Marca do item.

Campos:
- `id`
- `codigo`
- `nome`
- `ativo`

## Operacao comercial

### agenda_diaria
Cabecalho da agenda do vendedor em cada dia.

Campos:
- `id`
- `data_agenda`
- `vendedor_id`
- `status` (`ABERTA`, `EM_EXECUCAO`, `FINALIZADA`)
- `top5_meta`
- `fila_estendida_meta`
- `created_at`
- `updated_at`

### agenda_item
Fila operacional materializada.

Campos:
- `id`
- `agenda_diaria_id`
- `cliente_id`
- `ordem_exibicao`
- `grupo_fila` (`TOP5`, `ESTENDIDA`)
- `motivo_principal_id`
- `motivos_secundarios_json`
- `oferta_principal_id`
- `ofertas_secundarias_json`
- `pergunta_principal_id`
- `perguntas_apoio_json`
- `proximo_passo_sugerido`
- `status_execucao` (`PENDENTE`, `EM_ANDAMENTO`, `CONCLUIDO`, `ADIADO`, `REORDENADO`, `DESCARTADO`)
- `justificativa_id`
- `justificativa_texto`
- `reposto_automaticamente`
- `concluido_at`
- `created_at`
- `updated_at`

### motivo_prioridade
Catalogo de motivos da agenda.

Campos:
- `id`
- `codigo`
- `nome`
- `descricao`
- `ordem_prioridade`
- `ativo`

### recomendacao_oferta
Recomendacao por cliente e data de referencia.

Campos:
- `id`
- `cliente_id`
- `data_referencia`
- `tipo_recomendacao` (`RECOMPRA`, `COMPLEMENTAR`, `LINHA_ESTRATEGICA`, `SEGMENTO`)
- `produto_id`
- `linha_produto_id`
- `prioridade`
- `titulo_exibicao`
- `motivo_recomendacao`
- `principal`
- `ativo`
- `created_at`

### pergunta_sugerida
Perguntas sugeridas por contexto.

Campos:
- `id`
- `codigo`
- `tipo_contexto` (`STATUS`, `HISTORICO`, `LINHA`, `SEGMENTO`, `OBJETIVO`)
- `texto`
- `principal`
- `ativo`

### pergunta_sugerida_execucao
Ligacao entre agenda e perguntas apresentadas.

Campos:
- `id`
- `agenda_item_id`
- `pergunta_sugerida_id`
- `ordem`
- `principal`

### interacao
Registro comercial principal.

Campos:
- `id`
- `cliente_id`
- `vendedor_id`
- `agenda_item_id`
- `tarefa_followup_origem_id`
- `tipo_interacao_id`
- `resultado_interacao_id`
- `ocorreu_at`
- `observacao`
- `pergunta_utilizada_id`
- `houve_avanco`
- `oferta_principal_id`
- `proxima_acao`
- `data_retorno_prevista`
- `gerou_followup_automatico`
- `created_at`
- `updated_at`

### tipo_interacao
Campos:
- `id`
- `codigo`
- `nome` (`LIGACAO`, `WHATSAPP`, `VISITA`, `ORCAMENTO`, `OUTRO`)
- `ativo`

### resultado_interacao
Campos:
- `id`
- `codigo`
- `nome`
- `gera_followup_automatico`
- `exige_data_retorno`
- `ativo`

### tarefa_followup
Tarefa comercial derivada de interacao ou agenda.

Campos:
- `id`
- `cliente_id`
- `vendedor_id`
- `interacao_origem_id`
- `tipo_tarefa` (`RETORNO`, `REAGENDAMENTO`, `NOVA_TENTATIVA`, `FOLLOWUP_ORCAMENTO`)
- `titulo`
- `descricao`
- `prioridade`
- `prevista_para_at`
- `status` (`ABERTA`, `CONCLUIDA`, `ATRASADA`, `CANCELADA`, `REAGENDADA`)
- `concluida_at`
- `reagendada_de_id`
- `created_at`
- `updated_at`

## Gamificacao e performance

### regra_pontuacao
Parametros de score.

Campos:
- `id`
- `codigo_acao`
- `descricao`
- `pontuacao`
- `ativo`
- `vigencia_inicio_at`
- `vigencia_fim_at`

### pontuacao_evento
Eventos pontuaveis gerados pelo sistema.

Campos:
- `id`
- `vendedor_id`
- `cliente_id`
- `interacao_id`
- `agenda_item_id`
- `codigo_acao`
- `pontuacao`
- `data_evento`
- `referencia_tipo`
- `referencia_id`
- `created_at`

### score_diario_vendedor
Consolidado diario.

Campos:
- `id`
- `data_referencia`
- `vendedor_id`
- `pontuacao_total`
- `contatos_registrados`
- `contatos_com_sucesso`
- `orcamentos_gerados`
- `pedidos_gerados`
- `clientes_reativados`
- `contatos_top5_concluidos`
- `tarefas_no_prazo_concluidas`
- `created_at`

### missao
Catalogo de missoes.

Campos:
- `id`
- `codigo`
- `nome`
- `descricao`
- `tipo_missao` (`DIARIA`, `SEMANAL`)
- `padrao_global`
- `dinamica_contextual`
- `criterio_json`
- `pontuacao_bonus`
- `ativo`

### missao_vendedor
Missoes instanciadas por vendedor e periodo.

Campos:
- `id`
- `missao_id`
- `vendedor_id`
- `data_inicio`
- `data_fim`
- `meta`
- `progresso`
- `concluida`
- `concluida_at`
- `created_at`

### conquista
Catalogo de medalhas e badges.

Campos:
- `id`
- `codigo`
- `nome`
- `descricao`
- `icone`
- `criterio_json`
- `ativo`

### conquista_vendedor
Campos:
- `id`
- `conquista_id`
- `vendedor_id`
- `conquistada_at`
- `observacao`

### nivel_vendedor
Campos:
- `id`
- `codigo`
- `nome`
- `pontuacao_minima`
- `pontuacao_maxima`
- `ativo`

## Gestao e auditoria

### justificativa_tipo
Motivos obrigatorios de adiamento/reordenacao.

Campos:
- `id`
- `codigo`
- `nome`
- `tipo_uso` (`ADIAMENTO`, `REORDENACAO`, `AMBOS`)
- `ativo`

### auditoria_execucao
Eventos auditaveis relevantes.

Campos:
- `id`
- `usuario_id`
- `entidade`
- `entidade_id`
- `acao`
- `valor_anterior_json`
- `valor_novo_json`
- `ocorreu_at`

## Importacao

### importacao_lote
Cabecalho de carga.

Campos:
- `id`
- `tipo_importacao` (`VENDAS`, `CARTEIRA`, `PAINEL`)
- `arquivo_nome`
- `arquivo_hash`
- `data_referencia`
- `origem`
- `status` (`PROCESSANDO`, `CONCLUIDA`, `COM_ERRO`)
- `iniciada_at`
- `finalizada_at`
- `usuario_execucao_id`
- `observacao`

### importacao_log
Linhas de log da carga.

Campos:
- `id`
- `importacao_lote_id`
- `nivel` (`INFO`, `WARN`, `ERROR`)
- `linha_origem`
- `mensagem`
- `payload_json`
- `created_at`

## Relacionamentos principais
- `perfil 1:N usuario`
- `usuario 1:1 vendedor`
- `unidade 1:N vendedor`
- `segmento 1:N cliente`
- `cliente 1:N carteira_cliente`
- `vendedor 1:N carteira_cliente`
- `cliente 1:N cliente_classificacao`
- `cliente 1:N cliente_snapshot_metricas`
- `cliente 1:N compra`
- `compra 1:N compra_item`
- `produto 1:N sku`
- `linha_produto 1:N produto`
- `marca 1:N produto`
- `vendedor 1:N agenda_diaria`
- `agenda_diaria 1:N agenda_item`
- `cliente 1:N agenda_item`
- `cliente 1:N recomendacao_oferta`
- `cliente 1:N interacao`
- `vendedor 1:N interacao`
- `interacao 1:N tarefa_followup`
- `vendedor 1:N pontuacao_evento`
- `vendedor 1:N score_diario_vendedor`
- `vendedor 1:N missao_vendedor`
- `vendedor 1:N conquista_vendedor`

## Views materializadas recomendadas
- `vw_cliente_360_atual`
- `vw_agenda_priorizada_vendedor`
- `vw_painel_vendedor_diario`
- `vw_painel_gerencial_unidade`
- `vw_mix_cliente_atual`
- `vw_oportunidade_recompra`
- `vw_clientes_reativados_periodo`

## Regras de derivacao recomendadas
- classe do cliente calculada diariamente pela media dos ultimos 3 meses
- status do cliente calculado por dias sem compra
- alerta de queda calculado por comparacao entre mes atual e media trimestral
- oportunidade de recompra baseada em SKUs/linhas ja comprados e ausentes em janela recente
- oportunidade complementar baseada em matriz de linhas associadas
- agenda diaria gerada em D-1 apos carga
- score diario consolidado a partir de `pontuacao_evento`

## Chaves e indices recomendados
- indice unico em `cliente.codigo_externo`
- indice em `cliente.documento`
- indice em `carteira_cliente(cliente_id, ativo)`
- indice em `cliente_snapshot_metricas(data_referencia, vendedor_id, prioridade_base)`
- indice em `compra(cliente_id, data_compra_at)`
- indice em `compra_item(produto_id, sku_id)`
- indice em `interacao(cliente_id, ocorreu_at desc)`
- indice em `tarefa_followup(vendedor_id, status, prevista_para_at)`
- indice em `agenda_item(agenda_diaria_id, grupo_fila, ordem_exibicao)`
- indice em `pontuacao_evento(vendedor_id, data_evento)`

## Observacoes de implementacao
- `cliente_snapshot_metricas` deve ser a principal fonte da agenda e dashboards
- `agenda_item` nao deve ser recalculada em tempo real apos o vendedor comecar a operar; a reposicao deve respeitar auditabilidade
- `interacao.observacao` e obrigatoria por regra de negocio
- `motivos_secundarios_json`, `ofertas_secundarias_json` e `perguntas_apoio_json` podem nascer como JSON no MVP e evoluir para tabelas dedicadas depois
- a importacao inicial deve suportar processo automatico e manual de contingencia
