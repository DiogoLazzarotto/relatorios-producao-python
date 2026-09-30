"""Valida produção CSV e gera relatório HTML/JSON sem dependências externas."""
import argparse
import csv
import html
import json
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

CATEGORIES = ('Medicamentos', 'Premix', 'Mineral', 'Ração', 'Recebimentos')
FIELDS = ('data', 'categoria', 'produto', 'batidas', 'kg')

def number(value, field, line):
    try:
        n = Decimal(value.replace(',', '.'))
    except (InvalidOperation, AttributeError):
        raise ValueError(f'Linha {line}: {field} inválido') from None
    if not n.is_finite() or n < 0:
        raise ValueError(f'Linha {line}: {field} deve ser finito e não negativo')
    return n

def load(path):
    rows = []
    with open(path, encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f, delimiter=';')
        if tuple(reader.fieldnames or ()) != FIELDS:
            raise ValueError('Cabeçalho esperado: ' + ';'.join(FIELDS))
        for line, r in enumerate(reader, 2):
            if None in r or any(v is None for v in r.values()):
                raise ValueError(f'Linha {line}: número de colunas inválido')
            r = {k: v.strip() for k, v in r.items()}
            try:
                day = date.fromisoformat(r['data'])
            except ValueError:
                raise ValueError(f'Linha {line}: data inválida') from None
            if r['categoria'] not in CATEGORIES or not r['produto']:
                raise ValueError(f'Linha {line}: categoria ou produto inválido')
            b = number(r['batidas'], 'batidas', line)
            kg = number(r['kg'], 'kg', line)
            if b != b.to_integral_value():
                raise ValueError(f'Linha {line}: batidas devem ser inteiras')
            if r['categoria'] in CATEGORIES[:3] and kg != 0:
                raise ValueError(f'Linha {line}: categorias auxiliares usam apenas batidas (kg=0)')
            if r['categoria'] == 'Recebimentos' and b != 0:
                raise ValueError(f'Linha {line}: recebimentos usam apenas kg (batidas=0)')
            rows.append(dict(data=day, categoria=r['categoria'], produto=r['produto'], batidas=int(b), kg=kg))
    return rows

def summarize(rows, start=None, end=None):
    if start and end and start > end:
        raise ValueError('Data inicial deve ser anterior ou igual à final')
    groups = {}
    for r in rows:
        if (start and r['data'] < start) or (end and r['data'] > end):
            continue
        key = (r['categoria'], r['produto'])
        target = groups.setdefault(key, {'batidas': 0, 'kg': Decimal(0)})
        target['batidas'] += r['batidas']; target['kg'] += r['kg']
    return groups

def export(groups, output, title):
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    payload = [{'categoria': c, 'produto': p, 'batidas': v['batidas'], 'kg': str(v['kg'])}
               for (c, p), v in sorted(groups.items())]
    (output/'totais.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    sections = []
    for cat in CATEGORIES:
        items = [(p, v) for (c, p), v in sorted(groups.items()) if c == cat]
        if not items: continue
        weight = cat in ('Ração', 'Recebimentos')
        heads = '<th>Batidas</th><th>kg</th>' if cat == 'Ração' else ('<th>kg</th>' if weight else '<th>Batidas</th>')
        trs = []
        for product, v in items:
            cells = f"<td>{v['batidas']}</td><td>{v['kg']}</td>" if cat == 'Ração' else f"<td>{v['kg'] if weight else v['batidas']}</td>"
            trs.append('<tr><td>'+html.escape(product)+'</td>'+cells+'</tr>')
        total = sum((v['kg'] for _, v in items), Decimal(0)) if weight else sum(v['batidas'] for _, v in items)
        footer = f'Total: {total} kg' if weight else f'Total: {total} batidas'
        if cat == 'Ração': footer += f' · {total/Decimal(1000)} toneladas'
        sections.append(f'<section><h2>{cat}</h2><table><thead><tr><th>Produto</th>{heads}</tr></thead><tbody>'+''.join(trs)+f'</tbody></table><p><strong>{footer}</strong></p></section>')
    body = ''.join(sections) or '<p>Nenhum registro no período.</p>'
    page = '<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title><style>body{font:16px system-ui;color:#172b42;max-width:900px;margin:40px auto;padding:0 24px}h1,h2{color:#124b80}section{break-inside:avoid;margin:30px 0}table{width:100%;border-collapse:collapse}th,td{padding:10px;border-bottom:1px solid #ccd8e5;text-align:left}th{background:#eaf2fa}@media print{body{margin:0;font-size:12px}}</style><h1>'+html.escape(title)+'</h1><p>Dados fictícios para demonstração · pesos informados, sem conversão de batidas.</p>'+body+'</html>'
    (output/'relatorio.html').write_text(page, encoding='utf-8')

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('csv'); ap.add_argument('--start', type=date.fromisoformat)
    ap.add_argument('--end', type=date.fromisoformat); ap.add_argument('--output', default='output')
    args = ap.parse_args()
    try:
        groups = summarize(load(args.csv), args.start, args.end)
        export(groups, args.output, f'Produção e recebimentos · {args.start or "início"} a {args.end or "fim"}')
    except (ValueError, OSError) as e:
        ap.exit(2, f'Erro: {e}\n')
    print(f'Relatório criado em {args.output}/relatorio.html')
if __name__ == '__main__': main()
