# Dashboard Comercial Passini

Aplicação local em navegador para gestão comercial da Passini Distribuidora de Autopeças.

## O que já está pronto

- login com usuário e senha protegida por hash
- banco local `sqlite`
- importação do pacote completo de CSVs
- sugestão automática de competência com confirmação manual
- histórico de importações com auditoria
- dashboard executivo com:
  - faturamento líquido
  - meta x realizado
  - devolução
  - ticket médio
  - clientes distintos
  - desconto em R$ e %
  - margem
  - projeção por dias úteis
  - top 10 vendedores
  - quadrante meta x score
  - comparativo com competência anterior e ano anterior
- ranking completo de vendedores
- ranking por cidade
- calendário comercial
- área administrativa com cadastros, pendências, importações e auditoria
- exportação para Excel e PDF

## Login inicial

- usuário: `admin`
- senha: definida no primeiro acesso / fornecida em separado (não versionar credenciais no repositório)

## Como rodar

1. Execute `start_dashboard.bat`
2. O servidor vai abrir em uma janela separada e o navegador sera aberto automaticamente em `http://127.0.0.1:8876`

## Observações da V1

- o sistema já semeia a planilha de apoio `UNIDADE X VENDEDOR E CIDADE X UNIDADE.xlsx` se ela existir no caminho configurado
- existe um botão `Carregar exemplo Passini` para importar rapidamente os arquivos reais já encontrados em `Downloads`
- a importação oficial exige os 3 arquivos do pacote diário

## Estrutura

- `backend.py`: servidor local, banco, autenticação, importações e APIs
- `static/index.html`: shell principal
- `static/styles.css`: identidade visual
- `static/app.js`: dashboard e telas administrativas

## Armazenamento local

- o banco `sqlite` fica em `%LOCALAPPDATA%\PassiniDashboard\passini_dashboard.db`
- isso evita problemas de gravação do `sqlite` em pastas sincronizadas pelo OneDrive
