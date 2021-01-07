import asyncio
import discord
from math import ceil

COLOUR = 0xf27b00
PAGE_SIZE = 10
NEXT_ARROW = "➡"
PREVIOUS_ARROW = "⬅"

async def send_video_list(discord_client, video_list, channel_id, page=1):
    embed_message = discord.embed(Title="Videos Available:", colour=COLOUR)
    if (len(video_list) > PAGE_SIZE):
        start = (page-1) * PAGE_SIZE
        end = page * PAGE_SIZE
        video_list = video_list[start:end]
    for item in video_list:
        embed.add_field(name=item,value="")
    embed.set_footer(text="Page" + str(page) + "/" + str(ceil(len(video_list)/PAGE_SIZE))) # e.g. Page 2/5
    channel = discord_client.get_channel(channel_id)

    message = await channel.send(embed=embed_message)

    if len(video_list) > page * PAGE_SIZE:
        await message.add_reaction(message, NEXT_ARROW)
    if page > 1:
        await message.add_reaction(message, PREVIOUS_ARROW)
