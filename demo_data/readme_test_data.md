# OWIxsec

A Python tool for drawing well cross sections using Minnesota CWI data 

## Demo data files and legend files.

Four files are provided:
-   `cwischema_c4.3.0.sql` : DDL statments (Table definitions) for data tables in a data source.
-   `OWI_demo_data.sql` : Demo data to be inserted into the data tables.
-   `xsec_Legend_DDL.sql` : DDL statements for a legend database
-   `xsec_Legend_data.sql` : Demo data for the legend database (designed for 
     the xsec_demo script).

The wells included in the demo data set are selected to illustrate:
-   A sampling of all of well components recorded in the CWI database that the 
    program currently knows how to draw,
-   How missing data is handled,
-   Well groups suitable for demonstrating the fenceline and projected line 
    options.

As of November, 2021, the demo data set is identical to the data set provided 
for the [OWI](https://github.com/panibillo/OWI.git) project on github.

The legend definitions are not complete, but are sufficient to run the demos, 
and to illustrate a possible method of providing legend definitions from 
scratch for use with matplotlib as the drawing tool.

## To create the tables and read in the data using SQLite Studio

-   Obtain  SQLite Studio from [here](https://sqlitestudio.pl/).
-   Open *SQLite Studio*.
-   Create new database(s). For the xsec_demo script, these should be named: 
>> `<your_path>/MNxsec/db/OWI_demo.sqlite`
>> `<your_path>/MNxsec/db/xsec_legend.sqlite`
-   Open an SQL editor window (`Alt + E`).
-   Copy and paste the DDL statments into the editor window and execute them all. 
-   Copy and paste the demo data queries into the editor window and execute them all. 
-   You can choose to execute queries individually by placing the cursor in the 
    query and pressing the execute button, or (`F9`). 
    Or you can execute them all by changing the `Tools/Configuration` (`F2`) 
    settings:  uncheck `Execute only the query under the cursor`. 

