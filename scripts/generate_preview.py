"""Gera prévia SVG dos resultados reais do CSV fictício, sem pacotes gráficos."""
import sys
from decimal import Decimal
from pathlib import Path
from preview_utils import preview
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from report import load,summarize

def main():
    groups=summarize(load(ROOT/'examples/producao.csv'))
    values=lambda category:[v for (c,_),v in groups.items() if c==category]
    kg=lambda category:sum((v['kg'] for v in values(category)),Decimal(0))
    batches=lambda category:sum(v['batidas'] for v in values(category))
    fmt=lambda value:format(value,',').replace(',','.')
    preview('Relatórios de produção','CSV / XLSX · validação comum · pesos Decimal · exportação HTML e JSON',
            [('Ração',f"{kg('Ração')/Decimal(1000)} t"),('Batidas de ração',batches('Ração')),('Recebimentos',f"{fmt(kg('Recebimentos'))} kg")],
            [('Produção por categoria',[(c,f"{batches(c)} batidas") for c in ['Medicamentos','Premix','Mineral']]),
             ('Peso de ração por produto',[(p,f"{fmt(v['kg'])} kg") for (c,p),v in sorted(groups.items()) if c=='Ração'])],ROOT/'docs/assets/preview.svg')
if __name__=='__main__':main()
