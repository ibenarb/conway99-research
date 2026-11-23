from pathlib import Path
from math import lcm
import json
import own_local
import own_setup


def write_setup(cid, parity, output):
    chart = own_local.Chart(cid, parity)
    assert chart.physical and chart.rank in (8, 9)
    assert chart.rank == own_local.LAY[cid][0]
    bounds = {}
    for name, matrix, factor in [('signed', chart.Finv, 3600), ('unsigned', chart.Hinv, 2304)]:
        den = lcm(*(x.denominator for row in matrix for x in row))
        maximum = max(abs(int(x * den)) for row in matrix for x in row)
        assert factor * maximum < 2**63 and 10 * den < 2**63
        bounds[name] = dict(denominator=den, int64_bound=factor*maximum)
    den = bounds['signed']['denominator']
    fi = [[int(x * den) for x in row] for row in chart.Finv]
    max_fi = max(abs(x) for row in fi for x in row)
    assert (5 * den + 3600 * max_fi)**2 < 2**127
    domains = own_setup.attachments_fast(chart)
    counts = {str(y): len(domains[y]) for y in own_local.OUTER}
    with Path(output).open('w') as stream:
        stream.write(f'LOWGRAM1 {chart.rank} {chart.detQ} {den}\n')
        for j in range(6):
            for k in range(j+1, 6):
                stream.write(' '.join(map(str, chart.words_outer[(j,k)]))+'\n')
        stream.write(str(sum(map(len, domains.values())))+'\n')
        for yi, y in enumerate(own_local.OUTER):
            for a in domains[y]:
                projected = [sum(fi[i][j]*a['f'][j] for j in range(12)) for i in range(12)]
                norm = 10*den - sum(a['f'][i]*projected[i] for i in range(12))
                assert norm >= 0 and len(a['h']) == 11-chart.rank
                # Cross-check the optimized setup against direct exact rational arithmetic.
                assert norm == den*(10-sum(a['f'][i]*chart.Finv[i][j]*a['f'][j] for i in range(12) for j in range(12)))
                assert all(0 <= x < 7 for x in a['h'])
                row = [yi,a['mask'],a['twin'],a['rho'],norm]
                row += list(a['h'])+list(a['key'])+a['fI']+a['m']+a['f']+projected
                stream.write(' '.join(map(str,row))+'\n')
        stream.write(' '.join(map(str,chart.A))+'\n')
    return chart, dict(bounds=bounds, attachments=counts, determinant=chart.detQ,
                       common_image='57_planes' if chart.rank == 8 else
                       ('whole_F7_squared_both_cases' if chart.detQ in (1,2,4) else '8_lines'))
