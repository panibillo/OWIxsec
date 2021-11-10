/* 
Definition of database tables defining legends for the MNcwixsec Well Cross-section drawing program.
Attributes correspond with plotting attributes in Python's Matplotlib package.

Tables are incomplete, but sufficient for running MNcwixsec demonstration scripts. 
For the demonstration, the legend database should be named "demo_data/xsec_Legend.sqlite"

Author: Bill Olsen
Date:   2021-11-09
Language: SQLite
*/

CREATE TABLE GROUT_polygon (
    rowid        INTEGER PRIMARY KEY,
    code         TEXT    UNIQUE
                         NOT NULL,
    label        TEXT,
    fillcolor    TEXT,
    patterncolor TEXT    DEFAULT ('#000000'),
    Pattern      TEXT,
    linecolor    TEXT    DEFAULT ('#000000'),
    linethick    REAL    DEFAULT (1),
    linestyle    TEXT    DEFAULT ('-') 
);

CREATE TABLE MISC_polygon (
    rowid        INTEGER PRIMARY KEY,
    layer        TEXT,
    code         TEXT    UNIQUE
                         NOT NULL,
    label        TEXT,
    fillcolor    TEXT,
    patterncolor TEXT    DEFAULT ('#000000'),
    Pattern      TEXT,
    linecolor    TEXT    DEFAULT ('#000000'),
    linethick    REAL    DEFAULT (1),
    linestyle    TEXT    DEFAULT ('-') 
);

CREATE TABLE MISC_polyline (
    rowid     INTEGER PRIMARY KEY,
    layer     TEXT,
    label     TEXT,
    linecolor TEXT    DEFAULT ('#000000'),
    linethick REAL    DEFAULT (1),
    linestyle TEXT    DEFAULT ('-') 
);

CREATE TABLE STRAT_polygon (
    rowid        INTEGER PRIMARY KEY,
    aqrank       TEXT,
    code         TEXT    UNIQUE
                         NOT NULL,
    label        TEXT,
    fillcolor    TEXT,
    patterncolor TEXT    DEFAULT ('#000000'),
    Pattern      TEXT,
    linecolor    TEXT    DEFAULT ('#000000'),
    linethick    REAL    DEFAULT (1),
    linestyle    TEXT    DEFAULT ('-') 
);

