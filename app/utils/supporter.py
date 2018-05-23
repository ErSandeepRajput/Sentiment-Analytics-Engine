from yowsup.layers.protocol_messages.protocolentities import *
import string
from pprint import pprint

log_file = "saelog.txt"
me = "5218114140740@s.whatsapp.net"

def get_who_send(message_entity):
    who = message_entity.getFrom()
    if message_entity.isGroupMessage():
        who = message_entity.getParticipant()
        
    return who
    
    
def sender_name(message_entity):
    name = message_entity.getNotify()
    name = name.encode('latin-1')
    name = name.decode('utf-8')
    return name


def get_conversation(message_entity):
    return message_entity.getFrom()

def is_text_message(message_entity):
    return message_entity.getType() == "text"

def is_media_message(message_entity):
    return message_entity.getType() == "media"


def is_image_media(message_entity):
    if is_media_message(message_entity):
        return message_entity.getMediaType() == "image"


def is_location_media(message_entity):
    if is_media_message(message_entity):
        return message_entity.getMediaType() == "location"

def is_vcard_media(message_entity):
    if is_media_message(message_entity):
        return message_entity.getMediaType() == "vcard"


def make_message(msg, conversation):
    outgoing_message_enity = TextMessageProtocolEntity(msg, to=conversation)
    return outgoing_message_enity


def log_txt(message_entity):
    who = who = sender_name(message_entity)

    conversation = message_entity.getFrom()

    message = message_entity.getBody()
    message = message.strip()
    message = ''.join(filter(lambda x: x in string.printable, message))
    message = message.strip()
    
    dirty = message_entity.getBody().strip()

    print("logging something...")

    file = open(log_file, "a")
    file.write(
        "------------------------" +
        "\n" + "Sender:" + "\n" + who + "\n" + "Number sender:" + "\n" + conversation +
        "\n" + "Real msg:" + "\n" + dirty + "\n" +
        "\n" + "Clean msg:" + "\n" + message + "\n" +
        "------------------------" + "\n" + "\n")
    file.close()
    

def log(message_entity):
    pprint(vars(message_entity))
    

def message(message):
    message = clean_message(message)
    if is_command(message):
        return message[1:]
    else:
        return message


def clean_message(message_entity):
    message = message_entity.getBody()
    message = message.strip()
    return message

def is_command(message):
    saeShorcut = message[:1]
    return saeShorcut == "!"


def nice_list(list):
    return "[" + ", ".join( str(x) for x in list) + "]"
    

def command(message_entity):
    command = ""
    try:
        command = message(message_entity).split(' ', 1)[0]
    except IndexError:
        print("Command error")
    
    return command
    
    
def predicate(message_entity):
    rest = ""
    try:
        rest = message(message_entity).split(' ', 1)[1]
    except IndexError:
        pass
    
    return rest
    
