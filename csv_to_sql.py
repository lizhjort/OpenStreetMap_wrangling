import pandas as pd
import sqlite3

conn = sqlite3.connect('example.db')

TABLES = ['nodes', 'nodes_tags', 'ways', 'ways_nodes', 'ways_tags']

for t in TABLES:
    df = pd.read_csv("{}.csv".format(t))
    df.to_sql(t, conn, if_exists='replace', index=False)


