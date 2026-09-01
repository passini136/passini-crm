# Migração 2026 — marca e histórico completos

Estado apurado em 01/09/2026 pelo `diag_meses.py 2026`.

**Regra que explica tudo:** a marca faz parte da identidade da linha de venda.
Importar o relatório completo por cima de um mês sem marca não preenche nada —
duplica o mês. Por isso todo mês que já tem faturamento detalhado **sem marca**
precisa ser zerado antes. O sistema bloqueia se você esquecer.

O `--zerar-mes` apaga **só o faturamento detalhado**. Custo × venda, consolidado
e devoluções do mês continuam intactos.

---

## Ordem de trabalho

Um mês por vez, do início ao fim. Zerar vários de uma vez deixa buracos abertos.

### 1. Julho — o mais urgente

Está sem faturamento detalhado (foi zerado e não reimportado). Enquanto isso,
julho não aparece em nenhuma análise de cliente, marca ou item.

- [ ] Importar FAT DETALHADO de 01/07 a 31/07 — **não zerar, já está vazio**
- [ ] Conferir: `diag_meses.py 2026` → julho em "Completos"

### 2. Janeiro

- [ ] `limpar_import.py --zerar-mes 2026-01 --aplicar`
- [ ] Importar FAT DETALHADO de 01/01 a 31/01
- [ ] Importar CUSTO × VENDA (unidade e vendedor)
- [ ] Importar CONSOLIDADO POR CLIENTE
- [ ] Conferir: marca 100%, diferença perto de +6%

### 3. Fevereiro

- [ ] `limpar_import.py --zerar-mes 2026-02 --aplicar`
- [ ] Importar FAT DETALHADO de 01/02 a 28/02
- [ ] Importar CUSTO × VENDA (unidade e vendedor)
- [ ] Importar CONSOLIDADO POR CLIENTE
- [ ] Conferir

### 4. Março

- [ ] `limpar_import.py --zerar-mes 2026-03 --aplicar`
- [ ] Importar FAT DETALHADO de 01/03 a 31/03
- [ ] Importar CUSTO × VENDA (unidade e vendedor)
- [ ] Importar CONSOLIDADO POR CLIENTE
- [ ] Conferir

### 5. Abril

- [ ] `limpar_import.py --zerar-mes 2026-04 --aplicar`
- [ ] Importar FAT DETALHADO de 01/04 a 30/04
- [ ] Importar CONSOLIDADO POR CLIENTE
- [ ] Conferir

### 6. Maio

- [ ] `limpar_import.py --zerar-mes 2026-05 --aplicar`
- [ ] Importar FAT DETALHADO de 01/05 a 31/05
- [ ] Conferir

### Prontos, não mexer

- **Junho** — completo, marca 100%
- **Agosto** — completo, marca 100%
- **Devoluções** — já importadas de janeiro a agosto

---

## Como saber que deu certo

```bash
cd /srv/passini/apps/crm-comercial
/srv/passini/venv/crm/bin/python diag_meses.py 2026
```

O mês está certo quando aparece com:

- **1 importação** (veio de um relatório completo, não de diários somados)
- **marca 100%**
- **diferença de +6% a +7%** contra o custo × venda
- as quatro colunas marcadas: `DET CST CON DEV`

A diferença de 6% é normal e conhecida: o detalhado é venda bruta e o custo ×
venda desconta a devolução do mês. Não é erro.

## Se algo sair errado

- **A marca não subiu para 100%** — o mês não foi zerado. Zere e importe de novo.
- **O valor dobrou** — improvável, o sistema bloqueia. Se acontecer:
  `limpar_import.py --zerar-mes <mês> --aplicar` e importar de novo.
- **A importação foi recusada** — é a trava funcionando. A mensagem diz o
  comando exato para rodar.

Toda operação que apaga faz cópia de segurança sozinha em
`/srv/passini/data/crm/backups/`, e as 10 mais recentes ficam guardadas.
