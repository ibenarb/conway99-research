cd /home/claude/review
for a in 2076 2077; do
  [ -f depth3_$a.json ] || python3 depth3_resume.py $a >> depth3_$a.log 2>&1
done
