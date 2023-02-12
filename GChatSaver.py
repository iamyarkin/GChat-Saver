import sys
import datetime

from g_python.gextension import Extension
from g_python.hmessage import Direction
from g_python.hparsers import HEntity

extension_info = {
    "title": "G-ChatSaver",
    "description": "Saves incoming chats",
    "version": "1.0",
    "author": "Yarkin"
}

ext = Extension(extension_info, sys.argv, silent=True)
ext.start()

entities = []

ext.write_to_console("\nLOGGING CHATS")

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
            file.write("------------------------------------------------------------------------------\n")
            file.write(f"[  You Joined a room at: {date_str}  ]\n")
            file.write("[Room Name : " + room_name + " ]\n")
            file.write("[Room Owner : " + owner_name + " ]\n")
            file.write("[Room Description : " + description + " ]\n")
            file.write("------------------------------------------------------------------------------\n")

def speech_in(msg):
    index, text, _, bubble, _, id = msg.packet.read('isiiii')
    now = datetime.datetime.now()
    date_str = now.strftime("[%Y-%m-%d %H:%M:%S]")
    entity = next((entity for entity in entities if entity.index == index), None)
    if entity:
        ext.write_to_console(f"{date_str} {entity.name}: {text}")
        with open("chat.txt", "a", encoding="ISO-8859-9") as file:  #You might like to change encoding to UTF-8
            file.write(f"{date_str} {entity.name}: {text}\n")
    else:
         ext.write_to_console(f"Incoming chat from unknown user: {text}")

def whisper(msg):
    index, text, _, bubble, _, id = msg.packet.read('isiiii')
    now = datetime.datetime.now()
    date_str = now.strftime("[%Y-%m-%d %H:%M:%S]")
    entity = next((entity for entity in entities if entity.index == index), None)
    if entity:
        ext.write_to_console(f"{date_str} {entity.name} (whisper): {text}")
        with open("chat.txt", "a", encoding="ISO-8859-9") as file:  #You might like to change encoding to UTF-8
            file.write(f"{date_str} {entity.name} (whisper): {text}\n")
    else:
        ext.write_to_console(f"Incoming whisper from unknown user: {text}")

def speech_shout(msg):
    index, text, _, bubble, _, id = msg.packet.read('isiiii')
    now = datetime.datetime.now()
    date_str = now.strftime("[%Y-%m-%d %H:%M:%S]")
    entity = next((entity for entity in entities if entity.index == index), None)
    if entity:
        ext.write_to_console(f"{date_str} {entity.name} (shout): {text}")
        with open("chat.txt", "a", encoding="ISO-8859-9") as file:  #You might like to change encoding to UTF-8
            file.write(f"{date_str} {entity.name} (shout): {text}\n")
    else:
        ext.write_to_console(f"Incoming shout from unknown user: {text}")

ext.intercept(Direction.TO_CLIENT, add_users, 'Users')
ext.intercept(Direction.TO_CLIENT, get_users, 'RoomReady')
ext.intercept(Direction.TO_CLIENT, speech_in, 'Chat')
ext.intercept(Direction.TO_CLIENT, speech_shout, 'Shout')
ext.intercept(Direction.TO_CLIENT, whisper, 'Whisper')
ext.intercept(Direction.TO_CLIENT, room_name, "GetGuestRoomResult")