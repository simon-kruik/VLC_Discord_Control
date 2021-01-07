import asyncio
import discord
from math import ceil

COLOUR = 0xf27b00
PAGE_SIZE = 10
NEXT_ARROW = "➡"
PREVIOUS_ARROW = "⬅"

async def send_video_list(discord_client, video_list, channel_id, page=1):
    embed_message = discord.Embed(Title="Videos Available:", colour=COLOUR)
    total_pages = ceil(len(video_list)/PAGE_SIZE)
    if (total_pages > 1):
        start = (page-1) * PAGE_SIZE
        end = page * PAGE_SIZE
        video_list = video_list[start:end]
    for item in video_list:
        embed_message.add_field(name=item,value="\u200b", inline=False)
    embed_message.set_footer(text="Page: " + str(page) + "/" + str(total_pages)) # e.g. Page 2/5
    channel = discord_client.get_channel(channel_id)

    message = await channel.send(embed=embed_message)

    if page < total_pages:
        await message.add_reaction(message, NEXT_ARROW)
    if page > 1:
        await message.add_reaction(message, PREVIOUS_ARROW)
