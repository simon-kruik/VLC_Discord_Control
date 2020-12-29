import obspython as obs
import os # For working with paths and directories
from pathlib import Path # For grabbing the home directory
import urllib.request # For contacting VLC HTTP Interface
import urllib.parse # For encoding urls
import base64 # For encoding values
import json # For handling responses from VLC (hopefully I don't have to deal with XML)

vlc_password = "obs"
file_directory = str(os.path.join(Path.home(), "Videos"))
my_settings = None

# Executes on load, not sure what I need to set here
def script_load(settings):
    print("Script loaded, current dir: " + file_directory)

def script_description():
    return "A script by Simon Kruik to control VLC from a Discord bot"

def script_update(settings):
    global my_settings
    global file_directory
    my_settings = settings
    file_directory = obs.obs_data_get_string(settings,"file_directory")
    #playlist = obs.obs_data_get_array(my_settings, "playlist")
    #print(obs.obs_data_array_count(playlist))
    #current_dir = obs.obs_data_get_string(settings,"file_directory")
    #print(current_dir)
    # DO SOMETHING - I think this is the loop

def script_defaults(settings):
    obs.obs_data_set_default_int(settings, "interval", 30)

def script_properties():
    props = obs.obs_properties_create()
    # Directory to source video files from
    file_directory_path_field = obs.obs_properties_add_path(props, "file_directory", "Source Directory (where all your videos live)", obs.OBS_PATH_DIRECTORY,"",file_directory)
    obs.obs_property_set_modified_callback(file_directory_path_field, directory_updated)
    # List of Video Files for the playlist
    obs.obs_properties_add_editable_list(props,"playlist", "Playlist", obs.OBS_EDITABLE_LIST_TYPE_FILES,"*.mkv *.mp4 *.avi",file_directory)
    # Testing the skip button
    obs.obs_properties_add_button(props, "skip", "Skip", skip)
    # Testing the playlist button
    obs.obs_properties_add_button(props, "getPlaylist", "Show Playlist", get_playlist)
    # Testing the status button
    obs.obs_properties_add_button(props, "currently_playing", "Status", currently_playing)
    # Testing the pause button
    obs.obs_properties_add_button(props, "pause", "Play/Pause", toggle_pause)

    # Testing adding stuff to playlist
    obs.obs_properties_add_button(props, "add_to_playlist", "Add", add_to_playlist_handler)
    # Testing clearing the playlist
    obs.obs_properties_add_button(props, "clear_playlist", "Clear", clear_playlist)

    # Test listing the video library:
    obs.obs_properties_add_button(props, "list_library", "List",list_library)

    obs.obs_properties_apply_settings(props, my_settings)
    return props

# Callback function - not sure what each of these variables passed into it are
def directory_updated(a,b,c):
    #print("1st argument: " + str(a))
    #print("2nd argument: " + str(b))
    #print("3rd argument: " + str(c))
    return ""

def vlc_request(path):
    url = "http://127.0.0.1:8080/requests/" + path
    #print("Accessing URL: " + url   )
    vlc_req = urllib.request.Request(url)
    auth_headers = ":" + vlc_password
    auth_headers_enc = base64.b64encode(auth_headers.encode('ascii'))
    vlc_req.add_header('Authorization','Basic ' + auth_headers_enc.decode("ascii"))
    try:
        vlc_resp = urllib.request.urlopen(vlc_req)
        if (vlc_resp.getcode() == 200):
            vlc_data = json.loads(vlc_resp.read())
            return vlc_data
        elif (vlc_resp.getcode() == 401):
            print("Error talking to VLC - is the password set correctly?")
            return None
        else:
            print("Error talking to VLC - is it running and is the HTTP Interface active?")
            return None
    except urllib.error.URLError:
        print("Error talking to VLC - is it running and is the HTTP Interface active?")
        return None

def currently_playing(props, prop):
    status = vlc_request("status.json")
    if (status["state"] == "playing"):
        title = status["information"]["category"]["meta"]["title"]
        print(title)
        return title
    else:
        print("Nothing currently playing")
        return None

def toggle_pause(props, prop):
    status = vlc_request("status.json?command=pl_pause")
    if (status["state"] == "paused"):
        print("Paused item: " + status["information"]["category"]["meta"]["title"])
    elif (status["state"] == "playing"):
        print("Resumed playback of item: " + status["information"]["category"]["meta"]["title"])
    else:
        print("No item to play/pause")
    return ""

def skip(props, prop):
    status = vlc_request("status.json?command=pl_next")
    print("Skip button pressed")
    # Need to figure out how to get the currently playing one and return it


def get_playlist(props,prop):
    playlist_data = vlc_request("playlist.json")
    if playlist_data:
        children = playlist_data["children"][0]["children"]
        for item in children:
            print(item['name'])

def add_to_playlist_handler(props,prop):
    #add_to_playlist("")
    #playlist_prop = obs.obs_properties_get(props, "playlist")
    #print(obs.obs_property_description(playlist_prop))
    playlist_array = obs.obs_data_get_array(my_settings,"playlist")
    for i in range(obs.obs_data_array_count(playlist_array)):
        data_item = obs.obs_data_array_item(playlist_array,i)
        filepath = obs.obs_data_get_string(data_item,"value")
        mrl = "file:///" + filepath
        if is_in_playlist(mrl):
            remove_from_playlist(mrl)
            add_to_playlist(mrl)
        else:
            add_to_playlist(mrl)


def add_to_playlist(mrl):
    status = vlc_request("status.json?command=in_enqueue&input=" + urllib.parse.quote(mrl))
    playlist = vlc_request("playlist.json")
    last_item_uri = playlist["children"][0]["children"][-1]["uri"]
    last_item_title = playlist["children"][0]["children"][-1]["name"]
    if last_item_uri == mrl:
        print("Successfully added item to queue: " + last_item_title)
    return ""

    # Example of good request: http://127.0.0.1:8080/requests/status.json?command=in_enqueue&input=file:///D:\Users\Simon\Downloads\DownloadedVideos\[Hi10]_Hunter_X_Hunter_[BD_1080p]\(Hi10)_Hunter_X_Hunter_-_005_(BD_1080p)_(Coalgirls)_(ACE5FCCF).mkv

def remove_from_playlist_handler(props,prop):
    remove_from_playlist("")
    # TODO: Work out how to get filepath from props and prop

def remove_from_playlist(mrl):
    playlist = vlc_request("playlist.json")
    for item in playlist["children"][0]["children"]:
        if item["uri"] == mrl:
            status = vlc_request("status.json?command=pl_delete&id=" + item["id"])
            print("Successfully removed item: " + item["name"])

    return ""

def clear_playlist(props, prop):
    playlist = vlc_request("status.json?command=pl_empty")
    print("Playlist cleared")

def is_in_playlist(mrl):
    playlist = vlc_request("playlist.json")
    for item in playlist["children"][0]["children"]:
        if item["uri"] == mrl:
            return True
    return False

def list_library(props,prop):
    global file_directory
    file_list = []
    print("Listing videos in: " + file_directory  )
    for (dirpath, dirnames, filenames) in os.walk(file_directory):
        file_list.extend(filenames)
    print(file_list)
    return ""
