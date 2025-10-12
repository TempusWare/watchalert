import os
import discord
import sqlite3
import dotenv

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

    if message.author.id != 494030294723067904:
        return

    if message.content.startswith("!hello"):
        await message.channel.send("Hello!")

    args = message.content.split(" ")

    match args[0]:
        case "!addwatch":
            if len(args) < 2:
                return
            site = args[1].lower()
            query = " ".join(args[2:]).lower()
            print([site, query])
            await message.channel.send(
                "Added watch for site:" + site + " with query:" + query
            )
        case "!delwatch":
            if len(args) < 2:
                return
            site = args[1].lower()
            query = " ".join(args[2:]).lower()
            print([site, query])
            await message.channel.send(
                "Removed watch for site:" + site + " with query:" + query
            )
        case "!watchlist":
            list = watchlist()
            msg = "site:query"
            for record in list:
                msg = msg + "\n" + record[0] + ":" + record[1]
            await message.channel.send(msg)
        case _:
            print("Uh oh!")


def addwatch(site, query):
    con = sqlite3.connect("products.db")
    cur = con.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO watchlist VALUES(?, ?)",
        (
            site,
            query,
        ),
    )
    con.commit()
    con.close()
    return


def delwatch(site, query):
    con = sqlite3.connect("products.db")
    cur = con.cursor()
    cur.execute(
        "DELETE FROM watchlist WHERE site=? AND query=?",
        (
            site,
            query,
        ),
    )
    con.commit()
    con.close()
    return


def watchlist():
    con = sqlite3.connect("products.db")
    cur = con.cursor()
    cur.execute("SELECT * FROM watchlist")
    list = []
    for row in cur.fetchall():
        list.append((row[0], row[1]))
    con.close()
    return list


client.run(token)
