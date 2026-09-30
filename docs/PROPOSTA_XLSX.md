# Importação XLSX — contrato e implementação

Referência: [issue #2](https://github.com/DiogoLazzarotto/DiogoLazzarotto/issues/2).

## Implementação

`src/report.py` mantém a API pública `load(path)`, `summarize` e `export`.
`load` seleciona CSV/XLSX pela extensão sem diferenciar maiúsculas/minúsculas.
Os leitores `_load_csv` e `_load_xlsx` usam `_validate_row` para aplicar as mesmas regras.
`number` converte os pesos para Decimal; `summarize` e `export` preservam a implementação existente.
A CLI aceita qualquer um dos dois formatos com os mesmos filtros e destino.

XLSX importa openpyxl somente quando necessário, lê a primeira worksheet em `read_only=True`,
`data_only=False`, `keep_links=False` e fecha tanto arquivo quanto workbook em falhas.
O leitor redefine as dimensões da aba para não omitir células por metadados incorretos.
Arquivos ZIP/XML inválidos são traduzidos em erros legíveis. Pacote ausente gera instrução de instalação.

## Contrato de células

| Caso | Comportamento |
|---|---|
| Cabeçalho | Primeira linha, exatamente `data`, `categoria`, `produto`, `batidas`, `kg` |
| Colunas extras | Rejeitar conteúdo além das cinco; ignorar colunas finais sem valores |
| Linha completamente vazia | Ignorar no XLSX, preservando os números físicos seguintes |
| Célula obrigatória vazia | Rejeitar None, texto vazio ou espaços; não converter para zero |
| Data textual | Parser compartilhado com CSV; documentação orienta `AAAA-MM-DD` |
| Data Excel | Aceitar date/datetime à meia-noite; rejeitar horário e serial sem formato de data |
| Categoria/produto | Texto validado, com espaços externos removidos |
| Número textual | Decimal com ponto/vírgula, sem separador de milhares |
| Número Excel | Decimal(str(value)); evitar conversão direta de float para Decimal |
| Booleano, fórmula, erro Excel | Rejeitar nas células obrigatórias com linha/campo |
| Negativo/NaN/infinito | Rejeitar em ambos os formatos |
| Duplicatas | Somar por categoria/produto como no CSV |

O leitor não calcula fórmulas nem usa seus valores armazenados.
Referência: [documentação do openpyxl](https://openpyxl.readthedocs.io/en/stable/tutorial.html#loading-from-a-file).
Excel limita a precisão numérica: a conversão para Decimal não recupera dígitos perdidos na origem.
Para alta precisão, usar pesos textuais. Não foi introduzido arredondamento novo.

## Arquivos e evidências

| Arquivo | Papel |
|---|---|
| `src/report.py` | Leitores, dispatcher, validação comum, CLI e erros |
| `requirements-xlsx.txt` | Dependência opcional openpyxl 3.1.5 |
| `tests/test_report.py` | Sete testes CSV/consolidação |
| `tests/acceptance/test_xlsx.py` | 21 testes XLSX/integração |
| `tests/acceptance/__init__.py` | Inclui XLSX na descoberta padrão do unittest |
| `examples/producao.xlsx` e `examples/gerar_xlsx.py` | Exemplo fictício de nove lançamentos e gerador |
| `README.md`, `docs/REQUISITOS.md`, `docs/VALIDACAO.md` | Instalação, critérios e resultados verificáveis |

Todos os 28 testes passaram em Python 3.12.14/openpyxl 3.1.5.
CSV e XLSX do exemplo produziram HTML/JSON idênticos byte a byte; Ração 145.000 kg / 145 t / 58 batidas.
O comando padrão inclui toda a suíte: `python -m unittest discover -s tests -v`.
Detalhes, comandos sem dependência e limites de verificação estão em [VALIDACAO.md](VALIDACAO.md).

A implementação está no PR; a issue pode ser encerrada após integração em main.
