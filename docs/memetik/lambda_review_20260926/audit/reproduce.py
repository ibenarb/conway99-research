"""Replay the bounded audits of the supplied review; no depth-3/4 search."""
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

here = Path(__file__).resolve().parent
repo = next(p for p in here.parents if (p / 'tools/memetik/audit_python.py').is_file())
helper = repo / 'tools/memetik/audit_python.py'
archive_commit = '7a00a6a93227eb7eb09980355b4d3129975489fc'
output = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(tempfile.mkdtemp(prefix='lambda_review_audit_'))
output.mkdir(parents=True, exist_ok=True)
data = output / 'data'
review = output / 'review'
data.mkdir(exist_ok=True)
review.mkdir(exist_ok=True)
with zipfile.ZipFile(repo / 'releases/memetik/Lambda_Review_20260926.zip') as z:
    z.extractall(data)
blob = subprocess.check_output(['git', '-C', str(repo), 'show', archive_commit + ':docs/reviews/20260926_lambda/reviewer_lambda_20260926_pruefsatz.zip'])
archive = output / 'reviewer_original.zip'
archive.write_bytes(blob)
with zipfile.ZipFile(archive) as z:
    z.extractall(review)
for name in ('depth2.py', 'mitm.py'):
    text = (review / name).read_text()
    text = text.replace('/home/claude/repo', str(repo))
    text = text.replace('/home/claude/lr', str(data))
    text = text.replace('/home/claude/rv', str(review))
    (review / name).write_text(text)

def run(script, args, log):
    with (output / log).open('w') as stream:
        subprocess.run([sys.executable, str(helper), '--', str(script), *map(str, args)], cwd=output, stdout=stream, check=True)

run(data / '04_VERIFY.py', [], 'verify_result.json')
run(review / 'analysis.py', [data], 'analysis_summary.json')
run(review / 'depth2.py', [review / 'spec.json', output / 'depth2_result.json'], 'depth2.log')
run(review / 'mitm.py', ['2079-2076', '2081-2079', '2096-2081'], 'mitm.log')
run(here / 'supplement.py', [data, output / 'supplement_result.json'], 'supplement.log')
print(output)
