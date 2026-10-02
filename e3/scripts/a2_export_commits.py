"""Export the frozen C0/C1/C2 fixtures of A2's EChecker lab project.

Read-only with respect to Git: the script resolves the three tags, reads the
lab project tree straight out of the commit objects and writes byte-identical
snapshots plus metadata under ``e3/fixtures/commits/<tag>/``.

Running it again only rewrites the same bytes, so the export can be re-checked
at any time (for example after a fresh clone).

    python e3/scripts/a2_export_commits.py [--check]
"""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

E3 = Path(__file__).resolve().parents[1]
REPO = E3.parent
LAB = "e3/fixtures/commits/lab"
TAGS = ["C0", "C1", "C2"]
FIXTURES = E3 / "fixtures" / "commits"


def git(*args):
    return subprocess.run(["git", "-C", str(REPO), *args], check=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout


def resolve(tag):
    """Full commit SHA, must be 40 hex characters: refuses abbreviated output."""
    sha = git("rev-parse", tag + "^{commit}").decode().strip()
    if len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        raise RuntimeError("unexpected commit id for %s: %r" % (tag, sha))
    return sha


def tree_entries(commit):
    """[{path, blob}] for every file of the lab project at that commit."""
    out = git("ls-tree", "-r", "-z", "--full-tree", commit + ":" + LAB)
    entries = []
    for item in out.split(b"\0"):
        if not item:
            continue
        meta, path = item.split(b"\t", 1)
        mode, kind, blob = meta.split(b" ", 2)
        if kind != b"blob":
            raise RuntimeError("unexpected object type %r" % kind)
        entries.append({"path": path.decode("utf-8"), "blob": blob.decode("ascii"),
                        "mode": mode.decode("ascii")})
    return sorted(entries, key=lambda e: e["path"])


def commit_meta(commit):
    raw = git("show", "-s", "--format=%H%n%an%n%ae%n%aI%n%cI%n%B", commit).decode("utf-8", "replace")
    fields = raw.split("\n", 5)
    return {"commit": fields[0], "author_name": fields[1], "author_email": fields[2],
            "authored_at": fields[3], "committed_at": fields[4],
            "message": fields[5].rstrip("\n")}


def blob_id(data):
    """Git object id of a blob, i.e. sha1("blob <len>\\0" + content)."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="only verify that the snapshots already match the tags")
    args = parser.parse_args()

    summary = {"member": "A2", "project": LAB, "tags": {}, "order": TAGS}
    for tag in TAGS:
        commit = resolve(tag)
        entries = tree_entries(commit)
        meta = commit_meta(commit)
        meta["parent"] = git("rev-parse", commit + "^").decode().strip() if tag != "C0" else None
        files = {}
        for entry in entries:
            blob_bytes = git("cat-file", "blob", entry["blob"])
            if blob_id(blob_bytes) != entry["blob"]:
                raise RuntimeError("blob id mismatch for %s" % entry["path"])
            dest = FIXTURES / tag / entry["path"]
            if args.check:
                if not dest.is_file() or dest.read_bytes() != blob_bytes:
                    raise RuntimeError("%s is missing or differs from tag %s" % (dest, tag))
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(blob_bytes)
            files[entry["path"]] = {"git_blob_sha1": entry["blob"], "mode": entry["mode"],
                                    "sha256": hashlib.sha256(blob_bytes).hexdigest(),
                                    "bytes": len(blob_bytes)}
        meta.update({"tag": tag, "tree_path": LAB + " at " + tag, "files": files})
        summary["tags"][tag] = meta
        if not args.check:
            (FIXTURES / tag / "commit.json").write_text(
                json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    summary["export"] = {
        "script": "e3/scripts/a2_export_commits.py",
        "method": "git cat-file blob of <tag>:e3/fixtures/commits/lab, byte-identical",
        "check_command": "python e3/scripts/a2_export_commits.py --check",
    }
    if not args.check:
        (FIXTURES / "versions.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for tag in TAGS:
        print("TAG=%s COMMIT=%s FILES=%d" % (tag, summary["tags"][tag]["commit"],
                                             len(summary["tags"][tag]["files"])))
    print("MODE=" + ("CHECK" if args.check else "EXPORT"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
