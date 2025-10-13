import os
import requests
import json
import sqlite3
import urllib.parse
import re
from datetime import datetime
import discord
import dotenv

dotenv.load_dotenv()
token = str(os.getenv("TOKEN"))

con = sqlite3.connect("./products.db")
cur = con.cursor()

today = datetime.today().strftime("%Y-%m-%d %H:%M:%S")


def scrape_link(site: str, query: str):
    encoded_query = urllib.parse.quote_plus(query)
    match site:
        case "cashconverters":
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.5",
                # 'Accept-Encoding': 'gzip, deflate, br, zstd',
                "Referer": "https://www.cashconverters.com.au/search-results?Sort=newest&page=1&f%5Bcategory%5D%5B0%5D=all&f%5Blocations%5D%5B0%5D=all&query="
                + encoded_query,
                "Sec-GPC": "1",
                "Alt-Used": "www.cashconverters.com.au",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                # Requests doesn't support trailers
                # 'TE': 'trailers',
            }

            params = {
                "Sort": "newest",
                "page": "1",
                "query": query,
            }

            response = requests.get(
                "https://www.cashconverters.com.au/c3api/search/results",
                params=params,
                headers=headers,
            )

            if response.status_code != 200:
                return

            data_response = response.text
            data_parsed = json.loads(data_response)
            items = data_parsed["Value"]["ProductList"]["ProductListItems"]

            data_insert = []

            for i in items:
                item = (
                    i["Code"],
                    i["Title"],
                    "https://www.cashconverters.com.au" + i["Url"],
                    i["Rrp"] + "+" + i["ShippingCost"],
                    i["AbsoluteImageUrl"],
                    i["StoreNameWithState"],
                    today,
                    site,
                )

                # print(item)

                data_insert.append(item)

            insert_into_db(data_insert)
            return
        case "worldofbooks":
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                # 'Accept-Encoding': 'gzip, deflate, br, zstd',
                "content-type": "application/x-www-form-urlencoded",
                "Origin": "https://www.worldofbooks.com",
                "Sec-GPC": "1",
                "Connection": "keep-alive",
                "Referer": "https://www.worldofbooks.com/",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "cross-site",
            }

            data = (
                '{"requests":[{"indexName":"shopify_products_apac","params":"clickAnalytics=true&facets=%5B%22author%22%2C%22availableConditions%22%2C%22bindingType%22%2C%22console%22%2C%22hierarchicalCategories.lvl0%22%2C%22platform%22%2C%22priceRanges%22%2C%22productType%22%2C%22publisher%22%5D&filters=fromPrice%20%3E%200&highlightPostTag=__%2Fais-highlight__&highlightPreTag=__ais-highlight__&maxValuesPerFacet=10&page=0&query='
                + encoded_query
                + '&tagFilters="}]}'
            )

            response = requests.post(
                "https://ar33g9njgj-1.algolianet.com/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(4.22.1)%3B%20Browser%20(lite)%3B%20instantsearch.js%20(4.62.0)%3B%20JS%20Helper%20(3.16.0)&x-algolia-api-key=96c16938971ef89ae1d14e21494e2114&x-algolia-application-id=AR33G9NJGJ",
                headers=headers,
                data=data,
            )

            data_response = response.text
            data_parsed = json.loads(data_response)
            items = data_parsed["results"][0]["hits"]

            data_insert = []

            for i in items:
                author = i["author"] or "Unknown Author"
                bindingType = i["bindingType"] or "Unknown Binding Type"
                productType = i["productType"] or "Unknown Product Type"
                item = (
                    i["id"],
                    i["longTitle"],
                    "https://www.worldofbooks.com/en-au/products/" + i["productHandle"],
                    i["fromPrice"],
                    i["imageURL"],
                    " / ".join((author, bindingType, productType)),
                    today,
                    site,
                )

                # print(item)

                data_insert.append(item)

            insert_into_db(data_insert)
            return
        case "salvos":
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0",
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.5",
                # 'Accept-Encoding': 'gzip, deflate, br, zstd',
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "https://www.salvosstores.com.au/",
                "x-algolia-api-key": "87e3f9aa6024de97a93cb797fa889cab",
                "x-algolia-application-id": "1Q4DUFTDP2",
                "Origin": "https://www.salvosstores.com.au",
                "Sec-GPC": "1",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "cross-site",
                "Connection": "keep-alive",
            }

            data = '{"query":"doctor who","hitsPerPage":48,"page":0,"numericFilters":["price >= 0","price <= 2000"],"facetFilters":[],"facets":["*"],"filters":"NOT collections:\\"Retail Fest\\""}'

            response = requests.post(
                "https://1q4duftdp2-dsn.algolia.net/1/indexes/created_at_asc/query?x-algolia-agent=Algolia%20for%20JavaScript%20(4.22.1)%3B%20Browser",
                headers=headers,
                data=data,
            )

            data_response = response.text
            data_parsed = json.loads(data_response)
            items = data_parsed["hits"]

            data_insert = []

            for i in items:
                price = (
                    i["salePrice"]
                    if i["salePrice"] is not None and i["salePrice"] != i["price"]
                    else i["price"]
                )
                item = (
                    i["sku"],
                    i["name"],
                    i["url"],
                    price,
                    i["image"],
                    " / ".join(i["warehouseName"])
                    + " / "
                    + " ".join(re.split("\s+", i["desc"], flags=re.UNICODE)),
                    today,
                    site,
                )

                # print(item)

                data_insert.append(item)
                insert_into_db(data_insert)
            return

        case _:
            print("Uh oh!")
            return


def insert_into_db(data):
    cur.executemany(
        "INSERT OR IGNORE INTO products VALUES(?, ?, ?, ?, ?, ?, ?, ?)", data
    )
    con.commit()


# Use watchlist
cur.execute("SELECT * FROM watchlist")
for row in cur.fetchall():
    scrape_link(row[0], row[1])

con.close()


### Send to Discord


# Yield successive n-sized chunks from l. https://www.geeksforgeeks.org/break-list-chunks-size-n-python/
def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i : i + n]


con = sqlite3.connect("./products.db")
cur = con.cursor()
cur.execute("SELECT * FROM products WHERE date=?", (today,))

embeds = []

colours = {
    "cashconverters": discord.Colour.from_rgb(255, 217, 18),
    "salvos": discord.Colour.from_rgb(255, 40, 62),
    "worldofbooks": discord.Colour.from_rgb(48, 132, 74),
    "default": discord.Colour.from_rgb(255, 255, 255),
}

# Fetch and print each row
print("New products:\n")
for row in cur.fetchall():
    colour = row[7] if colours[row[7]] is not None else "default"
    embed = discord.Embed(title=row[1], url=row[2], color=colours[colour])
    embed.add_field(name="Price", value=row[3])
    embed.add_field(name="Notes", value=row[5])
    # embed.set_author(name=row[7])
    if type(row[4]) == str and len(row[4]) > 1:
        embed.set_thumbnail(url=row[4])
    embeds.append(embed)

con.close()

# How many embeds per chunk
n = 10

embeds_chunks = list(divide_chunks(embeds, n))

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    channel = client.get_channel(1283193276156874876)

    if len(embeds) < 1:
        await channel.send("No new results today.")
    else:
        await channel.send("Printing today's results (" + str(len(embeds)) + ")")

        for chunk in embeds_chunks:
            await channel.send(embeds=chunk)

        await channel.send("Ended.")

    await client.close()
    print("Bot has disconnected.")


client.run(token)
