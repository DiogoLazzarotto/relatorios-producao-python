# Validação dos relatórios de produção

Verificado em 30/09/2026 com Python 3.12.14 e openpyxl 3.1.5. Evidências específicas deste projeto.

| Verificação | Resultado |
|---|---|
| `python -m unittest discover -s tests -v` | 28 testes aprovados: sete de CSV/consolidação e 21 de XLSX/integração |
| `python -S -m unittest discover -s tests -p test_report.py -v` | Sete testes aprovados sem acesso aos pacotes externos |
| CLI CSV e XLSX com exemplo e período 21–25/09/2026 | HTML e JSON comparados byte a byte: idênticos |
| CLI sem dependência (`python -S`) | CSV funciona; XLSX retorna código 2 com instrução de instalação, sem traceback |
| Arquivos ZIP/XML danificados | Erro legível, código 2; nenhum relatório novo gerado |
| Validação falha após abrir XLSX | Workbook fechado; verificado por teste com leitor real |
| Exemplo fictício incluído | Nove lançamentos equivalentes ao CSV; Ração 145.000 kg / 145 t / 58 batidas |

Os testes verificam cabeçalhos, datas, células vazias, negativos, finitude, batidas inteiras,
regras de categoria, fórmulas/erros de célula, colunas extras/formatadas, primeira aba,
extensão maiúscula, linhas físicas, filtros e Decimal. Testam soma 0.1+0.2 sem artefatos,
peso textual com muitos dígitos, escape HTML e kg textual no JSON.

Dependência opcional fixada em `requirements-xlsx.txt`; comandos documentados no README.
A instalação por download em ambiente novo não foi executada: a versão 3.1.5 já estava disponível
no ambiente de verificação. O teste sem dependência usa `-S` para excluir pacotes externos.

## Limitações da verificação

Executado em Python 3.12; Python 3.11 não foi executado neste ambiente. Não houve inspeção visual
em navegador, validação com usuários ou medição operacional. Não há CI configurada neste repositório.
