set -eu
source /root/241880464/e8e10-materials/classroom_helpers.sh
lab_ready
lab_new_run e9 A
printf "%s\n" "$OUT" > work/last-e9-A-extension.path
lab_python "$OUT" <<'EXTENSION_PY_END'
from pathlib import Path
import sys
from student_241880464_followup import run_extension
run_extension("e9", Path(sys.argv[1]))
EXTENSION_PY_END

git -C "$OUT/project" log --reverse --format="%H %s" > "$OUT/project-history.txt"
git -C "$OUT/project" bundle create "$PWD/$OUT/project-history.bundle" HEAD
git -C "$OUT/project" bundle verify "$PWD/$OUT/project-history.bundle"
