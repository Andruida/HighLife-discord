import discord
import asyncio
from discord.ext import commands
import logging
import configparser
import requests
import datetime

import traceback

logger = logging.getLogger('discord')
#logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

config = configparser.ConfigParser()

config.read("config.ini")
config.read("messages.ini")

bot = commands.Bot(command_prefix=config["discord"]["prefix"])
bot.remove_command('help')
status_message = None

@bot.event
async def on_ready():
	global status_message
	if "status" in config and config["status"].get("message") and config["status"].get("channel"):
		try:
			status_message = await bot.get_channel(int(config["status"]["channel"])).fetch_message(int(config["status"]["message"]))
		except:
			pass
	print("Finished loading, ready for operation.")

@commands.guild_only()
@commands.has_guild_permissions(administrator=True)
@bot.command()
async def status(ctx):
	global status_message
	await asyncio.sleep(2)
	await ctx.message.delete()
	status_message = await ctx.send("This is a status message")
	config["status"] = {"channel":str(ctx.channel.id), "message":str(status_message.id)}
	with open("config.ini", "w") as f:
		config.write(f)

async def update_status():
	global status_message
	await bot.wait_until_ready()
	print(bot.is_closed())
	last_embed = None
	last_update = datetime.datetime.now()
	while not bot.is_closed():
		if status_message:
			try:
				config.read("messages.ini")
			except:
				print("Couldn't read messages.ini. Ignoring...")
			online = False
			dev_online = False
			try:
				r = requests.get(config["server"].get("main", "http://localhost:30120/players.json"))
				data = r.json()
				online = True
			except:
				data = []
				online = False
			try:
				r = requests.get(config["server"].get("dev", "http://localhost:30120/players.json"))
				dev_online = True
			except:
				dev_online = False
			embed = content_generator(online, data, last_update, dev_online)
			if last_embed != embed.to_dict():
				print("updated:", len(data), online, dev_online)
				last_update = datetime.datetime.now()
				embed = content_generator(online, data, last_update, dev_online)
				last_embed = embed.to_dict()
				await status_message.edit(content="", embed=embed)
		await asyncio.sleep(5)

def content_generator(online,data, last_update, dev_online=True):
	if online:
		color = 0x18DC56
	else:
		color = 0xE03F3F

	unknown = config["global"].get("unknown", "*Unknown*")
	message = config["message"]
	title = config["title"]

	embed = discord.Embed(color=color, description=message.get("description", unknown)+"\n\u200b")
	embed.set_author(name=message.get("name", unknown), url=message.get("url", discord.Embed.Empty), icon_url=message.get("icon", discord.Embed.Empty))


	embed.add_field(name=title.get("specs", unknown), value=message.get("specs", unknown)+"\n\u200b", inline=False)
	embed.add_field(name=title.get("ip", unknown), value=message.get("ip", unknown), inline=False)
	embed.add_field(name=title.get("restart", unknown), value=message.get("restart", unknown)+"\n\u200b", inline=False)
	embed.add_field(name=title.get("discord", unknown), value=message.get("discord", unknown), inline=False)
	embed.add_field(name=title.get("web", unknown), value=message.get("web", unknown), inline=False)
	embed.add_field(name=title.get("forum", unknown), value=message.get("forum", unknown), inline=False)
	embed.add_field(name=title.get("facebook", unknown), value=message.get("facebook", unknown), inline=False)
	embed.add_field(name=title.get("leaderboard", unknown), value=message.get("leaderboard", unknown)+"\n\u200b", inline=False)

	dev_message = message.get("online", unknown) if dev_online else message.get("offline", unknown)
	main_message = message.get("online", unknown) if online else message.get("offline", unknown)
	always_online = message.get("online", unknown)
	always_online_fields = title.get("always_online", "").split(",") # comma separated field in messages.ini; TODO: allow spaces

	embed.add_field(name=title.get("dev_status", unknown), value=dev_message, inline=True)
	embed.add_field(name=title.get("status", unknown), value=main_message, inline=True)

	embed.add_field(name=title.get("c_status0", unknown), value=main_message if not "0" in always_online_fields else always_online, inline=True)
	embed.add_field(name=title.get("c_status1", unknown), value=main_message if not "1" in always_online_fields else always_online, inline=True)
	embed.add_field(name=title.get("c_status2", unknown), value=main_message if not "2" in always_online_fields else always_online, inline=True)
	embed.add_field(name=title.get("c_status3", unknown), value=(main_message if not "3" in always_online_fields else always_online)+"\n\u200b", inline=True)

	embed.add_field(name=title.get("online_players", unknown), value="{}/{}".format(len(data), message.get("online_max", -1)) if online else message.get("offline", unknown), inline=False)
	
	players = ["","",""]
	data.sort(key=lambda x: x.get("name", unknown)[:20])
	for p in data:
		players[data.index(p)%3] += "{} [{}]\n".format(p.get("name", unknown), p.get("id", "-1"))
	embed.add_field(name=title.get("players", unknown), value=players[0] if len(players[0]) > 0 else message.get("no_online_player", unknown), inline=True)
	embed.add_field(name="\u200b", value=players[1] if len(players[1]) > 0 else "\u200b", inline=True)
	embed.add_field(name="\u200b", value=players[2]+"\n\u200b" if len(players[2]) > 0 else "\u200b", inline=True)

	embed.timestamp = last_update
	embed.set_footer(text=message.get("name", unknown), icon_url=message.get("icon", discord.Embed.Empty))

	return embed

bot.loop.create_task(update_status())



bot.run(config["discord"]["token"])