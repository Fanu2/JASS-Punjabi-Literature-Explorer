import sys
import sqlite3
import subprocess
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStatusBar,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)


APP_TITLE = "JASS Punjabi Literature Explorer v1.2"


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "JASS_Punjabi_Literature.db"
BUILDER_PATH = BASE_DIR / "JASS_Punjabi_Literature_Corpus_Builder_v1.0.py"


class Database:
    """Read-only access to the Punjabi Literature corpus."""

    def __init__(self, path):
        self.path = Path(path)

        if not self.path.exists():
            raise FileNotFoundError(
                f"Database not found:\n\n{self.path}"
            )

        uri = f"file:{self.path.as_posix()}?mode=ro"
        self.conn = sqlite3.connect(uri, uri=True)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        self.conn.close()

    def tables(self):
        rows = self.conn.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            ORDER BY name
            """
        ).fetchall()

        return [row["name"] for row in rows]

    def stats(self):
        result = {}

        queries = {
            "works": "SELECT COUNT(*) FROM works",
            "passages": "SELECT COUNT(*) FROM passages",
            "words": "SELECT COALESCE(SUM(word_count), 0) FROM works",
            "characters": "SELECT COALESCE(SUM(character_count), 0) FROM works",
        }

        for key, sql in queries.items():
            try:
                result[key] = self.conn.execute(sql).fetchone()[0]
            except sqlite3.Error:
                result[key] = 0

        return result

    def works(self):
        return self.conn.execute(
            """
            SELECT
                work_id,
                title,
                word_count,
                character_count
            FROM works
            ORDER BY work_id
            """
        ).fetchall()

    def passages_for_work(self, work_id):
        return self.conn.execute(
            """
            SELECT
                passage_id,
                work_id,
                paragraph_number,
                text,
                word_count
            FROM passages
            WHERE work_id = ?
            ORDER BY paragraph_number
            """,
            (work_id,),
        ).fetchall()

    def search(self, query, work_id=None):
        query = query.strip()

        if not query:
            return []

        # FTS5 search.
        if work_id is None:
            sql = """
                SELECT
                    p.passage_id,
                    p.work_id,
                    p.paragraph_number,
                    p.text,
                    w.title
                FROM passages_fts f
                JOIN passages p ON p.passage_id = f.rowid
                JOIN works w ON w.work_id = p.work_id
                WHERE passages_fts MATCH ?
                ORDER BY bm25(passages_fts)
                LIMIT 200
            """
            params = (query,)
        else:
            sql = """
                SELECT
                    p.passage_id,
                    p.work_id,
                    p.paragraph_number,
                    p.text,
                    w.title
                FROM passages_fts f
                JOIN passages p ON p.passage_id = f.rowid
                JOIN works w ON w.work_id = p.work_id
                WHERE passages_fts MATCH ?
                  AND p.work_id = ?
                ORDER BY bm25(passages_fts)
                LIMIT 200
            """
            params = (query, work_id)

        try:
            return self.conn.execute(sql, params).fetchall()
        except sqlite3.Error:
            # Fallback for ordinary text search.
            pattern = f"%{query}%"

            if work_id is None:
                return self.conn.execute(
                    """
                    SELECT
                        p.passage_id,
                        p.work_id,
                        p.paragraph_number,
                        p.text,
                        w.title
                    FROM passages p
                    JOIN works w ON w.work_id = p.work_id
                    WHERE p.text LIKE ?
                    ORDER BY p.passage_id
                    LIMIT 200
                    """,
                    (pattern,),
                ).fetchall()

            return self.conn.execute(
                """
                SELECT
                    p.passage_id,
                    p.work_id,
                    p.paragraph_number,
                    p.text,
                    w.title
                FROM passages p
                JOIN works w ON w.work_id = p.work_id
                WHERE p.work_id = ?
                  AND p.text LIKE ?
                ORDER BY p.passage_id
                LIMIT 200
                """,
                (work_id, pattern),
            ).fetchall()

    def passage(self, passage_id):
        return self.conn.execute(
            """
            SELECT
                p.*,
                w.title AS work_title
            FROM passages p
            JOIN works w ON w.work_id = p.work_id
            WHERE p.passage_id = ?
            """,
            (passage_id,),
        ).fetchone()


class ExplorerWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.db = Database(DB_PATH)
        self.current_work_id = None
        self.current_passages = []

        self.setWindowTitle(APP_TITLE)
        self.resize(1400, 850)

        self.build_ui()
        self.load_statistics()
        self.load_works()

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 8)
        main_layout.setSpacing(8)

        # ---------------------------------------------------------
        # Header
        # ---------------------------------------------------------

        header = QHBoxLayout()

        title = QLabel("JASS Punjabi Literature Explorer")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))

        version = QLabel("v1.1")
        version.setFrameStyle(QFrame.Panel | QFrame.Sunken)

        header.addWidget(title)
        header.addWidget(version)
        header.addStretch()

        main_layout.addLayout(header)

        # ---------------------------------------------------------
        # Search bar
        # ---------------------------------------------------------

        search_layout = QHBoxLayout()

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText(
            "Search Punjabi literature..."
        )
        self.search_box.returnPressed.connect(self.perform_search)

        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.perform_search)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_search)

        self.rescan_button = QPushButton("↻ Rescan")
        self.rescan_button.setToolTip(
            "Scan this folder for newly added .txt books and rebuild the library"
        )
        self.rescan_button.clicked.connect(self.rescan_library)

        self.scope_combo = QComboBox()
        self.scope_combo.addItem("All works", None)

        search_layout.addWidget(self.search_box, 1)
        search_layout.addWidget(self.scope_combo)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.clear_button)
        search_layout.addWidget(self.rescan_button)

        main_layout.addLayout(search_layout)

        # ---------------------------------------------------------
        # Main splitter
        # ---------------------------------------------------------

        splitter = QSplitter(Qt.Horizontal)

        # Left panel
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(4, 4, 4, 4)

        works_label = QLabel("LITERATURE")
        works_label.setFont(QFont("Segoe UI", 11, QFont.Bold))

        self.works_list = QListWidget()
        self.works_list.currentItemChanged.connect(
            self.work_selected
        )

        left_layout.addWidget(works_label)
        left_layout.addWidget(self.works_list)

        # Right panel
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(8, 4, 4, 4)

        self.reader_title = QLabel("Select a work")
        self.reader_title.setFont(QFont("Segoe UI", 14, QFont.Bold))

        self.reader_info = QLabel("")

        self.reader = QTextBrowser()
        self.reader.setOpenExternalLinks(False)
        self.reader.setLayoutDirection(Qt.RightToLeft)

        # Shahmukhi-friendly display.
        font = QFont("Noto Sans")
        font.setPointSize(15)
        self.reader.setFont(font)

        right_layout.addWidget(self.reader_title)
        right_layout.addWidget(self.reader_info)
        right_layout.addWidget(self.reader, 1)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([360, 1000])

        main_layout.addWidget(splitter, 1)

        # ---------------------------------------------------------
        # Statistics
        # ---------------------------------------------------------

        stats_layout = QHBoxLayout()

        self.stats_label = QLabel("Loading corpus...")
        self.stats_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)

        stats_layout.addWidget(self.stats_label, 1)

        readonly = QLabel("READ ONLY")
        readonly.setFrameStyle(QFrame.Panel | QFrame.Sunken)

        stats_layout.addWidget(readonly)

        main_layout.addLayout(stats_layout)

        # ---------------------------------------------------------
        # Status bar
        # ---------------------------------------------------------

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage(
            "Punjabi Literature Corpus loaded — click ↻ Rescan after adding books"
        )

    def load_statistics(self):
        stats = self.db.stats()

        self.stats_label.setText(
            f"Works: {stats['works']:,}    |    "
            f"Words: {stats['words']:,}    |    "
            f"Passages: {stats['passages']:,}    |    "
            f"Characters: {stats['characters']:,}"
        )

    def load_works(self):
        self.works_list.clear()

        self.scope_combo.blockSignals(True)
        self.scope_combo.clear()
        self.scope_combo.addItem("All works", None)

        works = self.db.works()

        for work in works:
            label = (
                f"{work['title']}  "
                f"({work['word_count']:,} words)"
            )

            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, work["work_id"])

            self.works_list.addItem(item)

            self.scope_combo.addItem(
                work["title"],
                work["work_id"],
            )

        self.scope_combo.blockSignals(False)

        self.statusBar().showMessage(
            f"{len(works)} works loaded"
        )

    def work_selected(self, current, previous):
        if current is None:
            return

        work_id = current.data(Qt.UserRole)
        self.current_work_id = work_id

        work = next(
            (
                row
                for row in self.db.works()
                if row["work_id"]
            ),
            None,
        )

        if work is None:
            return

        self.reader_title.setText(work["title"])

        self.current_passages = self.db.passages_for_work(
            work_id
        )

        self.reader_info.setText(
            f"{work['word_count']:,} words  |  "
            f"{len(self.current_passages):,} passages"
        )

        self.display_passages(self.current_passages)

        self.scope_combo.blockSignals(True)

        index = self.scope_combo.findData(work_id)

        if index >= 0:
            self.scope_combo.setCurrentIndex(index)

        self.scope_combo.blockSignals(False)

        self.statusBar().showMessage(
            f"Reading: {work['title']}"
        )

    def display_passages(self, passages):
        if not passages:
            self.reader.setHtml(
                "<p>No passages found.</p>"
            )
            return

        html_parts = []

        for passage in passages:
            text = (
                str(passage["text"])
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\n", "<br>")
            )

            html_parts.append(
                f"""
                <div dir="rtl"
                     style="
                     margin-bottom:24px;
                     line-height:1.8;
                     text-align:right;
                     ">
                    <div style="
                        font-size:10pt;
                        direction:ltr;
                        text-align:left;
                        opacity:0.6;
                        ">
                        Passage {passage['paragraph_number']}
                    </div>

                    <div style="
                        font-size:16pt;
                        margin-top:6px;
                        ">
                        {text}
                    </div>
                </div>
                """
            )

        self.reader.setHtml(
            "".join(html_parts)
        )

    def perform_search(self):
        query = self.search_box.text().strip()

        if not query:
            return

        work_id = self.scope_combo.currentData()

        results = self.db.search(
            query,
            work_id,
        )

        self.reader_title.setText(
            f"Search results: {query}"
        )

        self.reader_info.setText(
            f"{len(results):,} result(s)"
        )

        if not results:
            self.reader.setHtml(
                """
                <div dir="rtl"
                     style="font-size:16pt;text-align:right;">
                    کوئی نتیجہ نہیں ملا۔
                </div>
                """
            )

            self.statusBar().showMessage(
                "No search results"
            )
            return

        html_parts = []

        for result in results:
            text = (
                str(result["text"])
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\n", "<br>")
            )

            html_parts.append(
                f"""
                <div dir="rtl"
                     style="
                     margin-bottom:28px;
                     padding:10px;
                     border-bottom:1px solid #cccccc;
                     text-align:right;
                     ">

                    <div dir="ltr"
                         style="
                         font-size:10pt;
                         opacity:0.7;
                         ">
                        {result['title']}
                        — Passage {result['paragraph_number']}
                    </div>

                    <div style="
                         font-size:16pt;
                         line-height:1.8;
                         margin-top:8px;
                         ">
                        {text}
                    </div>
                </div>
                """
            )

        self.reader.setHtml(
            "".join(html_parts)
        )

        self.statusBar().showMessage(
            f"{len(results):,} result(s) found"
        )

    def rescan_library(self):
        """Rebuild the library database from .txt files in BASE_DIR."""
        if not BUILDER_PATH.exists():
            QMessageBox.critical(
                self,
                "Rescan Unavailable",
                "The corpus builder was not found.\n\n"
                f"Expected:\n{BUILDER_PATH}",
            )
            return

        old_title = None
        if self.current_work_id is not None:
            for row in self.db.works():
                if row["work_id"] == self.current_work_id:
                    old_title = row["title"]
                    break

        self.rescan_button.setEnabled(False)
        self.statusBar().showMessage(
            "Scanning folder and rebuilding literature library..."
        )
        QApplication.processEvents()

        try:
            # Close the read-only connection before the builder recreates
            # the SQLite database on Windows.
            self.db.close()

            # The builder scans .txt files. Hide its generated reports during
            # the scan so they are never mistaken for literature works.
            hidden_reports = []
            for report_name in (
                "punjabi_literature_inspection_report.txt",
                "punjabi_literature_build_report.txt",
            ):
                report_path = BASE_DIR / report_name
                if report_path.exists():
                    hidden_path = BASE_DIR / (report_name + ".rescan-hidden")
                    report_path.replace(hidden_path)
                    hidden_reports.append((report_path, hidden_path))

            try:
                result = subprocess.run(
                    [sys.executable, str(BUILDER_PATH)],
                    cwd=str(BASE_DIR),
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
            finally:
                for report_path, hidden_path in hidden_reports:
                    if hidden_path.exists():
                        hidden_path.replace(report_path)

            if result.returncode != 0:
                raise RuntimeError(
                    "The corpus builder failed.\n\n"
                    + (result.stderr.strip() or result.stdout.strip())
                )

            self.db = Database(DB_PATH)
            self.current_work_id = None
            self.current_passages = []

            self.load_statistics()
            self.load_works()

            # Restore the previously selected book when it still exists.
            if old_title:
                for i in range(self.works_list.count()):
                    item = self.works_list.item(i)
                    if self._work_title(item) == old_title:
                        self.works_list.setCurrentRow(i)
                        break

            stats = self.db.stats()
            self.statusBar().showMessage(
                f"Library rescanned successfully — "
                f"{stats['works']:,} works loaded"
            )

            QMessageBox.information(
                self,
                "Library Rescanned",
                "The literature folder has been rescanned successfully.\n\n"
                f"Works: {stats['works']:,}\n"
                f"Words: {stats['words']:,}\n"
                f"Passages: {stats['passages']:,}\n\n"
                "New .txt books in this folder are now available in the Explorer.",
            )

        except Exception as exc:
            try:
                self.db = Database(DB_PATH)
            except Exception:
                pass

            QMessageBox.critical(
                self,
                "Rescan Error",
                str(exc),
            )
            self.statusBar().showMessage("Rescan failed")

        finally:
            self.rescan_button.setEnabled(True)

    def _work_title(self, item):
        """Return the title represented by a literature list item."""
        work_id = item.data(Qt.UserRole)
        for row in self.db.works():
            if row["work_id"] == work_id:
                return row["title"]
        return None

    def clear_search(self):
        self.search_box.clear()

        if self.current_work_id is not None:
            self.current_passages = (
                self.db.passages_for_work(
                    self.current_work_id
                )
            )
            self.display_passages(
                self.current_passages
            )

            self.statusBar().showMessage(
                "Search cleared"
            )
        else:
            self.reader.clear()

    def closeEvent(self, event):
        self.db.close()
        event.accept()


def main():
    app = QApplication(sys.argv)

    app.setApplicationName(
        "JASS Punjabi Literature Explorer"
    )

    try:
        window = ExplorerWindow()
    except Exception as exc:
        QMessageBox.critical(
            None,
            "Startup Error",
            str(exc),
        )
        return 1

    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())