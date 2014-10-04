#!/usr/bin/env python3

import psycopg2
import csv
from bhsdk import config

conn = psycopg2.connect(config.get('db', 'connect'))
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
        # except sqlite3.IntegrityError:
        #     # duplication
        #     pass
    conn.commit()

print('Total: %d, new added: %d' % (total, added))
