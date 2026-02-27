import os
import discord
import sqlite3
import dotenv
import subprocess
from urllib.parse import parse_qs, urlparse

dotenv.load_dotenv()
token = str(os.getenv("TOKEN"))

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if (
        message.author.id != 494030294723067904
        and message.author.id != 457371383140450306
    ):
        return

    if not message.content.startswith("!"):
        return

    if message.content.startswith("!hello"):
        await message.channel.send("Hello!")

    args = message.content.split(" ")

    channel_id = message.channel.id

    match args[0]:
        case "!addwatch":
            if len(args) < 3:
                return
            site = args[1].lower()
            query = " ".join(args[2:]).lower()
            print([site, query])
            addwatch(site, query, channel_id)
            await message.channel.send(
                "Added watch for site:" + site + " with query:" + query
            )
        case "!delwatch":
            if len(args) < 2:
                return
            site = args[1].lower()
            query = " ".join(args[2:]).lower()
            print([site, query])
            delwatch(site, query, channel_id)
            await message.channel.send(
                "Removed watch for site:" + site + " with query:" + query
            )
        case "!addwatchc":
            if len(args) < 3:
                return
            site = args[1].lower()
            query = " ".join(args[2:])
            print([site, query])
            addwatch(site, query, channel_id)
            await message.channel.send(
                "Added case sensitive watch for site:" + site + " with query:" + query
            )
        case "!delwatchc":
            if len(args) < 2:
                return
            site = args[1].lower()
            query = " ".join(args[2:])
            print([site, query])
            delwatch(site, query, channel_id)
            await message.channel.send(
                "Removed case sensitive watch for site:" + site + " with query:" + query
            )
        case "!addwatches":
            if len(args) < 3:
                return
            site = args[1].lower()
            query = " ".join(args[2:]).lower()
            queries = query.split(",")
            if len(queries) > 1:
                print([site, queries])
                for q in queries:
                    addwatch(site, q.strip(), channel_id)
                msg = f"Added watches for site:{site} with queries:\n - {'\n - '.join(queries)}"
                if len(msg) <= 2000:
                    await message.channel.send(msg)
                else:
                    await message.channel.send("Message too long to send")
        case "!delwatches":
            if len(args) < 3:
                return
            site = args[1].lower()
            query = " ".join(args[2:]).lower()
            queries = query.split(",")
            if len(queries) > 1:
                print([site, queries])
                for q in queries:
                    delwatch(site, q.strip(), channel_id)
                msg = f"Removed watches for site:{site} with queries:\n - {'\n - '.join(queries)}"
                if len(msg) <= 2000:
                    await message.channel.send(msg)
                else:
                    await message.channel.send("Message too long to send")
        case "!watchlist":
            items = watchlist(channel_id)
            msg = "site:query"
            for record in items:
                msg = msg + "\n" + record[0] + ":" + record[1]
            if len(msg) <= 2000:
                await message.channel.send(msg)
            else:
                await message.channel.send("Message too long to send")
        case "!purgewatchlist":
            purgewatchlist(channel_id)
            await message.channel.send("Purged watchlist")
        case "!triggerwatch":
            if len(args) == 2 and args[1] == "all":
                await message.channel.send("Triggering global watch")
                subprocess.run(["./venv/Scripts/python", "./getproducts.py", "all"])
            else:
                await message.channel.send(f"Triggering watch for this channel {channel_id}")
                subprocess.run(["./venv/Scripts/python", "./getproducts.py", "channel", str(channel_id)])
        case "!gethistory":
            if len(args) < 2:
                return
            url = args[1]
            history = gethistory(channel_id, url)
            msg = "history:" + url
            for record in history:
                msg = msg + "\n" + str(record[0]) + " : " + str(record[1])
            await message.channel.send(msg)
        case "!setapikey":
            if len(args) < 3:
                return
            site = args[1].lower()
            key = args[2]
            print([site, key])
            setapikey(site, key)
            await message.channel.send(
                "Set API key for site:" + site + " with key:" + key
            )
        case "!getapikeys":
            items = getapikeys()
            msg = "site:key"
            for record in items:
                msg = msg + "\n" + record[0] + ":" + record[1]
            if len(msg) <= 2000:
                await message.channel.send(msg)
            else:
                await message.channel.send("Message too long to send")
        case _:
            await message.channel.send("Not a command! Uh oh!")
            print("Uh oh!")


# URL validator from https://stackoverflow.com/a/38020041
def uri_validator(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc])
    except AttributeError:
        return False


def addwatch(site: str, query: str, channel_id: int):
    # extract id from cex queries
    if site == "cex":
        # validate cex url
        if not uri_validator(query) or "webuy" not in query:
            print(f"error with cex query {query}")
            return
        try:
            query = parse_qs(urlparse(query).query)["id"][0]
        except:
            return
    try:
        with sqlite3.connect("./products.db") as con:
            cur = con.cursor()
            cur.execute(
                "INSERT OR IGNORE INTO watchlist VALUES(?, ?, ?)",
                (site, query, channel_id),
            )
            con.commit()
    except sqlite3.OperationalError as e:
        print(e)
    return


def delwatch(site: str, query: str, channel_id: int):
    try:
        with sqlite3.connect("./products.db") as con:
            cur = con.cursor()
            cur.execute(
                "DELETE FROM watchlist WHERE site=? AND query=? AND channel=?",
                (site, query, channel_id),
            )
            con.commit()
    except sqlite3.OperationalError as e:
        print(e)
    return


def watchlist(channel_id: int):
    try:
        with sqlite3.connect("./products.db") as con:
            cur = con.cursor()
            cur.execute(
                "SELECT * FROM watchlist WHERE channel=? ORDER BY site", (channel_id,)
            )
            list = []
            for row in cur.fetchall():
                list.append((row[0], row[1]))
            return list
    except sqlite3.OperationalError as e:
        print(e)
    return []


def purgewatchlist(channel_id: int):
    try:
        with sqlite3.connect("./products.db") as con:
            cur = con.cursor()
            cur.execute("DELETE FROM watchlist WHERE channel=?", (channel_id,))
            con.commit()
    except sqlite3.OperationalError as e:
        print(e)


def gethistory(channel_id: int, url: str):
    try:
        with sqlite3.connect("./products.db") as con:
            cur = con.cursor()
            cur.execute(
                "SELECT date, price FROM products WHERE url=? ORDER BY date",
                (url,),
            )
            list = []
            for row in cur.fetchall():
                list.append((row[0], row[1]))
            return list
    except sqlite3.OperationalError as e:
        print(e)
    return []


def setapikey(site: str, key: str):
    try:
        with sqlite3.connect("./products.db") as con:
            cur = con.cursor()
            cur.execute(
                "INSERT OR IGNORE INTO apikeys VALUES(?, ?)",
                (site, key),
            )
            con.commit()
    except sqlite3.OperationalError as e:
        print(e)
    return


def getapikeys():
    try:
        with sqlite3.connect("./products.db") as con:
            cur = con.cursor()
            cur.execute(
                "SELECT * FROM apikeys ORDER BY ROWID DESC LIMIT 10"
            )
            list = []
            for row in cur.fetchall():
                list.append((row[0], row[1]))
            return list
    except sqlite3.OperationalError as e:
        print(e)
    return []


client.run(token)
