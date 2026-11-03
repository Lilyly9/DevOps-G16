"""A3: cyclic phony prerequisites must fail explicitly, not certify a build."""
import tempfile
import unittest
from pathlib import Path

from buildchecker.fullcheck import Unsupported, declaration_graph


class TestPhonyCycle241880464(unittest.TestCase):
    def test_cyclic_phony_dependencies_are_unsupported(self):
        with tempfile.TemporaryDirectory() as folder:
            database = Path(folder) / "make-db.txt"
            database.write_text(
                "# Files\n.PHONY: prepare configure\n"
                "prepare: configure\nconfigure: prepare\n"
                "main.o: main.c prepare\n# files hash-table stats:\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(Unsupported, "Cycle in phony prerequisites"):
                declaration_graph(database, "/course/project")
