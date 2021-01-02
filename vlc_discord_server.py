import socket # For hosting a server that communicates w/ OBS script
import asyncio # For handling multiple connections
import discord # Requires "pip install discord.py" module for interacting with discord
from dotenv import load_dotenv # Loading environment variables
import os # Getting environment variables
import json # For exporting and importing files
import threading # To run both Discord and Server at same time


### DISCORD STUFF
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

async def send_message(message, guild, channel):
    ## TODO: Send a message to discord, presumably
    return ""


#client.run(TOKEN)
### END DISCORD STUFF

clients = {} # uses Task as key and (reader,writer) as value
HOST = '' # Empty string means assign to all interfaces
PORT = 8420

def accept_client(client_reader,client_writer):
    global clients
    task = asyncio.Task(handle_client(client_reader,client_writer,"Testing"))
    clients[task] = (client_reader, client_writer)

    def delete_client(task):
        del clients[task]
        client_writer.close()

    task.add_done_callback(delete_client)

async def handle_client(client_reader, client_writer, task):
    client_writer.write("Hello\n".encode())
    data = await asyncio.wait_for(client_reader.readline(), 5) # Wait for 5 seconds
    if data is None:
        print("I'm getting no data from the client")

    string_data = data.decode().rstrip()
    if string_data != "Heyo":
        print("Not getting the expected response from the client")

    client_writer.write(task.encode())
    data = await asyncio.wait_for(client_reader.readline(), 5)
    string_data = data.decode().rstrip()
    print("Received data: " + string_data)

    return string_data

def main():
    loop = asyncio.get_event_loop()
    server_task = asyncio.start_server(accept_client, HOST, PORT)
    loop.run_until_complete(server_task)
    loop.run_forever()

if __name__ == '__main__':
    main()




#
# async def handle_connection(reader,writer):
#     data = await reader.read(100)
#     message = data.decode()
#     addr = writer.get_extra_info('peername')
#     print("Received: " + message + " from " + str(addr))
#     writer.write("Hello")
#     await writer.drain()
#     print("Closing")
#     writer.close()
#
# async def start_server(HOST,PORT):
#     loop = asyncio.get_event_loop()
#     coro = asyncio.start_server(handle_connection, HOST, PORT, loop=loop)
#     # THere's an issue with this line that causes it to never complete :/
#     server = loop.run_until_complete(coro)
#
#     print('Serving on {}'.format(server.sockets[0].getsockname()))
#     try:
#         loop.run_forever()
#     except KeyboardInterrupt:
#         pass
#
#     server.close()
#     loop.run_until_complete(server.wait_closed())
#     loop.close()
#
# if __name__ == '__main__':
#     t1 = threading.Thread(target=client.run, args=(TOKEN))
#     await start_server(HOST,PORT)
#     t1.start()


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
