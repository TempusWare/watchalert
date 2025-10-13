import os
import requests
import json
import sqlite3
import urllib.parse
from datetime import datetime
import discord
import dotenv
from bs4 import BeautifulSoup


dotenv.load_dotenv()
token = str(os.getenv("TOKEN"))

today = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

colours = {
    "cashconverters": discord.Colour.from_rgb(255, 217, 18),
    "salvos": discord.Colour.from_rgb(255, 40, 62),
    "worldofbooks": discord.Colour.from_rgb(48, 132, 74),
    "surugaya": discord.Colour.from_rgb(29, 32, 136),
    "default": discord.Colour.from_rgb(255, 255, 255),
}


def scrape_cashconverters(query: str, channel_id: int) -> list:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        # 'Accept-Encoding': 'gzip, deflate, br, zstd',
        # "Referer": "https://www.cashconverters.com.au/search-results?Sort=newest&page=1&f%5Bcategory%5D%5B0%5D=all&f%5Blocations%5D%5B0%5D=all&query="
        # + encoded_query,
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
            "cashconverters",
            channel_id,
        )

        print(item)

        data_insert.append(item)

    return data_insert


def scrape_worldofbooks(query: str, channel_id: int) -> list:
    encoded_query = urllib.parse.quote_plus(query)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        # 'Accept-Encoding': 'gzip, deflate, br, zstd',
        "content-type": "application/x-www-form-urlencoded",
        "Origin": "https://www.worldofbooks.com",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
        # "Referer": "https://www.worldofbooks.com/",
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
            "worldofbooks",
            channel_id,
        )

        print(item)

        data_insert.append(item)

    return data_insert


def scrape_salvos(query: str, channel_id: int) -> list:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        # 'Accept-Encoding': 'gzip, deflate, br, zstd',
        "Content-Type": "application/x-www-form-urlencoded",
        # "Referer": "https://www.salvosstores.com.au/",
        "x-algolia-api-key": "87e3f9aa6024de97a93cb797fa889cab",
        "x-algolia-application-id": "1Q4DUFTDP2",
        "Origin": "https://www.salvosstores.com.au",
        "Sec-GPC": "1",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Connection": "keep-alive",
    }

    data = (
        '{"query":"'
        + query
        + '","hitsPerPage":48,"page":0,"numericFilters":["price >= 0","price <= 2000"],"facetFilters":[],"facets":["*"],"filters":"NOT collections:\\"Retail Fest\\""}'
    )

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
            " / ".join(i["warehouseName"]),
            today,
            "salvos",
            channel_id,
        )

        print(item)

        data_insert.append(item)

    return data_insert


def scrape_surugaya(query: str, channel_id: int) -> list:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        # 'Accept-Encoding': 'gzip, deflate, br, zstd',
        "Sec-GPC": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Priority": "u=0, i",
        # Requests doesn't support trailers
        # 'TE': 'trailers',
    }

    params = {
        "keyword": query,
        "btn_search": "",
        "sort": "updated_date_desc",
        # "in_stock": "t",
    }

    response = requests.get(
        "https://www.suruga-ya.com/en/products",
        params=params,
        headers=headers,
    )

    data_response = response.text

    data_insert = []

    soup = BeautifulSoup(data_response, "html.parser")

    for i in soup.select("div.item"):
        price = (
            i.find("div", class_="price_product").findChildren()[0].get_text().strip()
        )

        if price == "Out of stock":
            continue

        image = (
            i.find("img", class_="img-fluid")["src"]
            if i.find("img", class_="img-fluid")["src"]
            != "/themes/surugaya_global/images/products/no_photo.jpg"
            else "https://www.suruga-ya.com/themes/surugaya_global/images_light/products/no_photo.jpg.webp"
        )

        item = (
            i.find("a")["data-product-id"],
            i.find("h3", class_="title_product").get_text().strip(),
            "https://www.suruga-ya.com" + i.find("a")["href"],
            price,
            image,
            i.find("p", class_="message").get_text().strip() or "",
            today,
            "surugaya",
            channel_id,
        )

        print(item)

        data_insert.append(item)

    return data_insert


def scrape_link(site: str, query: str, channel_id: int) -> list:
    match site:
        case "cashconverters":
            return scrape_cashconverters(query, channel_id)
        case "worldofbooks":
            return scrape_worldofbooks(query, channel_id)
        case "salvos":
            return scrape_salvos(query, channel_id)
        case "surugaya":
            return scrape_surugaya(query, channel_id)
        case _:
            print("Uh oh!")
            return []


# Use watchlist
def watch():
    try:
        with sqlite3.connect("./products.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM watchlist")
            for row in cur.fetchall():
                data = scrape_link(row[0], row[1], row[2])
                cur.executemany(
                    "INSERT OR IGNORE INTO products VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    data,
                )
    except sqlite3.OperationalError as e:
        print(e)


watch()

### Send to Discord


# Yield successive n-sized chunks from l. https://www.geeksforgeeks.org/break-list-chunks-size-n-python/
def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i : i + n]


con = sqlite3.connect("./products.db")
cur = con.cursor()
cur.execute("SELECT * FROM products WHERE date=?", (today,))

embeds = {}

# Fetch and print each row
print("New products:\n")
for row in cur.fetchall():
    title = row[1]
    url = row[2]
    price = row[3]
    image = row[4]
    notes = row[5]
    # date = row[6]
    site = row[7]
    channel = row[8]

    colour = site if colours[site] is not None else "default"

    embed = discord.Embed(title=title, url=url, color=colours[colour])
    embed.add_field(name="Price", value=price)
    embed.add_field(name="Notes", value=notes)
    embed.set_footer(text=site)
    if type(image) == str and len(image) > 1:
        embed.set_thumbnail(url=image)

    if str(channel) not in embeds:
        embeds[str(channel)] = []

    embeds[str(channel)].append(embed)

con.close()

# How many embeds per chunk
n = 10

# embeds_chunks = list(divide_chunks(embeds, n))

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

    for key in embeds.keys():
        channel = client.get_channel(int(key))

        alerts = embeds[str(key)]

        if len(alerts) < 1:
            await channel.send("No new results today.")
        else:
            await channel.send("Printing today's results (" + str(len(alerts)) + ")")

            embeds_chunks = list(divide_chunks(alerts, n))
            for chunk in embeds_chunks:
                await channel.send(embeds=chunk)

            await channel.send("Ended.")

    await client.close()
    print("Bot has disconnected.")


client.run(token)
