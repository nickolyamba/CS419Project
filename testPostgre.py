#!C:\python27_x64
#
# Small script to show PostgreSQL and Pyscopg together
# https://api.elephantsql.com/sso/469d9185-77f8-411a-ac0e-69f59803905e/mgmt
# https://wiki.postgresql.org/wiki/Psycopg2_Tutorial

import psycopg2

try:
    conn = psycopg2.connect("dbname='muepyavy' user='muepyavy' host='babar.elephantsql.com' password='EQoh7fJJNxK-4ag4SNUIYwzzWqTVzj-8'")
except:
    print "I am unable to connect to the database"

cur = conn.cursor()
#cur.execute("""SELECT datname from pg_database""")
#rows = cur.fetchall()
#print "\nShow me the databases:\n"
#for row in rows:
#    print "   ", row[0]
cur.execute("""SELECT * from company""")
rows = cur.fetchall()
print "\nShow me the databases:\n"
for row in rows:
    print "   ", row[1]
print rows
