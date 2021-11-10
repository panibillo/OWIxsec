/* 
Data for database tables defining legends for the MNcwixsec Well Cross-section drawing program.

Tables are defined in xsec_Legend_DDL.sql.
Tables and data are incomplete, but are sufficient for running MNcwixsec demonstrations. 
Attributes correspond with plotting attributes in Python's Matplotlib package.

For the demonstrations, the legend database should be named "demo_data/xsec_Legend.sqlite"

Author: Bill Olsen
Date:   2021-11-09
Language: SQL 
*/

-- Table: GROUT_polygon -------------------------------------------------------
INSERT INTO GROUT_polygon (rowid, code, label, fillcolor, patterncolor, Pattern, linecolor, linethick, linestyle) 
VALUES 
(1, 'B', 'bentonite', '#bbbbbb', NULL, NULL, NULL, 0.0, NULL),
(2, 'C', 'cuttings', '#bbbbbb', NULL, NULL, NULL, 0.0, NULL),
(3, 'D', 'driven casing seal', '#bbbbbb', NULL, NULL, NULL, 0.0, NULL),
(4, 'E', 'concrete', '#bbbbbb', NULL, NULL, NULL, 0.0, NULL),
(5, 'G', 'neat cement', '#bbbbbb', NULL, NULL, NULL, 0.0, NULL),
(6, 'H', 'high solids bentonite', '#bbbbbb', NULL, NULL, NULL, 0.0, NULL),
(7, 'N', 'well known to be not grouted', '#bbbbbb', NULL, NULL, NULL, 0.0, NULL),
(8, 'O', 'other', '#bbbbbb', NULL, NULL, NULL, 0.0, NULL),
(9, 'P', 'pearock', '#bbbbbb', NULL, NULL, NULL, 0.0, NULL),
(10, 'S', 'cement-sand', '#bbbbbb', NULL, NULL, NULL, 0.0, NULL),
(11, 'Y', 'well grouted, type unknown', '#bbbbbb', NULL, NULL, NULL, 0.0, NULL);


-- Table: MISC_polygon -------------------------------------------------------
INSERT INTO MISC_polygon (rowid, layer, code, label, fillcolor, patterncolor, Pattern, linecolor, linethick, linestyle) 
VALUES 
(1, 'PERF', 'PERF', 'Perforation', '#eeeeee', '#080808', '+++', '#eeeeee', 0.2, '-'),
(2, 'HFRAC', 'HFRAC', 'Hydrofrac interval', '#22ffaa', '#080808', 'oo', '#22ff00', 0.2, '-'),
(3, 'CASING', 'CASE', 'Casing', '#000000', '#000000', NULL, '#000000', 0.0, '-');

-- Table: MISC_polyline -------------------------------------------------------
INSERT INTO MISC_polyline (rowid, layer, label, linecolor, linethick, linestyle) 
VALUES 
(1, 'casing', NULL, '#000000', 2.0, '-'),
(2, 'swl', NULL, '#0505ff', 2.0, '-'),
(3, 'bdrk', NULL, '#080808', 2.0, '-'),
(4, 'screen', NULL, '#009900', 2.0, 'dotted');

-- Table: STRAT_polygon -------------------------------------------------------
INSERT INTO STRAT_polygon (rowid, aqrank, code, label, fillcolor, patterncolor, Pattern, linecolor, linethick, linestyle) 
VALUES 
(1, 'AA', 'QUUU', 'Unconsolidated', '#ed9b37', '#000000', NULL, '#000000', 0.2, '-'),
(2, 'AA', 'QFUU', 'Sand', '#edc937', '#d1982e', NULL, '#000000', 0.2, '-'),
(3, 'AA', 'QGUU', 'Gravel', '#fcd63a', '#db9130', NULL, '#000000', 0.2, '-'),
(4, 'CC', 'OGAL', 'Galena', '#f75252', '#000000', NULL, '#000000', 0.2, '-'),
(5, 'DD', 'ODCR', 'Decorah', '#3dff69', '#000000', NULL, '#000000', 0.2, '-'),
(6, 'DE', 'ODPL', 'Decorah-Platteville', '#80ffff', '#3dff69', '//', '#000000', 0.2, '-'),
(7, 'EE', 'OPVL', 'Platteville', '#80ffff', '#000000', NULL, '#000000', 0.2, '-'),
(8, 'EF', 'OPGD', 'Platteville-Glenwood', '#5fe8b4', '#80ffff', '//', '#000000', 0.2, '-'),
(9, 'FF', 'OGWD', 'Glenwood', '#5fe8b4', '#000000', NULL, '#000000', 0.2, '-'),
(10, 'FH', 'OGSP', 'Glenwood-St Peter', '#feffbf', '#5fe8b4', '//', '#000000', 0.2, '-'),
(11, 'HH', 'OSTP', 'St Peter', '#feffbf', '#000000', NULL, '#000000', 0.2, '-'),
(12, 'HI', 'OSPC', 'St Peter Prairie du Chien', '#1365df', '#feffbf', '/', '#000000', 0.2, '-'),
(13, 'II', 'OPDC', 'Prairie du Chien', '#1365df', '#000000', NULL, '#000000', 0.2, '-'),
(14, 'IJ', 'OPCJ', 'Prairie du Chien-Jordan', '#fff52a', '#1365df', '//', '#000000', 0.2, '-'),
(15, 'JJ', 'CJDN', 'Jordan', '#fff52a', '#000000', NULL, '#000000', 0.2, '-'),
(16, 'JL', 'CJSL', 'Jordan-St Lawrence', '#54ff99', '#fff52a', '//', '#000000', 0.2, '-'),
(17, 'LL', 'CSTL', 'St Lawrence', '#54ff99', '#000000', NULL, '#000000', 0.2, '-'),
(18, 'LM', 'CSLF', 'St Lawrence-Franconia', '#5effcc', '#54ff99', '//', '#000000', 0.2, '-'),
(19, 'MM', 'CFRN', 'Franconia', '#5effcc', '#000000', NULL, '#000000', 0.2, '-'),
(20, 'NO', 'CIGL', 'Ironton-Galesville', '#20e8cd', '#000000', NULL, '#000000', 0.2, '-'),
(21, 'OO', 'CGSL', 'Galesville', '#20e8cd', '#000000', NULL, '#000000', 0.2, '-'),
(22, 'PP', 'CECR', 'Eau Claire', '#9bba0d', '#000000', NULL, '#000000', 0.2, '-'),
(23, 'RR', 'CMTS', 'Mount Simon', '#e5eb49', '#000000', NULL, '#000000', 0.2, '-'),
(24, 'RS', 'CMSH', 'Mount Simon-Hinckley', '#e5eb49', '#000000', NULL, '#000000', 0.2, '-'),
(25, 'TT', 'CAMB', 'Cambrian', '#ffadec', '#000000', NULL, '#000000', 0.2, '-'),
(26, 'U', 'MULT', 'Multiple Aquifer', '#ffffff', '#000000', '//', '#000000', 0.2, '-'),
(27, '0', 'PITT', 'Pit', '#f7f7f7', '#000000', NULL, '#000000', 0.2, '-'),
(28, 'Z', 'UNCL', 'Unclassified', '#ffffff', '#000000', NULL, '#000000', 0.2, '-'),
(29, 'Z', 'NRCD', 'No Record', '#ffffff', '#000000', NULL, '#000000', 0.2, '-'),
(30, '0', 'RUUU', 'Recent', '#808080', '#000000', NULL, '#000000', 0.2, '-'),
(31, 'AA', 'QCUU', 'Clay', '#a9c42d', '#000000', NULL, '#000000', 0.2, '-'),
(32, 'EF', 'OPGW', 'Platteville-Glenwood', '#5fe8b4', '#80ffff', '//', '#000000', 0.2, '-'),
(33, '1', 'RMMF', 'Recent Manmade Fill', '#808080', '#000000', NULL, '#000000', 0.2, '-'),
(35, 'AA', 'QLUU', NULL, '#fcd63a', '#db9130', NULL, '#000000', 0.2, '-'),
(36, 'AA', 'QGUB', NULL, '#fcd63a', '#db9130', NULL, '#000000', 0.2, NULL),
(37, 'YY', 'missing', 'Missing code', '#cccccc', '#000000', NULL, '#000000', 0.2, '-'),
(38, NULL, 'PEVT', 'PEVT', '#cc22bb', '''#000000''', NULL, '#000000', 1.0, '-'),
(39, NULL, 'QCUB', 'QCUB', '#a9c42d', '''#000000''', NULL, '#000000', 1.0, '-'),
(40, NULL, 'QCUR', 'QCUR', '#a9c42d', '''#000000''', NULL, '#000000', 1.0, '-'),
(41, NULL, 'QFUB', 'QFUB', '#a9c42d', '#000000', NULL, '#000000', 0.2, '-'),
(42, NULL, 'QFUG', 'QFUG', '#a9c42d', '#000000', NULL, '#000000', 0.2, '-'),
(43, NULL, 'QIUB', 'QIUB', '#a9c42d', '#000000', NULL, '#000000', 0.2, '-'),
(44, NULL, 'QNUB', 'QNUB', '#a9c42d', '#000000', NULL, '#000000', 0.2, '-'),
(45, NULL, 'QPUR', 'QPUR', '#a9c42d', '#000000', NULL, '#000000', 0.2, '-');

