# Relatórios de produção em Python

Automatiza a consolidação de planilhas exportadas pelo Excel como CSV, com validações, filtros de período e totais por produto. Projeto demonstrativo com dados fictícios e apoio de IA.

## Executar

Python 3.11+, sem pacotes externos. Execute nesta pasta:

```bash
python src/report.py examples/producao.csv --start 2026-09-21 --end 2026-09-25 --output output
python -m unittest discover -s tests -v
```

Abra `output/relatorio.html` ou [o exemplo gerado](examples/relatorio.html). O navegador permite imprimir/salvar como PDF. `totais.json` fornece a saída estruturada.

## Entrada e regras

CSV UTF-8 com separador `;` e cabeçalho `data;categoria;produto;batidas;kg`. Excel: exporte mantendo esse cabeçalho e separador. Datas ISO `AAAA-MM-DD`; decimal com ponto ou vírgula, sem separador de milhares.

Medicamentos, Premix e Mineral usam batidas inteiras e kg=0. Recebimentos usam kg e batidas=0. Ração mostra batidas, kg e total em toneladas. Peso é informado, não inferido por batida. Valores negativos, NaN, colunas incorretas, produtos vazios e datas inválidas são rejeitados. Duplicatas são somadas: o formato não possui identificador de lançamento.

## Resultado esperado do exemplo

- Ração: 145.000 kg / 145 t / 58 batidas.
- Medicamentos: 100 batidas; Premix: 100; Mineral: 18.
- Recebimentos: 36.720 kg.

## Decisões e limites

`Decimal` mantém precisão nos pesos. HTML escapa conteúdo do CSV. Biblioteca padrão simplifica a instalação. Não lê XLSX nem gera PDF diretamente; não registra indicadores reais de ganho de tempo.

Próximo passo: importar XLSX e adicionar identificadores para detectar duplicatas.

## Obter o projeto

```bash
git clone https://github.com/DiogoLazzarotto/relatorios-producao-python.git
cd relatorios-producao-python
```

[Voltar ao perfil](https://github.com/DiogoLazzarotto)
