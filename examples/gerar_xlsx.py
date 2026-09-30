"""Gera exemplo XLSX fictício equivalente a producao.csv; não altera o CSV."""
import csv
from datetime import date
from pathlib import Path
from openpyxl import Workbook

def generate():
    folder = Path(__file__).resolve().parent
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = 'Produção'
    with (folder / 'producao.csv').open(encoding='utf-8-sig', newline='') as source:
        reader = csv.reader(source, delimiter=';')
        sheet.append(next(reader))
        for row in reader:
            if not row:
                continue
            day, category, product, batches, kg = row
            # Pesos textuais preservam todos os dígitos; testes também cobrem números Excel.
            sheet.append([date.fromisoformat(day), category, product, int(batches), kg])
    target = folder / 'producao.xlsx'
    workbook.save(target)
    workbook.close()
    return target

if __name__ == '__main__':
    print(generate())
