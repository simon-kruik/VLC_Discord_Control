import socket # For hosting a server that communicates w/ OBS script
import asyncio # For handling multiple connections
import discord # Requires "pip install discord.py" module for interacting with discord
from dotenv import load_dotenv # Loading environment variables
import os # Getting environment variables
import json # For exporting and importing files
import threading # To run both Discord and Server at same time

import discord_messages as dms


### DISCORD STUFF
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()



@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    server_id = str(message.guild.id) + "." + str(message.author.id)
    # TODO: Add a message prefix, and save to local json file
    if message.author == client.user:
        return ""
    if message.content == 'list':
        response = await handle_task(server_id,  "LIST_LIBRARY")
        await dms.send_video_list(client, response, message.channel.id)

    if message.content.startswith('search'):
        args = message.content.replace("search","",1) # Replaces maximum of 1 use of term 'search' - leaving just the following arguments
        response = await handle_task(server_id, "SEARCH", args)
        await message.channel.send(response)

    if message.content == 'join':
        response = "Please enter the following into your OBS Script: " + server_id
        await message.channel.send(response)

async def send_dm(message, user_id):
    user = await client.fetch_user(user_id)
    print("Sending message to: ", user, "\n",message)
    await user.send(message)

    #TODO: Split out this embed code into a separate file determining how messages should look


#client.run(TOKEN)
### END DISCORD STUFF

clients = {} # uses Task as key and (reader,writer) as value
server_ids = {}
HOST = '' # Empty string means assign to all interfaces
PORT = 8420

async def handle_task(server_id, task, arg=None):
    global server_ids
    print("Looking for server: " + str(server_id))
    print("Current servers connected: " + str(server_ids))
    if server_id in server_ids:
        client_reader, client_writer = server_ids[server_id]
        response = await handle_client(client_reader,client_writer,task, arg)
        if response == "":
            response = "No message received from Client"

        return response
    else:
        return "No OBS script connected"


def accept_client(client_reader,client_writer):
    global clients
    task = asyncio.Task(handle_client(client_reader,client_writer,"HELLO"))
    clients[task] = (client_reader, client_writer)

    def delete_client(task):
        del clients[task]
        client_writer.close()

    #task.add_done_callback(delete_client)

async def handle_client(client_reader, client_writer, task, arg=None):
    global server_ids
    try:
        client_writer.write("Hello\n".encode())
        await client_writer.drain()
        data = await asyncio.wait_for(client_reader.readline(), 5) # Wait for 5 seconds
        if data is None:
            print("I'm getting no data from the client")

        string_data = data.decode().rstrip()
        if "Heyo" not in string_data:
            print("Not getting the expected response from the client")
            return ""
        else:
            print("Client says: Heyo")
        server_id = string_data.split(':')[1]
        print("Server connected: " + server_id)
        # TODO: Only send this on initial connection, not on subsequent commands
        if server_id not in server_ids:
            await send_dm("OBS client connected from: " + str(client_writer._transport.get_extra_info('peername')[0]), server_id.split('.')[1])
        # TODO: If there's already a server connected here, close it properly, then set a new one
        server_ids[server_id] = (client_reader, client_writer)
        if arg:
            task = task + "~" + arg + "\n" #add arg delimited by ~
        else:
            task = task + "\n" # append to make it a single line
        client_writer.write(task.encode())
        await client_writer.drain()
        data = await asyncio.wait_for(client_reader.readline(), 5)
        string_data = data.decode().rstrip()
        print("Received data: " + string_data)
        return string_data

    except ConnectionResetError:
        return "Client has been disconnected"
    except asyncio.TimeoutError:
        return "Connection timed out"


def main():
    loop = asyncio.get_event_loop()
    server_task = asyncio.start_server(accept_client, HOST, PORT)
    loop.run_until_complete(server_task)
    loop.run_until_complete(client.run(TOKEN))
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
