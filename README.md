<img width="1902" height="982" alt="image" src="https://github.com/user-attachments/assets/23829f33-5c83-43dc-b9e3-ea9c0f9adee4" />

# JASS Punjabi Literature Explorer

**Version:** v1.1\
**Project:** JASS Punjabi Literature Tools\
**Purpose:** Local, read-only exploration and search of a Punjabi
literary corpus\
**Technology:** Python 3.14+ · PySide6 · SQLite · SQLite FTS5\
**Mode:** Offline / Local / Read Only

------------------------------------------------------------------------

## 1. Overview

**JASS Punjabi Literature Explorer** is a lightweight desktop
application for browsing and searching a locally built Punjabi
literature corpus.

It provides a simple reading-oriented interface over the SQLite database
produced by the **JASS Punjabi Literature Corpus Builder**.

The Explorer is deliberately designed as a **read-only consumer** of the
corpus database:

-   It does not edit the source `.txt` works.
-   It does not write to the SQLite database.
-   It opens the database using SQLite read-only mode.
-   It provides browsing by literary work.
-   It provides full-text search across the corpus.
-   It can restrict searches to a selected work.
-   It displays Shahmukhi/Arabic-script Punjabi in a right-to-left
    reading layout.
-   It keeps the corpus entirely local.

The result is a small personal Punjabi literature library that can be
searched and read without requiring an internet connection or a cloud
service.

------------------------------------------------------------------------

# 2. Current Corpus

The current corpus was inspected and then built into SQLite.

### Corpus summary

  Item                                                   Value
  ---------------------------------- -------------------------
  Literary works                                            23
  Total words in source works                          992,364
  Total characters in source works                   4,669,933
  SQLite works records                                      24
  SQLite passages                                        1,117
  FTS records                                            1,117
  Database size                         approximately 11.55 MB
  Source encoding                      recorded by the Builder
  Source integrity                            SHA-256 verified
  SQLite integrity                                    verified
  FTS search test                                       passed

### Why the database reports 24 works

The original literature collection contains **23 literary text files**.

The Builder also included:

``` text
punjabi_literature_inspection_report.txt
```

as a source record because it was a `.txt` file present in the corpus
directory when the database was built.

Therefore the SQLite database currently contains:

``` text
23 literary works
+
1 inspection/report text
=
24 work records
```

If the goal is eventually to make a clean literary-only corpus, the
inspection and build reports should be excluded from a future corpus
build. This is a corpus-builder policy decision rather than an Explorer
requirement.

------------------------------------------------------------------------

# 3. Included Literary Works

The current source collection contains these 23 literature files:

1.  `01-Adyan Wichkar Gallan Baatan - 7200 W.txt`
2.  `02-Ahmad Nadeem Qasmi Stories - 23200 W.txt`
3.  `03-Al Ghaz Walfikhree - 32300 W.txt`
4.  `04-Alaao Novel - 36000.txt`
5.  `05-Allah dy Ik hon da matlab - 7200 W.txt`
6.  `06-Anjane Khauf Afsany - 85800 W.txt`
7.  `07-Apny Dukh Menu dy deyo - 10200 W.txt`
8.  `08-Deen diyan Gallaan - 40700 W.txt`
9.  `09-Urdu chunvy Afsanyan da Punjabi Tarjama - 152900 W.txt`
10. `10-Magharbi Tamadan di Ik jhalak - 53900 W.txt`
11. `11-Mumtaz Mufti dy afsaniyan da punjabi tarjama - 62250 W.txt`
12. `12-Noori-Afsana-9400 W.txt`
13. `13-Haneriyan diyan kahaniyan - 51900 W.txt`
14. `14-Bacheyan lai kahaniyan - 29800 W.txt`
15. `15-Punjabi Stories - 10900 W.txt`
16. `16-Punjabi Stories for Children Alphabatically - 26400 W.txt`
17. `17-Asli Shehad and stories - 9100 W.txt`
18. `18-Apny Hamsafar - 14800 W.txt`
19. `19-Punjabi Daramy - Translated - 128400 W.txt`
20. `20-Punjabi Daramy-2 - Translated - 112400 W.txt`
21. `21-Putar Sun Kahani - 38000 W.txt`
22. `22-Ag e Ag - Punjabi - 15000 W.txt`
23. `23-Aan Zaban ty jaan - 30900 W.txt`

The Explorer does not modify these source files.

------------------------------------------------------------------------

# 4. Project Files

A typical corpus directory looks like this:

``` text
1762611761169-MEDIAMEN's Punjabi Literature Corpus/
│
├── 01-Adyan Wichkar Gallan Baatan - 7200 W.txt
├── 02-Ahmad Nadeem Qasmi Stories - 23200 W.txt
├── ...
├── 23-Aan Zaban ty jaan - 30900 W.txt
│
├── JASS_Punjabi_Literature_Corpus_Builder_v1.0.py
├── JASS_Punjabi_Literature_Explorer_v1.1.py
│
├── JASS_Punjabi_Literature.db
│
├── punjabi_literature_inspection_report.txt
└── punjabi_literature_build_report.txt
```

The Explorer expects the database to be located beside the Python
application:

``` text
JASS_Punjabi_Literature_Explorer_v1.1.py
JASS_Punjabi_Literature.db
```

The database path is determined automatically from the location of the
Explorer script.

------------------------------------------------------------------------

# 5. Requirements

## Operating system

The application is intended to run on a normal desktop Windows
installation and does not require a GPU.

The current development environment uses:

``` text
Windows
Python 3.14.x
```

## Hardware

The Explorer is lightweight.

A system with:

-   8 GB RAM
-   no dedicated GPU

is sufficient for this application.

The Explorer itself does not run an AI model. It reads SQLite data and
performs text search.

------------------------------------------------------------------------

# 6. Python Dependencies

The application uses:

### Standard library

``` text
sys
sqlite3
pathlib
```

### External dependency

``` text
PySide6
```

SQLite is included with Python.

There is no requirement for:

-   PyTorch
-   Fairseq
-   CUDA
-   Ollama
-   an embedding model
-   an internet connection

for the Explorer.

This makes it substantially simpler than the Punjabi transliteration
model environment.

------------------------------------------------------------------------

# 7. Installation

Create or activate the Python environment you want to use.

For example:

``` powershell
cd "C:\Users\singh\Downloads\1762611761169-MEDIAMEN's Punjabi Literature Corpus"
```

Install PySide6 if necessary:

``` powershell
py -m pip install PySide6
```

Then verify:

``` powershell
py -c "import PySide6; print(PySide6.__version__)"
```

------------------------------------------------------------------------

# 8. Running the Explorer

From the corpus directory:

``` powershell
py .\JASS_Punjabi_Literature_Explorer_v1.1.py
```

The Explorer automatically looks for:

``` text
JASS_Punjabi_Literature.db
```

in the same directory as the Python script.

If the database is missing, the application displays a startup error.

------------------------------------------------------------------------

# 9. User Interface

The Explorer has four main areas.

## 9.1 Header

The header identifies the application:

``` text
JASS Punjabi Literature Explorer
v1.1
```

------------------------------------------------------------------------

## 9.2 Search Bar

The search area contains:

-   search input
-   search scope selector
-   Search button
-   Clear button

The search can be performed by pressing **Enter** or clicking
**Search**.

------------------------------------------------------------------------

## 9.3 Literature Panel

The left panel lists the available works.

Each work displays its title and word count, for example:

``` text
19-Punjabi Daramy - Translated - 128400 W
(128,469 words)
```

Selecting a work loads its passages into the reader.

------------------------------------------------------------------------

## 9.4 Reader Panel

The right panel displays the selected work.

The reader shows:

-   work title
-   word count
-   passage count
-   passage text
-   passage number

Shahmukhi/Arabic-script Punjabi is displayed using a right-to-left
layout.

The reader uses a relatively large font and increased line spacing to
make long Punjabi passages comfortable to read.

------------------------------------------------------------------------

# 10. Searching the Corpus

The Explorer uses the SQLite **FTS5** full-text search index when
available.

A search such as:

``` text
پنجابی
```

can be performed across the corpus.

The search returns up to **200 results**.

Each result identifies:

``` text
Work title
Passage number
Matching passage text
```

------------------------------------------------------------------------

# 11. Search Scope

The scope selector provides:

``` text
All works
```

plus each individual work.

For example:

``` text
All works
01-Adyan Wichkar Gallan Baatan
02-Ahmad Nadeem Qasmi Stories
...
19-Punjabi Daramy - Translated
...
23-Aan Zaban ty jaan
```

This allows two useful modes:

### Corpus-wide search

``` text
All works
```

Useful for discovering where a word or phrase appears throughout the
collection.

### Work-specific search

Select one work before searching.

Useful for investigating a particular novel, story collection, drama
collection, or other work.

------------------------------------------------------------------------

# 12. FTS5 and Fallback Search

The Explorer first attempts SQLite FTS5 search.

The relevant database structure is:

``` text
works
passages
passages_fts
```

The Explorer joins the FTS result back to the actual passage and work
records.

If SQLite reports an FTS search error, the application falls back to an
ordinary SQL `LIKE` search.

This makes the search interface more tolerant of queries that are not
accepted by FTS5 syntax.

The fallback search is also limited to 200 results.

------------------------------------------------------------------------

# 13. Database Schema

The Explorer was aligned to the actual database schema produced by the
JASS Literature Corpus Builder.

## `works`

The current table contains:

``` text
work_id
filename
title
size_bytes
encoding
word_count
character_count
line_count
paragraph_count
gurmukhi_characters
arabic_script_characters
sha256
```

The primary key is:

``` text
work_id
```

------------------------------------------------------------------------

## `passages`

The current table contains:

``` text
passage_id
work_id
paragraph_number
source_line_start
source_line_end
text
word_count
```

The primary key is:

``` text
passage_id
```

and `work_id` relates passages to their parent work.

------------------------------------------------------------------------

## `passages_fts`

The FTS table provides full-text search over the passage content.

The Explorer connects FTS rows to passages using:

``` text
passages_fts.rowid
        ↓
passages.passage_id
```

and then connects passages to works using:

``` text
passages.work_id
        ↓
works.work_id
```

This relationship is central to the Explorer.

------------------------------------------------------------------------

# 14. Read-Only Design

The Explorer deliberately opens SQLite using:

``` text
mode=ro
```

This means the application requests a read-only database connection.

The Explorer does not contain database write operations for:

-   INSERT
-   UPDATE
-   DELETE
-   schema modification
-   FTS rebuilding
-   corpus editing

The intended architecture is:

``` text
Source TXT files
      │
      ▼
Corpus Builder
      │
      ▼
SQLite database
      │
      ▼
Literature Explorer
```

The Explorer is the **reader layer**, not the corpus-authoring layer.

------------------------------------------------------------------------

# 15. Why Read-Only Matters

The corpus represents a valuable local collection of Punjabi literature.

Keeping the Explorer read-only provides an important safety boundary.

The user can freely:

-   browse
-   search
-   inspect
-   experiment with the UI

without worrying that a mistake in the Explorer will alter the corpus.

Any corpus changes should be made through a controlled Builder or a
separate corpus-processing tool.

------------------------------------------------------------------------

# 16. Corpus Builder Relationship

The Explorer is intended to work with:

``` text
JASS_Punjabi_Literature_Corpus_Builder_v1.0.py
```

The Builder is responsible for:

-   discovering source text files
-   calculating SHA-256 hashes
-   reading source metadata
-   counting words and characters
-   creating the SQLite database
-   creating passages
-   creating the FTS index
-   verifying database integrity

The Explorer is responsible for:

-   opening the resulting database
-   presenting works
-   displaying passages
-   searching text
-   providing a reading interface

This separation keeps corpus construction and corpus consumption
independent.

------------------------------------------------------------------------

# 17. Verification Already Completed

The current database build completed successfully.

The Builder reported:

``` text
Work count:       PASSED
Passage count:    PASSED
Word count:       PASSED
Character count:  PASSED
Source integrity: PASSED
SQLite integrity: PASSED
FTS search test:  305 matches
Overall:          PASSED
```

Build time was approximately:

``` text
2.1 seconds
```

The database size was approximately:

``` text
11.55 MB
```

------------------------------------------------------------------------

# 18. Example Workflow

A normal reading session can be:

``` text
1. Start Explorer
2. Choose a literary work
3. Read the Shahmukhi passages
4. Enter a Punjabi word or phrase
5. Choose "All works" or a particular work
6. Press Search
7. Inspect the matching passages
8. Press Clear
9. Continue reading
```

This turns the collection from a directory full of `.txt` files into a
searchable personal literature library.

------------------------------------------------------------------------

# 19. Practical Uses

The current Explorer is already useful for several kinds of work.

## Literature reading

Read long Shahmukhi works without opening individual text files.

## Word discovery

Find occurrences of a Punjabi word throughout the collection.

## Comparative reading

Search the same word or phrase across different works.

## Literary research

Locate passages of interest quickly.

## Punjabi language study

Observe vocabulary and usage in real literary contexts.

## Transliteration research

The Shahmukhi-heavy corpus provides useful material for future
Gurmukhi/Shahmukhi experiments.

## Corpus development

The SQLite database provides a structured foundation for future Punjabi
language tools.

------------------------------------------------------------------------

# 20. Future Possibilities

The Explorer should remain intentionally simple at the current
checkpoint.

However, the corpus provides a strong foundation for future
**separate/additive tools**.

Possible future components include:

``` text
JASS Punjabi Literature
│
├── Literature Explorer
│
├── Punjabi Concordance
│
├── Word Frequency Analyzer
│
├── Vocabulary Explorer
│
├── Gurmukhi ↔ Shahmukhi Workspace
│
├── Transliteration Evaluation Tool
│
├── Literary Search Tool
│
├── Corpus Statistics Dashboard
│
└── Local Punjabi RAG / Research Assistant
```

These should be considered extensions around the corpus rather than
reasons to make the current Explorer unnecessarily complex.

------------------------------------------------------------------------

# 21. Transliteration Model Connection

A separate Punjabi transliteration project is also available in the
user's environment, including a Gurmukhi-to-Shahmukhi Fairseq
checkpoint.

That model and this literature corpus serve different purposes.

### Transliteration model

``` text
Gurmukhi
   ↓
NMT model
   ↓
Shahmukhi
```

### Literature Explorer

``` text
SQLite corpus
   ↓
Search / Browse / Read
```

A future tool could combine them:

``` text
Punjabi Literature
       ↓
Explorer
       ↓
Select passage
       ↓
Gurmukhi ↔ Shahmukhi conversion
       ↓
Compare / evaluate / save result
```

That would be a natural future project, but it is not required for the
current Explorer.

------------------------------------------------------------------------

# 22. Offline and Privacy Characteristics

The Explorer is designed for local use.

It does not require:

-   cloud APIs
-   online search
-   external databases
-   user accounts
-   remote AI services

The literary text remains on the user's computer.

This is particularly appropriate for a personal literature collection.

------------------------------------------------------------------------

# 23. Performance Expectations

The current corpus is approximately one million words and only about
11.55 MB as SQLite.

For this scale, SQLite is a very appropriate storage layer.

The FTS5 index allows the Explorer to search the corpus without loading
the entire collection into memory.

The application also limits search results to 200 records, preventing
extremely large result sets from overwhelming the reader panel.

------------------------------------------------------------------------

# 24. Troubleshooting

## Error: Database not found

Make sure these two files are together:

``` text
JASS_Punjabi_Literature_Explorer_v1.1.py
JASS_Punjabi_Literature.db
```

Then run the Explorer from that directory.

------------------------------------------------------------------------

## Error: No module named `PySide6`

Install PySide6:

``` powershell
py -m pip install PySide6
```

------------------------------------------------------------------------

## Explorer opens but search fails

The Explorer first tries FTS5 and automatically attempts a `LIKE`
fallback when SQLite reports an FTS error.

If a particular query still behaves unexpectedly, try a simpler Punjabi
word or phrase.

------------------------------------------------------------------------

## Punjabi characters display incorrectly

Check the Windows/Python environment and available fonts.

The Explorer requests:

``` text
Noto Sans
```

for the reading panel.

A suitable Punjabi/Arabic-script font can improve rendering.

------------------------------------------------------------------------

# 25. Important Development Note

The database schema is the authoritative interface between the Builder
and Explorer.

The Explorer must use the actual schema names:

``` text
works.work_id
passages.passage_id
passages.work_id
passages.paragraph_number
```

It must not assume generic column names such as:

``` text
works.id
passages.id
passages.passage_number
```

The v1.1 Explorer was specifically aligned to the actual database schema
after this mismatch caused the original startup error:

``` text
no such column: id
```

This is an important compatibility lesson for future JASS tools.

------------------------------------------------------------------------

# 26. Current Version Boundary

## JASS Punjabi Literature Explorer v1.1

The current release establishes:

-   working SQLite connection
-   read-only database access
-   corpus statistics
-   literature list
-   work selection
-   passage display
-   RTL Shahmukhi rendering
-   corpus-wide search
-   work-specific search
-   FTS5 search
-   fallback `LIKE` search
-   search result display
-   clear/search workflow

The Explorer should be treated as a **working baseline** before adding
larger features.

------------------------------------------------------------------------

# 27. Recommended Future Development Policy

The best next step is not to turn the Explorer into a huge application.

A proportional approach is preferable:

``` text
Explorer
   │
   ├── Keep stable
   │
   ├── Fix verified bugs
   │
   └── Add only high-value reading/search features
```

More experimental capabilities should preferably become separate JASS
tools using the same SQLite corpus.

This keeps the literature database reusable across multiple
applications.

------------------------------------------------------------------------

# 28. Suggested Next-Level Tools

If the corpus proves useful, the following projects would provide high
value without destabilizing the Explorer.

### 1. JASS Punjabi Concordance

Show a searched word with surrounding context:

``` text
... previous words ...
TARGET WORD
... following words ...
```

across all works.

### 2. JASS Punjabi Word Frequency Analyzer

Produce statistics such as:

``` text
word
frequency
works containing word
passages containing word
```

### 3. JASS Punjabi Vocabulary Explorer

Allow a researcher to inspect the vocabulary of individual works.

### 4. JASS Gurmukhi-Shahmukhi Workspace

Use the literature corpus together with the transliteration model for
controlled experiments.

### 5. JASS Punjabi Corpus RAG

Use SQLite/FTS as the retrieval layer for a local research assistant.

The important principle is that these can all share the same corpus
database.

------------------------------------------------------------------------

# 29. Project Philosophy

The JASS Punjabi Literature Explorer follows a few simple principles:

### Local first

The corpus should remain usable without the internet.

### Read only

The Explorer should not accidentally damage the source corpus.

### Simple tools

A literature reader does not need to become a giant application.

### Reusable data

The SQLite corpus should be useful to many future tools.

### Search before AI

The structured corpus and FTS index provide a strong deterministic
foundation before introducing AI.

### Preserve provenance

The Builder records source metadata and SHA-256 hashes so that the
corpus can be traced back to its source files.

------------------------------------------------------------------------

# 30. Quick Start

For everyday use:

``` powershell
cd "C:\Users\singh\Downloads\1762611761169-MEDIAMEN's Punjabi Literature Corpus"

py .\JASS_Punjabi_Literature_Explorer_v1.1.py
```

Then:

``` text
Select a work
       ↓
Read
       ↓
Search when needed
       ↓
Clear
       ↓
Continue reading
```

------------------------------------------------------------------------

# 31. Project Status

**Status: WORKING BASELINE**

The Explorer is functional and already provides a practical interface to
a substantial Punjabi literary collection.

The current milestone should be preserved as a stable checkpoint before
significant feature expansion.

------------------------------------------------------------------------

# 32. Files Associated With This Project

``` text
JASS_Punjabi_Literature_Explorer_v1.1.py
JASS_Punjabi_Literature.db
JASS_Punjabi_Literature_Corpus_Builder_v1.0.py
punjabi_literature_inspection_report.txt
punjabi_literature_build_report.txt
```

------------------------------------------------------------------------

## Final Summary

JASS Punjabi Literature Explorer v1.1 turns a collection of Punjabi text
files into a **local, searchable, structured literature library**.

At the current checkpoint, the project provides:

> **23 literary works · \~992K literary words · 1,117 passages · SQLite
> · FTS5 · RTL Shahmukhi reading · read-only access · completely local
> operation**

The most important achievement is not the GUI alone. It is the
separation of:

``` text
Punjabi literary corpus
        +
structured SQLite representation
        +
search index
        +
simple reader
```

That creates a reusable foundation for future Punjabi language,
literature, transliteration, and research tools while keeping the
current Explorer small, safe, and maintainable.
