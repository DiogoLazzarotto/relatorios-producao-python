import sys, unittest, tempfile
from pathlib import Path
from datetime import date
from decimal import Decimal
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from report import load, summarize, export

class ReportTests(unittest.TestCase):
    def test_totals_and_filter(self):
        rows=load(Path(__file__).resolve().parents[1]/'examples/producao.csv')
        g=summarize(rows)
        self.assertEqual(g[('Ração','Terminação 2A')]['kg'],Decimal('110000'))
        self.assertEqual(g[('Medicamentos','Terminação 1')]['batidas'],100)
        self.assertEqual(summarize(rows,date(2026,9,22),date(2026,9,22))[('Ração','Alojamento 1')]['kg'],Decimal('30000'))
    def test_invalid_values(self):
        for value in ['-1','NaN','Infinity','texto']:
            with self.subTest(value=value), tempfile.TemporaryDirectory() as td:
                p=Path(td)/'x.csv';p.write_text('data;categoria;produto;batidas;kg\n2026-09-21;Ração;X;1;'+value+'\n')
                with self.assertRaises(ValueError): load(p)
    def test_decimal_and_html_escape(self):
        rows=[dict(data=date(2026,9,21),categoria='Ração',produto='<script>',batidas=1,kg=Decimal(x)) for x in ['0.1','0.2']]
        g=summarize(rows);self.assertEqual(g[('Ração','<script>')]['kg'],Decimal('0.3'))
        with tempfile.TemporaryDirectory() as td:
            export(g,td,'teste');s=(Path(td)/'relatorio.html').read_text()
            self.assertIn('&lt;script&gt;',s);self.assertIn('0.0003 toneladas',s)
    def test_reversed_period(self):
        with self.assertRaises(ValueError): summarize([],date(2026,9,22),date(2026,9,21))
    def test_fractional_batches(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'x.csv';p.write_text('data;categoria;produto;batidas;kg\n2026-09-21;Premix;X;1.5;0\n')
            with self.assertRaises(ValueError):load(p)
if __name__=='__main__':unittest.main()
