# Requisitos e critérios de aceite — relatórios

| ID | Requisito | Critério de aceite | Evidência |
|---|---|---|---|
| RF01 | Consolidar produção por período | Somar pesos com Decimal e batidas inteiras, com filtro inclusivo | Testes de totais/filtro e comparação CSV/XLSX |
| RF02 | Detectar entradas inválidas | Rejeitar cabeçalhos, datas, vazios, negativos e números inválidos com linha do erro | Testes CSV e XLSX |
| RF08 | Importar XLSX | Mesmas validações e totais que CSV; aceitar datas Excel e preservar HTML/JSON | 21 testes XLSX/integração e exemplo fictício |
| RF12 | Exportar relatório | HTML com escape, pesos/totais e JSON com kg decimal textual | Testes de exportação e equivalência das saídas |

RF08 implementado na branch do PR associado à [issue #2](https://github.com/DiogoLazzarotto/DiogoLazzarotto/issues/2).
Os testes automatizados de aceite estão aprovados; a integração em `main` depende do merge do PR.

## Regras e limites

Pesos são informados; não inferir kg por batida. Categorias auxiliares usam kg=0;
Recebimentos usam batidas=0. Somar duplicatas por categoria/produto, pois não há ID de lançamento.
CSV e XLSX usam validador comum. XLSX lê apenas a primeira aba e rejeita fórmulas/erros de célula.
Os dados são fictícios, sem validação com usuários ou indicadores reais de produtividade.

## Backlog

- Identificadores de lançamento para detectar duplicatas.
- Seleção explícita de aba XLSX, se necessária.
- Configurar CI para executar a suíte em Python 3.11 e 3.12.
