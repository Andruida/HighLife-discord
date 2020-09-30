import discord
import asyncio
from discord.ext import commands
import logging
import configparser
import requests

import traceback

logger = logging.getLogger('discord')
#logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

config = configparser.ConfigParser()

config.read("config.ini")

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
	last_number = -1
	while not bot.is_closed():
		print("run")
		if status_message:
			print("message ready")
			r = requests.get("http://fivem.hlrp.hu:30120/players.json")
			data = r.json()
			if last_number != len(data):
				last_number = len(data)
				print("updated")
				await status_message.edit(content="Online játékosok {}/64.".format(last_number))
		await asyncio.sleep(30)

bot.loop.create_task(update_status())



bot.run(config["discord"]["token"])