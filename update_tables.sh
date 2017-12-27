# !/bin/bash

# This script just runs the 'mysql_scripts/create_tables.sql' and 'mysql_scripts/populate_tables.sql' scripts.

set -e

MYSQL_USER="default"
MYSQL_PASS="default"

mysql -u $MYSQL_USER -p"$MYSQL_PASS" < mysql_scripts/create_tables.sql
mysql -u $MYSQL_USER -p"$MYSQL_PASS" < mysql_scripts/populate_tables.sql