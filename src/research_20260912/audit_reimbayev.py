"""Two independent representations of the same HTML; exact symbolic audit."""
from pathlib import Path
import hashlib
import html
import json
import re
import xml.etree.ElementTree as ET
import sympy as s
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor

BASE = Path(__file__).resolve().parents[2]
path = BASE / 'data/research_20260912/reimbayev.html'
raw = path.read_text().split('<section id="S3"')[0]
n, k, x, y = s.symbols('n k x y')
locals_ = dict(n=n, k=k, x=x, y=y)
transforms = standard_transformations + (implicit_multiplication_application, convert_xor)

def mathml(e):
    tag = e.tag
    if tag in ('annotation', 'mphantom'):
        return ''
    if tag == 'semantics':
        return mathml(e[0])
    if tag == 'mfrac':
        return '((' + mathml(e[0]) + ')/(' + mathml(e[1]) + '))'
    if tag == 'msup':
        return '((' + mathml(e[0]) + ')**(' + mathml(e[1]) + '))'
    if tag == 'msub':
        text = ''.join(e.itertext())
        return {'n3': 'x', 'z11': 'y'}.get(text, text)
    if len(e):
        return ''.join(mathml(c) for c in e)
    return (e.text or '').replace('−', '-').replace('\u200b', '*').replace('OPEN', '').replace('CLOSE', '')

latex, visual = {}, {}
current = None
for fragment in re.findall(r'<math\b.*?</math>', raw, re.S):
    e = ET.fromstring(fragment)
    alt = html.unescape(e.get('alttext', ''))
    match = re.fullmatch(r'\\displaystyle z_\{(\d+)\}=', alt)
    if match:
        current = int(match[1])
        latex[current] = visual[current] = ''
    elif current is not None:
        latex[current] += alt.replace('\\displaystyle', '').rstrip(',.')
        visual[current] += mathml(e).rstrip(',.')
assert sorted(latex) == list(range(1, 209))
formulas = {}
for i, text in latex.items():
    text = text.replace('n_{3}', 'x').replace('z_{11}', 'y')
    text = re.sub(r'\\frac\{([^{}]+)\}\{([^{}]+)\}', r'((\1)/(\2))', text)
    text = text.replace('{', '(').replace('}', ')')
    first = parse_expr(text, local_dict=locals_, transformations=transforms)
    second = parse_expr(visual[i], local_dict=locals_, transformations=transforms)
    assert s.expand(first - second) == 0, i
    formulas[i] = first
tex_path = BASE / 'data/research_20260912/reimbayev_source.tex'
tex = tex_path.read_text()
parts = re.split(r'z_(?:\{(\d+)\}|(\d))\s*=&', tex)
source_checked = 0
for t in range(1, len(parts), 3):
    index = int(parts[t] or parts[t+1])
    expression = parts[t+2].split(r'\end{')[0]
    expression = expression.replace(r'\\', '').replace('&', '').replace(r'\nonumber', '').strip().rstrip(',.')
    expression = expression.replace('n_{3}', 'x').replace('n_3', 'x').replace('z_{11}', 'y')
    expression = re.sub(r'\\frac\{([^{}]+)\}\{([^{}]+)\}', r'((\1)/(\2))', expression)
    expression = expression.replace('{', '(').replace('}', ')')
    parsed = parse_expr(expression, local_dict=locals_, transformations=transforms)
    assert s.expand(parsed-formulas[index]) == 0, index
    source_checked += 1
assert source_checked == 208
summed = s.expand(sum(formulas.values()))
conway = s.expand(summed.subs({n: 99, k: 14}))
expected = s.binomial(99, 7)
rook = [v.subs({n: 9, k: 4, x: 0, y: 0}) for v in formulas.values()]
assert sum(rook) == 36 and min(rook) >= 0
result = {
    'status': 'PUBLISHED_TABLE_FAILS_NECESSARY_SUM_IDENTITY',
    'html_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
    'equations_parsed_and_crosschecked': len(formulas), 'source_tex_equations_crosschecked': source_checked, 'source_tex_sha256': hashlib.sha256(tex_path.read_bytes()).hexdigest(),
    'sum_conway': str(conway), 'required_conway': str(expected),
    'deficit': str(expected - conway),
    'free_variable_coefficients': [str(summed.coeff(x)), str(summed.coeff(y))],
    'sum_error_after_parameter_relation': str(s.factor((summed - s.prod(n-j for j in range(7))/s.factorial(7)).subs(n, (k*k+2)/2))),
    'rook_control': {'sum': str(sum(rook)), 'negative_entries': 0},
    'scope': 'HTML LaTeX and MathML plus original arXiv TeX agree termwise. No repaired individual formula claimed.',
}
out = BASE / 'results/research_20260912/reimbayev.json'
out.write_text(json.dumps(result, indent=4) + '\n')
print(json.dumps({k: v for k, v in result.items() if k != 'conway_formulas'}, indent=4))
