# Proposta de importação XLSX — issue #2

Referência: [DiogoLazzarotto/DiogoLazzarotto#2](https://github.com/DiogoLazzarotto/DiogoLazzarotto/issues/2).
Base examinada: `efb79896dab99403c3796011b12d99350b7a85e1`, em 30/09/2026.

## Situação desta entrega

Esta entrega prepara análise, contrato de comportamento, gerador de exemplo e testes de aceite.
**O leitor XLSX não foi implementado.** Não executar a CLI com XLSX esperando sucesso nesta versão.
Os critérios da issue permanecem pendentes; os testes de aceite são deliberadamente vermelhos.
O rascunho deve ser completado com a implementação antes de merge.

## Estrutura e diagnóstico

O projeto é pequeno: `src/report.py` concentra `number`, `load`, `summarize`, `export` e a CLI.
`load` usa `csv.DictReader`, valida cabeçalhos em ordem exata e todas as linhas antes do filtro.
O peso é `Decimal`, as batidas são inteiras e a consolidação soma duplicatas por categoria/produto.
`summarize` recebe datas Python e mantém pesos decimais. `export` grava kg como string em JSON
e escapa título/produtos no HTML. Essas duas funções não precisam mudar para XLSX.

Os cinco testes existentes cobrem totais/filtro, números inválidos, soma decimal/escape HTML,
período invertido e batidas fracionadas. Faltam testes dedicados de cabeçalhos, células vazias,
datas Excel e equivalência entre formatos. Não há manifesto de dependências ou CI na árvore examinada.
Os documentos atuais de requisitos/validação também contêm dados de outros projetos do portfólio;
o novo relatório de validação deve distinguir a evidência específica deste projeto.

## Arquivos da implementação proposta

| Arquivo | Mudança |
|---|---|
| `src/report.py` | Transformar `load(path)` em dispatcher por extensão; extrair leitores e validador comum; adaptar tipos Excel; atualizar descrição/argumento da CLI e erros |
| `requirements-xlsx.txt` | Dependência opcional XLSX: `openpyxl==3.1.5`; já preparada neste rascunho |
| `README.md` | Documentar instalação opcional, comandos XLSX, regras de primeira aba/datas/fórmulas/precisão; retirar “não lê XLSX” somente após implementação |
| `tests/test_report.py` | Manter cinco regressões e acrescentar validação CSV compartilhada quando o validador for extraído |
| `tests/acceptance/test_xlsx.py` | 16 testes executáveis de aceite já preparados; integrar à execução padrão ao implementar |
| `examples/gerar_xlsx.py` | Gerador já preparado, usando o CSV fictício existente; gera `examples/producao.xlsx` |
| `examples/producao.xlsx` | Exemplo fictício já gerado e incluído; contém os mesmos nove lançamentos do CSV |
| `docs/REQUISITOS.md` | Atualizar RF08 e vincular evidências após os testes passarem |
| `docs/VALIDACAO.md` | Registrar ambiente, comandos, resultados deste projeto e limitações reais |

## Desenho proposto

1. Preservar a assinatura pública `load(path)`; selecionar `.csv` ou `.xlsx` com extensão em minúsculas.
   Rejeitar demais extensões com mensagem clara. Não adicionar suporte a XLS/XLSM implicitamente.
2. Extrair `_load_csv` mantendo UTF-8/BOM, separador `;`, ordem dos campos e números de linha atuais.
3. Criar `_load_xlsx` com importação tardia de `openpyxl`, para CSV continuar sem pacotes externos.
   Usar `load_workbook(path, read_only=True, data_only=False, keep_links=False)` e fechar o workbook
   em `finally`, inclusive se uma linha falhar. Ler a primeira worksheet na ordem do arquivo,
   independentemente da aba ativa. A seleção de outras abas fica fora deste escopo inicial.
4. Usar um validador comum por linha, por exemplo `_validate_row(values, line)`, que retorne o
   mesmo dicionário atual: `data: date`, `categoria/produto: str`, `batidas: int`, `kg: Decimal`.
   A validação comum deve manter regras de categoria, batidas inteiras, pesos e finitude.
5. Manter `summarize` e `export`: validar toda a entrada antes do filtro; exportar apenas após sucesso.
   Renomear o argumento interno da CLI de `csv` para `input` sem mudar a forma de invocação.
6. Traduzir erros de arquivo XLSX inválido/ZIP/XML para `ValueError` com causa útil e sem traceback
   na CLI. Dependência ausente deve indicar `python -m pip install -r requirements-xlsx.txt`.
   Capturar exceções específicas do leitor, evitando esconder erros de programação com `except Exception`.

## Contrato de células XLSX

| Caso | Decisão proposta |
|---|---|
| Cabeçalho | Primeira linha, exatamente `data`, `categoria`, `produto`, `batidas`, `kg`; sem corrigir ordem, duplicatas, espaços ou maiúsculas |
| Colunas extras | Rejeitar conteúdo além das cinco colunas; ignorar somente colunas finais sem valores decorrentes de formatação |
| Linha completamente vazia | Ignorar, preservando o número físico das próximas linhas nos erros |
| Célula obrigatória vazia | `None`, texto vazio ou só espaços: rejeitar; não converter para zero |
| Data textual | Mesmo parser de data do CSV; documentação orienta `AAAA-MM-DD`; `21/09/2026` e datas impossíveis são rejeitadas |
| Data Excel tipada | Aceitar `date` e `datetime` à meia-noite, normalizando para `date`; rejeitar horário não zero e serial numérico sem formato de data |
| Categoria/produto | Exigir texto; aplicar `strip` e regras atuais, sem transformar números/bool em nomes |
| Número textual | Decimal com ponto ou vírgula, sem separador de milhares; manter todos os dígitos |
| Número Excel | Inteiros: `Decimal(str(value))`; floats finitos: `Decimal(str(value))`, nunca `Decimal(value)` |
| Booleano | Rejeitar mesmo que Python o trate como inteiro |
| Fórmula ou erro Excel | Rejeitar em qualquer campo obrigatório, com linha/campo; inspecionar `cell.data_type` antes da conversão |
| Negativo/NaN/infinito | Rejeitar com o mesmo validador em ambos os formatos |
| Duplicata de lançamento | Somar como no CSV; não introduzir identificação/deduplicação nesta issue |

`openpyxl` não calcula fórmulas. `data_only=True` pode retornar o último resultado armazenado
pelo Excel; por isso a proposta lê a fórmula e a rejeita explicitamente, sem usar cache desatualizado.
Referência primária: [documentação do leitor](https://openpyxl.readthedocs.io/en/stable/tutorial.html#loading-from-a-file).

Excel possui precisão numérica limitada: `Decimal(str(value))` evita acrescentar artefatos binários,
mas não recupera dígitos já perdidos na origem. Para pesos com muitos dígitos, usar células textuais.
O gerador do exemplo grava kg como texto; a suíte também cobre células numéricas reais com 0.1/0.2.
Não impor arredondamento novo nem converter para float ao consolidar/exportar.

## Preparação e execução

Python 3.11+:

```bash
python -m pip install -r requirements-xlsx.txt
python -m unittest discover -s tests -v
python -m unittest discover -s tests/acceptance -v
python examples/gerar_xlsx.py
```

Após implementar o leitor:

```bash
python src/report.py examples/producao.csv --start 2026-09-21 --end 2026-09-25 --output output/csv
python src/report.py examples/producao.xlsx --start 2026-09-21 --end 2026-09-25 --output output/xlsx
```

Os testes constroem workbooks reais em diretórios temporários; não dependem do gerador para seus
oráculos e não chamam helpers internos da implementação. Comparam registros, grupos, filtros,
JSON e HTML. O contrato público continua sendo `load`, `summarize`, `export` e a CLI.

## Critérios de aceite e evidência

| Critério da issue | Testes/entrega preparados | Situação |
|---|---|---|
| Dependência e instalação | Manifesto opcional e comandos acima | Preparado; README final pendente |
| Cabeçalhos, datas e células vazias | `test_headers_are_exact`, `test_date_cells_and_iso_text`, `test_invalid_dates`, `test_empty_required_cells_and_whitespace` | Pendente de implementação |
| Valores negativos e regras | `test_negative_nonfinite_and_invalid_numbers`, `test_category_and_batch_rules` | Pendente de implementação |
| CSV/XLSX com mesmos totais | `test_example_parity_and_known_totals`, `test_cli_matches_csv_with_period_and_exports` | Pendente de implementação |
| Exemplo fictício | Gerador a partir do CSV de nove lançamentos | Gerador verificado; leitor pendente |
| Decimal e HTML/JSON | `test_decimal_and_exports_match_csv`, `test_numeric_cells_use_decimal_without_float_artifacts` | Pendente de implementação |

Oráculo do exemplo: Ração 145.000 kg / 145 t / 58 batidas; Medicamentos 100 batidas;
Premix 100; Mineral 18; Recebimentos 36.720 kg. A comparação não se limita ao total geral:
verifica cada grupo e o recorte de 22/09/2026.

Também cobertos: fórmulas/erros em todas as colunas, linhas vazias com número físico correto,
coluna adicional, extensão maiúscula, primeira aba, planilha apenas com cabeçalho e arquivo corrompido.

## Validação realizada neste rascunho

Ambiente: Python 3.12.14 e openpyxl 3.1.5.
No código-base examinado, `python -m unittest discover -s tests -v`: **5 testes aprovados**.
A suíte separada de aceite contém **16 métodos de teste**; no código-base os testes ainda falham
porque `load` abre XLSX como CSV UTF-8. Falhas/erros de subcasos não representam leitores implementados.
Esses resultados são a etapa vermelha do desenvolvimento orientado por testes, não critérios aprovados.

Antes de merge: implementar o leitor, tornar toda a suíte verde, verificar CSV sem openpyxl,
testar diagnóstico de dependência ausente, conferir encerramento do workbook em erro e integrar os
testes XLSX ao comando padrão/CI. A instalação e a mensagem de dependência ausente ainda não foram
verificadas em ambiente limpo. Não encerrar a issue só pela publicação deste rascunho.
