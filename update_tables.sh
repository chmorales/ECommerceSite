# !/bin/bash

# This script just runs the 'mysql_scripts/create_tables.sql' and 'mysql_scripts/populate_tables.sql' scripts.

set -e

MYSQL_PASS="tl35tl35"

mysql -u root -p"$MYSQL_PASS" < mysql_scripts/create_tables.sql
mysql -u root -p"$MYSQL_PASS" < mysql_scripts/populate_tables.sql