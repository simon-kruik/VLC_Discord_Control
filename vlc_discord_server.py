import socket # For hosting a server that communicates w/ OBS script
import asyncio # For handling multiple connections
import discord # Requires "pip install discord.py" module for interacting with discord
from dotenv import load_dotenv # Loading environment variables
import os # Getting environment variables
import json # For exporting and importing files

MSG_LENTH = 1024

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()



@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content == 'list':
        response = "Listing files in the library is not currently available"
        await message.channel.send(response)

    if message.content == 'join':
        response = "Please enter the following into your OBS Script: " + str(message.guild.id)
        await message.channel.send(response)



client.run(TOKEN)

server_bindings = {}



HOST = '' # Empty string means assign to all interfaces
PORT = 8420

async def handle_connection(reader,writer):
    data = await reader.read(100)
    message = data.decode()
    addr = writer.get_extra_info('peername')
    print("Received: " + message + " from " + str(addr))
    writer.write("Hello")
    await writer.drain()
    print("Closing")
    writer.close()

loop = asyncio.get_event_loop()
coro = asyncio.start_server(handle_connection, HOST, PORT, loop=loop)
server = loop.run_until_complete(coro)

print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

server.close()
loop.run_until_complete(server.wait_closed())
loop.close()




#
# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serversock:
#     serversock.bind((HOST, PORT))
#     serversock.listen(5)
#     while True:
#         # Accept a connection from external
#         clientsock, addr = serversock.accept()
#         with clientsock:
#             print("Connected to by: ", addr)
#             token = clientsock.recv(MSG_LENGTH)
#             #command = input("Please enter command")
#             #command_bytes = command.encode('utf-8')
#             clientsock.sendall(command_bytes)
