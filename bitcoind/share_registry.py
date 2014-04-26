#!/usr/bin/env python3
import sqlite3
import csv
from bhsdk import config

conn = sqlite3.connect(config.get('sqlite3', 'db_file'))
c = conn.cursor()

total = 0
added = 0
with open('share_registry.csv') as f:
    reader = csv.reader(f)

    c.execute('DELETE FROM share_registry')
    for uid, shares in reader:
        total += 1
        try:
            c.execute('INSERT INTO share_registry VALUES(\'%s\', %s)' % (uid, shares))
            added += 1
        except sqlite3.IntegrityError:
            # duplication
            pass
    conn.commit()

print('Total: %d, new added: %d' % (total, added))
