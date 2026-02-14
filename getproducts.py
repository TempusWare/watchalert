import os
import time
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
today_simple = datetime.today().strftime("%Y%m%d")

colours = {
    "cashconverters": discord.Colour.from_rgb(255, 217, 18),
    "salvos": discord.Colour.from_rgb(255, 40, 62),
    "worldofbooks": discord.Colour.from_rgb(48, 132, 74),
    "surugaya": discord.Colour.from_rgb(29, 32, 136),
    "ebgames": discord.Colour.from_rgb(248, 65, 71),
    "booktopia": discord.Colour.from_rgb(35, 94, 57),
    "cex": discord.Colour.from_rgb(226, 10, 3),
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

    # Check if searching by special parameters
    args = query.split("?")
    if len(args) > 1:
        # Resolve keyword
        params["keyword"] = args[0]

        # Parse special parameters and add to params
        specials = args[1].split("&")
        for s in specials:
            v = s.split("=")
            keyname = v[0].lower()
            value = v[1]

            params[keyname] = value

        # Special case for CREATOR label is actually person_name
        if "creator" in params:
            params["person_name"] = params["creator"]
            params.pop("creator")

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


def scrape_ebgames(query: str, channel_id: int) -> list:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        # 'Accept-Encoding': 'gzip, deflate, br, zstd',
        "Referer": "https://www.ebgames.com.au/search?q=DC+Comics+-+Superman+2025+-+Superman+Shield+Moulded+Mini-Backpack",
        "Sec-GPC": "1",
        "Alt-Used": "www.ebgames.com.au",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=4",
        # Requests doesn't support trailers
        # 'TE': 'trailers',
    }

    params = {
        "q": query,
        "sort": "releasedate",
        "order": "desc",
    }

    response = requests.get(
        "https://www.ebgames.com.au/search/query",
        params=params,
        headers=headers,
    )

    data_response = response.text
    data_parsed = json.loads(data_response)
    items = data_parsed["results"]

    data_insert = []

    for i in items:
        price = i["promotionPrice"] or i["price"]
        note = "promotion" if "promotionPrice" in i else ""
        item = (
            i["sku"],
            i["title"],
            i["productUrlAbsolute"],
            price,
            "https:" + i["imageUrl"],
            note,
            today,
            "ebgames",
            channel_id,
        )

        print(item)

        data_insert.append(item)

    return data_insert


def scrape_booktopia(query: str, channel_id: int) -> list:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        # 'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Referer': 'https://www.booktopia.com.au/search?keywords=doctor%20who&productType=917504&pn=1',
        'x-nextjs-data': '1',
        'Sec-GPC': '1',
        'Alt-Used': 'www.booktopia.com.au',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Priority': 'u=0',
    }

    params = {
        'keywords': query,
        'productType': '917504',
        'pn': '1',
    }

    response = requests.get(
        'https://www.booktopia.com.au/_next/data/1uqt6obZg1LSgf_BaxyCb/search.json',
        params=params,
        headers=headers,
    )

    data_response = response.text
    data_parsed = json.loads(data_response)

    items = data_parsed["pageProps"]["searchData"]["pagination"]["products"]

    data_insert = []

    for i in items:
        item = (
            i["code"],
            f"{i["displayName"]}: {i["subtitle"]}" if i["subtitle"] is not None else i["displayName"],
            f"https://www.booktopia.com.au/{i["productUrl"]}",
            i["salePrice"],
            i["imageUrl"],
            f"{i["bindingFormat"]}. RRP:{i["retailPrice"]}",
            today,
            "booktopia",
            channel_id,
        )

        print(item)

        data_insert.append(item)

    return data_insert

def scrape_cex_product(query: str, channel_id: int) -> list:
    data_insert = []

    # Get product detail
    product_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        # 'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Referer': 'https://au.webuy.com/',
        'Origin': 'https://au.webuy.com',
        'Sec-GPC': '1',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'Connection': 'keep-alive',
    }

    product_response = requests.get(f'https://wss2.cex.au.webuy.io/v3/boxes/{query}/detail', headers=product_headers)
    product_data = product_response.text
    product_parsed = json.loads(product_data)

    details = product_parsed["response"]["data"]["boxDetails"][0]

    # If out of stock, return empty
    if details["outOfStock"] == 1:
        print(f"{query} Out of stock")
        return data_insert

    item = (
        details["boxId"],
        details["boxName"],
        f"https://au.webuy.com/product-detail?id={details["boxId"]}#{today_simple}", # Append date to end to bypass unique row
        details["sellPrice"],
        details["imageUrls"]["large"].replace(" ", "%20"),
        f"1st:{details["firstPrice"]}, prev:{details["previousPrice"]}, stock:{details["collectionQuantity"]}",
        today,
        "cex",
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
        # case "ebgames":
        #     return scrape_ebgames(query, channel_id)
        case "booktopia":
            return scrape_booktopia(query, channel_id)
        case "cex":
            return scrape_cex_product(query, channel_id)
        case _:
            print(f"Uh oh! Can't scrape {site}, {query}, {channel_id}")
            return []


def add_fault(channel_id: int):
    try:
        with sqlite3.connect("./products.db") as con:
            cur = con.cursor()
            cur.execute(
                "INSERT OR IGNORE INTO faults VALUES(?)",
                (channel_id,),
            )
            con.commit()
    except sqlite3.OperationalError as e:
        print(e)
    return


def clear_faults():
    try:
        with sqlite3.connect("./products.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM faults")
            for row in cur.fetchall():
                channel_id = row[0]
                cur.execute(
                    "DELETE FROM watchlist WHERE channel=?",
                    (channel_id,),
                )
                cur.execute(
                    "DELETE FROM faults WHERE channel=?",
                    (channel_id,),
                )
                con.commit()
    except sqlite3.OperationalError as e:
        print(e)
    return


# Use watchlist
def watch():
    try:
        with sqlite3.connect("./products.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM watchlist")
            for row in cur.fetchall():
                try:
                    data = scrape_link(row[0], row[1], row[2])
                    cur.executemany(
                        "INSERT OR IGNORE INTO products VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        data,
                    )
                except sqlite3.OperationalError as e:
                    print(e)
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

        try:
            if len(alerts) < 1:
                await channel.send("No new results today.")
            else:
                firstmsg = await channel.send(
                    "Printing today's results ("
                    + str(len(alerts))
                    + ") ["
                    + today
                    + "]"
                )
                # await firstmsg.pin()

                embeds_chunks = list(divide_chunks(alerts, n))
                for chunk in embeds_chunks:
                    await channel.send(embeds=chunk)
                    time.sleep(0.1)

                await channel.send("Ended.")
        except:
            print("Error with " + str(key))
            add_fault(int(key))

    await client.close()
    print("Bot has disconnected.")

    print("Clearing faults")
    clear_faults()


client.run(token)
