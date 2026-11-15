set -euo pipefail
source /root/241880464/e8e10-materials/classroom_helpers.sh
lab_ready
lab_new_run e10 A
printf '%s\n' "$OUT" > work/last-e10-A-extension.path
lab_python "$OUT" <<'PY'
from pathlib import Path
import sys
from student_241880464 import measure
measure(Path(sys.argv[1])/'extension')
PY
