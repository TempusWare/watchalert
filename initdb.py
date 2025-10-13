import sqlite3

con = sqlite3.connect("./products.db")
cur = con.cursor()
cur.execute(
    "CREATE TABLE IF NOT EXISTS products(id, title, url, price, image, notes, date, site, PRIMARY KEY (url, price))"
)
cur.execute(
    "CREATE TABLE IF NOT EXISTS watchlist(site, query, PRIMARY KEY (site, query))"
)
con.close()
