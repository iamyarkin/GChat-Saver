import sys
import datetime
import os
import json
from g_python.gextension import Extension
from g_python.hmessage import Direction
from g_python.hparsers import HEntity

extension_info = {
    "title": "GChatSaver",
    "description": "Save your incoming chats and the rooms you visit",
    "version": "1.2",
    "author": "Yarkin"
}

ext = Extension(extension_info, sys.argv, silent=True)
ext.start()

entities = []

def add_users(message):
    entities.extend(HEntity.parse(message.packet))

def get_users(_):
    entities.clear()

def room_name(room):
    packet = room.packet
    enter_room, flat_id, room_name, owner_id, owner_name, door_mode, user_count, max_user_count, description, trade_mode, score, ranking, category_id = packet.read("bisisiiisiiii")
    now = datetime.datetime.now()
    date_str = now.strftime("[%Y-%m-%d %H:%M:%S]")
    tags = [packet.read_string() for _ in range(packet.read_int())]
    multi_use = packet.read_int()
    if enter_room:
        with open("chat.txt", "a", encoding="ISO-8859-9") as file:
            file.write("------------------------------------------------------------------------------\n[ You Joined a room at : " + date_str + " ]\n[ Room Name : " + room_name + " ]\n[ Room Owner : " + owner_name + " ]\n[ Room Description : " + description + " ]\n------------------------------------------------------------------------------\n")

try:
    with open("gchat.json", "r") as f:
        config = json.load(f)
        filtered_users = config.get("filtered_users", [])
        filtered_words = config.get("filtered_words", [])
except FileNotFoundError:
    filtered_users = []
    filtered_words = []
    config = {}

def save_config():
    with open("gchat.json", "w") as f:
        json.dump(config, f, indent=4)

def speech_in(msg):
    index, text, _, bubble, _, id = msg.packet.read('isiiii')
    now = datetime.datetime.now()
    date_str = now.strftime("[%Y-%m-%d %H:%M:%S]")
    entity = next((entity for entity in entities if entity.index == index), None)
    if entity and entity.name.lower() in map(str.lower, filtered_users):
        return
    words = text.lower().split()
    if any(word == filtered_word for word in words for filtered_word in filtered_words):
        return
    if entity:
        ext.write_to_console(f"{date_str} {entity.name}: {text}")
        with open("chat.txt", "a", encoding="ISO-8859-9") as file: 
            file.write(f"{date_str} {entity.name}: {text}\n")
    else:
         ext.write_to_console(f"Incoming chat from unknown user: {text}")

def whisper(msg):
    index, text, _, bubble, _, id = msg.packet.read('isiiii')
    now = datetime.datetime.now()
    date_str = now.strftime("[%Y-%m-%d %H:%M:%S]")
    entity = next((entity for entity in entities if entity.index == index), None)
    if entity and entity.name.lower() in map(str.lower, filtered_users):
        return
    words = text.lower().split()
    if any(word == filtered_word for word in words for filtered_word in filtered_words):
        return
    if entity:
        ext.write_to_console(f"{date_str} {entity.name} (whisper): {text}")
        with open("chat.txt", "a", encoding="ISO-8859-9") as file: 
            file.write(f"{date_str} {entity.name} (whisper): {text}\n")
    else:
         ext.write_to_console(f"Incoming whisper from unknown user: {text}")

def speech_shout(msg):
    index, text, _, bubble, _, id = msg.packet.read('isiiii')
    now = datetime.datetime.now()
    date_str = now.strftime("[%Y-%m-%d %H:%M:%S]")
    entity = next((entity for entity in entities if entity.index == index), None)
    if entity and entity.name.lower() in map(str.lower, filtered_users):
        return
    words = text.lower().split()
    if any(word == filtered_word for word in words for filtered_word in filtered_words):
        return
    if entity:
        ext.write_to_console(f"{date_str} {entity.name} (shout): {text}")
        with open("chat.txt", "a", encoding="ISO-8859-9") as file: 
            file.write(f"{date_str} {entity.name} (shout): {text}\n")
    else:
         ext.write_to_console(f"Incoming shout from unknown user: {text}")

def speech_out(message):
    global filtered_users, filtered_words, config

    if "filtered_users" in config:
        filtered_users = config["filtered_users"]
    else:
        filtered_users = []

    if "filtered_words" in config:
        filtered_words = config["filtered_words"]
    else:
        filtered_words = []

    (text, color, index) = message.packet.read('sii')
    if text.lower() == ':gchat':
        message.is_blocked = True
        os.startfile('chat.txt', 'edit')
        ext.send_to_client('{in:Whisper}{i:-1}{s:"You have successfully opened the "chat.txt" file."}{i:0}{i:34}{i:0}{i:-1}')
    
    elif text.lower().startswith(':uf '):
        name = text.split(' ')[1].strip('"')
        if name.lower() not in [n.lower() for n in filtered_users]:
            filtered_users.append(name)
            config["filtered_users"] = filtered_users
            save_config()
            message.is_blocked = True
            ext.send_to_client('{in:Whisper}{i:-1}{s:"You have added ' + name + ' to the filtered users list."}{i:0}{i:34}{i:0}{i:-1}')
        else:
            message.is_blocked = True
            ext.send_to_client('{in:Whisper}{i:-1}{s:"' + name + ' is already in the filtered users list."}{i:0}{i:34}{i:0}{i:-1}')

    elif text.lower().startswith(':uuf '):
        name = text.split(' ')[1].strip('"')
        if name.lower() in [n.lower() for n in filtered_users]:
            filtered_users = [n for n in filtered_users if n.lower() != name.lower()]
            config["filtered_users"] = filtered_users
            save_config()
            message.is_blocked = True
            ext.send_to_client('{in:Whisper}{i:-1}{s:"You have removed ' + name + ' from the filtered users list."}{i:0}{i:34}{i:0}{i:-1}')
        else:
            message.is_blocked = True
            ext.send_to_client('{in:Whisper}{i:-1}{s:"' + name + ' is not in the filtered users list."}{i:0}{i:34}{i:0}{i:-1}')

    elif text.lower().startswith(':wf '):
        word = text.split(' ')[1].strip('"')
        if word.lower() not in [w.lower() for w in filtered_words]:
            filtered_words.append(word)
            config["filtered_words"] = filtered_words
            save_config()
            message.is_blocked = True
            ext.send_to_client('{in:Whisper}{i:-1}{s:"You have added ' + word + ' to the filtered word list."}{i:0}{i:34}{i:0}{i:-1}')
        else:
            message.is_blocked = True
            ext.send_to_client('{in:Whisper}{i:-1}{s:"' + word + ' is already in the filtered word list."}{i:0}{i:34}{i:0}{i:-1}')

    elif text.lower().startswith(':wuf '):
        word = text.split(' ')[1].strip('"')
        if word.lower() in [w.lower() for w in filtered_words]:
            filtered_words = [w for w in filtered_words if w.lower() != word.lower()]
            config["filtered_words"] = filtered_words
            save_config()
            message.is_blocked = True
            ext.send_to_client('{in:Whisper}{i:-1}{s:"You have removed ' + word + ' from the filtered words list."}{i:0}{i:34}{i:0}{i:-1}')
        else:
            message.is_blocked = True
            ext.send_to_client('{in:Whisper}{i:-1}{s:"' + word + ' is not in the filtered words list."}{i:0}{i:34}{i:0}{i:-1}') 

    elif text.lower().startswith(':gclearf'):
        config["filtered_users"] = []
        config["filtered_words"] = []
        save_config()
        filtered_users = []
        filtered_words = []
        message.is_blocked = True
        ext.send_to_client('{in:Whisper}{i:-1}{s:"You have deleted all filters."}{i:0}{i:34}{i:0}{i:-1}')

    elif text.lower().startswith(':gchatfilters'):
        message.is_blocked = True
        ext.send_to_client('{in:Whisper}{i:-1}{s:":uf "user" adds a user filter.\n:uuf "user" removes a user filter.\n:wf "word" adds a word filter.\n:wuf "word" removes a word filter.\n:gclearf clears all filters."}{i:0}{i:34}{i:0}{i:-1}')    

ext.intercept(Direction.TO_SERVER, speech_out, 'Chat')
ext.intercept(Direction.TO_CLIENT, add_users, 'Users')
ext.intercept(Direction.TO_CLIENT, get_users, 'RoomReady')
ext.intercept(Direction.TO_CLIENT, speech_in, 'Chat')
ext.intercept(Direction.TO_CLIENT, speech_shout, 'Shout')
ext.intercept(Direction.TO_CLIENT, whisper, 'Whisper')
ext.intercept(Direction.TO_CLIENT, room_name, "GetGuestRoomResult")
