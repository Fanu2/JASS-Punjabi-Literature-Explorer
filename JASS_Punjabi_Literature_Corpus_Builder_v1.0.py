"""
JASS Punjabi Literature Corpus Builder v1.0

Builds a read-only SQLite + FTS5 database from Punjabi literary TXT files.

Source files are NEVER modified.

Database:
    JASS_Punjabi_Literature.db

Tables:
    works      - one row per literary work
    passages   - one row per paragraph/passage
    passages_fts - FTS5 search index

Each passage retains:
    - work ID
    - source filename
    - paragraph number
    - source line start/end
    - text

The builder also records SHA-256 hashes of every source file and performs
post-build verification.
"""

from __future__ import annotations

import hashlib
import re
import sqlite3
import time
from pathlib import Path
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

FOLDER = Path(
    r"C:\Users\singh\Downloads\1762611761169-MEDIAMEN's Punjabi Literature Corpus"
)

DB_PATH = FOLDER / "JASS_Punjabi_Literature.db"
REPORT_PATH = FOLDER / "punjabi_literature_build_report.txt"

# ---------------------------------------------------------------------------
# Unicode/script helpers
# ---------------------------------------------------------------------------

GURMUKHI_RE = re.compile(r"[\u0A00-\u0A7F]")
ARABIC_RE = re.compile(
    r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]"
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def decode_text(data: bytes) -> tuple[str, str]:
    """
    Best-effort decoding.

    Punjabi literary files are expected to be Unicode text. UTF-8 is tried
    first, followed by UTF-16 variants. A replacement fallback is used only
    if necessary.
    """
    for enc in ("utf-8-sig", "utf-8", "utf-16", "utf-16-le", "utf-16-be"):
        try:
            return data.decode(enc), enc
        except UnicodeDecodeError:
            pass

    return data.decode("utf-8", errors="replace"), "utf-8 (replacement fallback)"


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def split_passages(text: str) -> list[tuple[int, int, str]]:
    """
    Split text into paragraphs while preserving source line positions.

    Returns:
        (source_line_start, source_line_end, paragraph_text)
    """
    lines = text.splitlines()
    passages = []

    start = None
    buffer = []

    for line_no, line in enumerate(lines, start=1):
        if line.strip():
            if start is None:
                start = line_no
            buffer.append(line.strip())
        else:
            if buffer:
                passages.append((start, line_no - 1, "\n".join(buffer)))
                start = None
                buffer = []

    if buffer:
        passages.append((start, len(lines), "\n".join(buffer)))

    # If the file has no non-empty paragraph structure, preserve non-empty
    # individual lines as passages.
    if not passages:
        for line_no, line in enumerate(lines, start=1):
            if line.strip():
                passages.append((line_no, line_no, line.strip()))

    return passages


def configure_database(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")

    conn.executescript(
        """
        DROP TABLE IF EXISTS passages_fts;
        DROP TABLE IF EXISTS passages;
        DROP TABLE IF EXISTS works;

        CREATE TABLE works (
            work_id INTEGER PRIMARY KEY,
            filename TEXT NOT NULL UNIQUE,
            title TEXT NOT NULL,
            size_bytes INTEGER NOT NULL,
            encoding TEXT NOT NULL,
            word_count INTEGER NOT NULL,
            character_count INTEGER NOT NULL,
            line_count INTEGER NOT NULL,
            paragraph_count INTEGER NOT NULL,
            gurmukhi_characters INTEGER NOT NULL,
            arabic_script_characters INTEGER NOT NULL,
            sha256 TEXT NOT NULL
        );

        CREATE TABLE passages (
            passage_id INTEGER PRIMARY KEY,
            work_id INTEGER NOT NULL,
            paragraph_number INTEGER NOT NULL,
            source_line_start INTEGER NOT NULL,
            source_line_end INTEGER NOT NULL,
            text TEXT NOT NULL,
            word_count INTEGER NOT NULL,
            FOREIGN KEY(work_id) REFERENCES works(work_id)
        );

        CREATE VIRTUAL TABLE passages_fts USING fts5(
            text,
            content='passages',
            content_rowid='passage_id'
        );

        CREATE INDEX idx_passages_work
            ON passages(work_id);

        CREATE INDEX idx_passages_work_paragraph
            ON passages(work_id, paragraph_number);
        """
    )


def main() -> None:
    print("JASS PUNJABI LITERATURE CORPUS BUILDER v1.0")
    print("=" * 49)
    print(f"Source: {FOLDER}")
    print("Mode: READ-ONLY")
    print()

    if not FOLDER.exists():
        print("ERROR: Source folder not found.")
        print("Check FOLDER at the top of this script.")
        return

    files = sorted(FOLDER.glob("*.txt"), key=lambda p: p.name.lower())

    # Never treat our generated report as a corpus source.
    files = [
        p for p in files
        if p.name.lower() != REPORT_PATH.name.lower()
    ]

    if not files:
        print("ERROR: No TXT files found.")
        return

    print(f"Source works: {len(files):,}")
    print("Calculating source SHA-256 hashes...")
    print()

    source_info = []

    for i, path in enumerate(files, 1):
        data = path.read_bytes()
        text, encoding = decode_text(data)
        digest = sha256_file(path)

        source_info.append(
            {
                "path": path,
                "data": data,
                "text": text,
                "encoding": encoding,
                "sha256": digest,
            }
        )

        print(f"  [{i:02d}/{len(files):02d}] {path.name}")
        print(f"      SHA-256: {digest}")

    print()
    print("Creating SQLite database...")
    if DB_PATH.exists():
        print(f"Replacing existing database: {DB_PATH.name}")

    # Remove old SQLite sidecars if they exist.
    for sidecar in (
        Path(str(DB_PATH) + "-wal"),
        Path(str(DB_PATH) + "-shm"),
    ):
        if sidecar.exists():
            sidecar.unlink()

    start_time = time.perf_counter()

    conn = sqlite3.connect(DB_PATH)
    try:
        configure_database(conn)

        total_words = 0
        total_chars = 0
        total_lines = 0
        total_paragraphs = 0
        total_gurmukhi = 0
        total_arabic = 0

        passage_id = 0

        for work_id, info in enumerate(source_info, start=1):
            path = info["path"]
            text = info["text"]

            lines = text.splitlines()
            line_count = len(lines)
            paragraphs = split_passages(text)

            words = word_count(text)
            chars = len(text)
            gur = len(GURMUKHI_RE.findall(text))
            arabic = len(ARABIC_RE.findall(text))

            title = path.stem

            conn.execute(
                """
                INSERT INTO works (
                    work_id, filename, title, size_bytes, encoding,
                    word_count, character_count, line_count,
                    paragraph_count, gurmukhi_characters,
                    arabic_script_characters, sha256
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    work_id,
                    path.name,
                    title,
                    len(info["data"]),
                    info["encoding"],
                    words,
                    chars,
                    line_count,
                    len(paragraphs),
                    gur,
                    arabic,
                    info["sha256"],
                ),
            )

            for paragraph_number, (line_start, line_end, passage) in enumerate(
                paragraphs, start=1
            ):
                passage_id += 1
                conn.execute(
                    """
                    INSERT INTO passages (
                        passage_id, work_id, paragraph_number,
                        source_line_start, source_line_end,
                        text, word_count
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        passage_id,
                        work_id,
                        paragraph_number,
                        line_start,
                        line_end,
                        passage,
                        word_count(passage),
                    ),
                )

            total_words += words
            total_chars += chars
            total_lines += line_count
            total_paragraphs += len(paragraphs)
            total_gurmukhi += gur
            total_arabic += arabic

            print(
                f"  {work_id:02d}. {path.name} — "
                f"{words:,} words, {len(paragraphs):,} passages"
            )

        print("Finalizing FTS index...")
        conn.execute(
            "INSERT INTO passages_fts(passages_fts) VALUES('rebuild')"
        )

        conn.commit()

        # Optimize database indexes.
        conn.execute("PRAGMA optimize")
        conn.commit()

        elapsed = time.perf_counter() - start_time

    finally:
        conn.close()

    # -----------------------------------------------------------------------
    # Verification
    # -----------------------------------------------------------------------

    print()
    print("Running verification...")

    conn = sqlite3.connect(DB_PATH)
    try:
        db_work_count = conn.execute(
            "SELECT COUNT(*) FROM works"
        ).fetchone()[0]

        db_passage_count = conn.execute(
            "SELECT COUNT(*) FROM passages"
        ).fetchone()[0]

        fts_count = conn.execute(
            "SELECT COUNT(*) FROM passages_fts"
        ).fetchone()[0]

        db_words = conn.execute(
            "SELECT COALESCE(SUM(word_count), 0) FROM works"
        ).fetchone()[0]

        db_chars = conn.execute(
            "SELECT COALESCE(SUM(character_count), 0) FROM works"
        ).fetchone()[0]

        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]

        # Search smoke test for an Arabic/Shahmukhi character commonly
        # present in the collection. This tests FTS functionality rather
        # than asserting a fixed corpus-wide match count.
        test_term = "ا"
        test_matches = conn.execute(
            """
            SELECT COUNT(*)
            FROM passages_fts
            WHERE passages_fts MATCH ?
            """,
            (test_term,),
        ).fetchone()[0]

    finally:
        conn.close()

    source_hashes_after = {
        info["path"].name: sha256_file(info["path"])
        for info in source_info
    }

    source_integrity = all(
        source_hashes_after[info["path"].name] == info["sha256"]
        for info in source_info
    )

    count_pass = db_work_count == len(files)
    passage_pass = db_passage_count == fts_count
    word_pass = db_words == total_words
    char_pass = db_chars == total_chars
    sqlite_pass = integrity.lower() == "ok"
    source_pass = source_integrity
    overall = all(
        (
            count_pass,
            passage_pass,
            word_pass,
            char_pass,
            sqlite_pass,
            source_pass,
        )
    )

    db_size = DB_PATH.stat().st_size

    report_lines = [
        "JASS PUNJABI LITERATURE CORPUS BUILD REPORT v1.0",
        "=" * 57,
        "",
        "SOURCE",
        f"Folder: {FOLDER}",
        f"Files: {len(files):,}",
        "Mode: READ-ONLY",
        "",
        "DATABASE",
        f"File: {DB_PATH}",
        f"Size: {db_size / (1024 * 1024):,.2f} MB",
        "",
        "CORPUS",
        f"Works: {len(files):,}",
        f"Words: {total_words:,}",
        f"Characters: {total_chars:,}",
        f"Lines: {total_lines:,}",
        f"Passages: {total_paragraphs:,}",
        f"Gurmukhi characters: {total_gurmukhi:,}",
        f"Arabic/Shahmukhi characters: {total_arabic:,}",
        "",
        "VERIFICATION",
        f"Work count: {'PASSED' if count_pass else 'FAILED'}",
        f"Passage count: {'PASSED' if passage_pass else 'FAILED'}",
        f"Word count: {'PASSED' if word_pass else 'FAILED'}",
        f"Character count: {'PASSED' if char_pass else 'FAILED'}",
        f"Source integrity: {'PASSED' if source_pass else 'FAILED'}",
        f"SQLite integrity: {'PASSED' if sqlite_pass else 'FAILED'}",
        f"FTS smoke test (term: {test_term}): {test_matches:,} matches",
        f"Overall verification: {'PASSED' if overall else 'FAILED'}",
        "",
        "BUILD TIME",
        f"{elapsed:.1f} seconds",
        "",
        "SOURCE HASHES",
    ]

    for info in source_info:
        report_lines.append(
            f"{info['path'].name}: {info['sha256']}"
        )

    report_lines.extend(
        [
            "",
            "NOTE",
            "Original TXT source files were not modified.",
        ]
    )

    REPORT_PATH.write_text("\n".join(report_lines), encoding="utf-8")

    print()
    print("JASS PUNJABI LITERATURE BUILD COMPLETE")
    print("=" * 49)
    print()
    print("DATABASE")
    print(f"File:       {DB_PATH}")
    print(f"Size:       {db_size / (1024 * 1024):,.2f} MB")
    print()
    print("RECORDS")
    print(f"Works:      {db_work_count:,}")
    print(f"Passages:   {db_passage_count:,}")
    print(f"FTS:        {fts_count:,}")
    print()
    print("CORPUS")
    print(f"Words:      {total_words:,}")
    print(f"Characters: {total_chars:,}")
    print(f"Lines:      {total_lines:,}")
    print()
    print("VERIFICATION")
    print(f"Work count:       {'PASSED' if count_pass else 'FAILED'}")
    print(f"Passage count:    {'PASSED' if passage_pass else 'FAILED'}")
    print(f"Word count:       {'PASSED' if word_pass else 'FAILED'}")
    print(f"Character count:  {'PASSED' if char_pass else 'FAILED'}")
    print(f"Source integrity: {'PASSED' if source_pass else 'FAILED'}")
    print(f"SQLite integrity: {'PASSED' if sqlite_pass else 'FAILED'}")
    print(f"FTS search test:  {test_matches:,} matches")
    print(f"Overall:          {'PASSED' if overall else 'FAILED'}")
    print()
    print(f"Build time:       {elapsed:.1f} seconds")
    print(f"Report written to: {REPORT_PATH}")


if __name__ == "__main__":
    main()
