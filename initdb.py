import sqlite3

con = sqlite3.connect("./products.db")
cur = con.cursor()
cur.execute(
    "CREATE TABLE IF NOT EXISTS products(id, title, url, price, image, notes, date, site, channel, PRIMARY KEY (url, price, channel))"
)
cur.execute(
    "CREATE TABLE IF NOT EXISTS watchlist(site, query, channel, PRIMARY KEY (site, query, channel))"
)
cur.execute("CREATE TABLE IF NOT EXISTS faults(channel, PRIMARY KEY (channel))")
cur.execute("CREATE TABLE IF NOT EXISTS apikeys(site, key)")
con.close()
