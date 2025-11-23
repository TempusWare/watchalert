import os
import discord
import sqlite3
import dotenv
import subprocess

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
                await message.channel.send(
                    "Added watch for site:"
                    + site
                    + " with queries:"
                    + ",".join(queries)
                )
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
                await message.channel.send(
                    "Removed watches for site:"
                    + site
                    + " with queries:"
                    + ",".join(queries)
                )
        case "!watchlist":
            list = watchlist(channel_id)
            msg = "site:query"
            for record in list:
                msg = msg + "\n" + record[0] + ":" + record[1]
            await message.channel.send(msg)
        case "!purgewatchlist":
            purgewatchlist()
            await message.channel.send("Purged watchlist")
        case "!triggerwatch":
            await message.channel.send("Triggering watch")
            subprocess.run(["python", "./getproducts.py"])
        case "!gethistory":
            if len(args) < 2:
                return
            url = args[1]
            history = gethistory(channel_id, url)
            msg = "history:" + url
            for record in history:
                msg = msg + "\n" + str(record[0]) + " : " + str(record[1])
            await message.channel.send(msg)
        case _:
            await message.channel.send("Not a command! Uh oh!")
            print("Uh oh!")


def addwatch(site: str, query: str, channel_id: int):
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


def purgewatchlist():
    try:
        with sqlite3.connect("./products.db") as con:
            cur = con.cursor()
            cur.execute("DELETE FROM watchlist")
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


client.run(token)
