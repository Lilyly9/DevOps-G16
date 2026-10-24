"""A3 authored equivalent: only the expected dependency differs between versions."""
import tempfile
from pathlib import Path

from buildchecker.fullcheck import declaration_graph


def test_ci_reject_demo():
    with tempfile.TemporaryDirectory() as folder:
        database = Path(folder) / "make-db.txt"
        database.write_text(
            "# Files\nmain.o: main.c config.h\n# files hash-table stats:\n",
            encoding="utf-8",
        )
        declared = declaration_graph(database, "/course/project")
        assert set(declared["main.o"]["dependencies"]) == {"main.c", "config.h"}
