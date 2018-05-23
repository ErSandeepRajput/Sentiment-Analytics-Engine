import os
import logging
import sys
import time
import random
import string
from yowsup.layers.protocol_presence.protocolentities import *
from yowsup.layers.protocol_chatstate.protocolentities import *
from yowsup.layers.protocol_media.protocolentities import *
from yowsup.layers.protocol_media.mediauploader import MediaUploader
from yowsup.common.tools import Jid
from yowsup.common.optionalmodules import PILOptionalModule, AxolotlOptionalModule
from yowsup.layers.protocol_profiles.protocolentities import *
from yowsup.layers.protocol_contacts.protocolentities import *

from app.utils import helper
from app.utils import media_decrypter


entity = None

name = "sae"
ack_queue = []
logger = logging.getLogger(__name__)

def set_entity(instance):
    global entity
    entity = instance


def receive_message(self, message_entity):
    self.toLower(message_entity.ack())
    ack_queue.append(message_entity)


def prepate_answer(self, conversation, disconnect_after=True):
    make_presence(self)

    online(self)
    time.sleep(random.uniform(0.1, 0.4))

    ack_messages(self, conversation)

    start_typing(self, conversation)
    time.sleep(random.uniform(0.5, 1.4))

    stop_typing(self, conversation)
    
    if disconnect_after:
        disconnect(self)


def make_presence(self):
    self.toLower(PresenceProtocolEntity(name=name))


def online(self):
    self.toLower(AvailablePresenceProtocolEntity())


def disconnect(self):
    self.toLower(UnavailablePresenceProtocolEntity())


def start_typing(self, conversation):
    self.toLower(OutgoingChatstateProtocolEntity(
        OutgoingChatstateProtocolEntity.STATE_TYPING,
        Jid.normalize(conversation)
    ))


def stop_typing(self, conversation):
    self.toLower(OutgoingChatstateProtocolEntity(
        OutgoingChatstateProtocolEntity.STATE_PAUSED,
        Jid.normalize(conversation)
    ))


def ack_messages(self, conversation):
    queue = [message_entity for message_entity in ack_queue if same_conversation(message_entity, conversation)]

    queue = queue[-20:]

    for message_entity in queue:
        self.toLower(message_entity.ack(True))

        if message_entity in ack_queue:
            ack_queue.remove(message_entity)

    remove_conversation_from_queue(conversation)


def same_conversation(message_entity, conversation):
    return message_entity.getFrom() == conversation


def remove_conversation_from_queue(conversation):
    ack_queue[:] = [entity for entity in ack_queue if not same_conversation(entity, conversation)]


def decode_string(message):
    try:
        if type(message) is bytes:
            message = message.decode(encoding='latin1', errors='ignore')
        return message
    except:
        return message.decode('utf-8','ignore').encode("utf-8")
        
        

def send_message(str_message, conversation, disconnect_after=True):
    message = decode_string(str_message)
    
    prepate_answer(entity, conversation, disconnect_after)
    entity.toLower(helper.make_message(message, conversation))
    


def send_message_to(str_message, phone_number, disconnect_after=True):
    jid = Jid.normalize(phone_number)
    send_message(str_message, jid)
    
    
def send_image(path, conversation, caption=None):
    if os.path.isfile(path):
        media_send(entity, conversation, path, RequestUploadIqProtocolEntity.MEDIA_TYPE_IMAGE, caption)
    else:
        print("Image doesn't exists")
        

def send_image_to(path, phone_number, caption=None):
    jid = Jid.normalize(phone_number)
    send_image(path, jid, caption)


def send_video(path, conversation, caption=None):
    if os.path.isfile(path):
        media_send(entity, conversation, path, RequestUploadIqProtocolEntity.MEDIA_TYPE_VIDEO)
    else:
        print("Video doesn't exists")
        
        
def send_video_to(path, phone_number, caption=None):
    jid = Jid.normalize(phone_number)
    send_video(path, jid, caption)
    

def send_audio(path, conversation):
    if os.path.isfile(path):
        media_send(entity, conversation, path, RequestUploadIqProtocolEntity.MEDIA_TYPE_AUDIO)
    else:
        print("File doesn't exists")
        

def send_audio_to(path, phone_number):
    jid = Jid.normalize(phone_number)
    send_audio(path, jid)


def media_send(self, jid, path, media_type, caption=None):
    entity = RequestUploadIqProtocolEntity(media_type, filePath=path)
    fn_success = lambda success_entity, original_entity: on_request_upload_result(self, jid, media_type, path,
                                                                                    success_entity, original_entity,
                                                                                    caption)
    fn_error = lambda error_entity, original_entity: on_request_upload_error(self, jid, path, error_entity, original_entity)
    self._sendIq(entity, fn_success, fn_error)


def contact_picture(conversation, success_fn=None, preview=False):
    iq = GetPictureIqProtocolEntity(conversation, preview=preview)
    
    def got_picture(result_picture, picture_protocol_entity):
        path = "app/assets/profiles/%s_%s.jpg" % (picture_protocol_entity.getTo(), "preview" if result_picture.isPreview() else "full")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        result_picture.writeToFile(path)
        if success_fn:
            success_fn(picture_protocol_entity.getTo(), path)
    
    entity._sendIq(iq, got_picture)
    

def contact_picture_from(number, success_fn=None, preview=False):
    jid = Jid.normalize(number)
    contact_picture(jid, success_fn, preview)


def set_profile_picture(path, success=None, error=None):
    picture, preview = make_picture_and_preview(path)
    entity._sendIq(SetPictureIqProtocolEntity(entity.getOwnJid(), preview, picture), success, error)


def set_group_picture(path, group_jid, success=None, error=None):
    picture, preview = make_picture_and_preview(path)
    entity._sendIq(SetPictureIqProtocolEntity(group_jid, preview, picture), success, error)
        
        
def make_picture_and_preview(path):
    with PILOptionalModule(failMessage = "No PIL library installed, try install pillow") as imp:
        Image = imp("Image")
        src = Image.open(path)
        picture = src.resize((640, 640)).tobytes("jpeg", "RGB")
        preview = src.resize((96, 96)).tobytes("jpeg", "RGB")
        return picture, preview
                

def contact_status(jids, fn=None):
    def success(result, original):
        if (fn):
            fn(result.statuses)
            
    if isinstance(jids, list):
        iq = GetStatusesIqProtocolEntity(jids)
        entity._sendIq(iq, success)
    else:
        iq = GetStatusesIqProtocolEntity([jids])
        entity._sendIq(iq, success)
        
        
def contact_status_from(number, fn=None):
    jid = Jid.normalize(number)
    contact_status(jid, fn)


'''
Callbacks. Do not touch
'''
def on_request_upload_result(self, jid, media_type, file_path, result_request_upload_entity,
                             request_upload_entity, caption=None):
    if result_request_upload_entity.isDuplicate():
        do_send_media(self, media_type, file_path, result_request_upload_entity.getUrl(), jid,
                      result_request_upload_entity.getIp(), caption)
    else:
        success_fn = lambda file_path, jid, url: do_send_media(self,
                                                               media_type,
                                                               file_path,
                                                               url,
                                                               jid,
                                                               result_request_upload_entity.getIp(),
                                                               caption)
        media_uploader = MediaUploader(jid,
                                       self.getOwnJid(),
                                       file_path,
                                       result_request_upload_entity.getUrl(),
                                       result_request_upload_entity.getResumeOffset(),
                                       success_fn,
                                       on_upload_error(self, file_path, jid),
                                       on_upload_progress(self,
                                                          file_path,
                                                          jid,
                                                          result_request_upload_entity.getResumeOffset()),
                                       async=True)
        media_uploader.start()


def on_request_upload_error(self, jid, path, error_request_upload_iq_entity, request_upload_iq_entity):
    return


def do_send_media(self, media_type, file_path, url, to, ip=None, caption=None):
    if media_type == RequestUploadIqProtocolEntity.MEDIA_TYPE_IMAGE:
        entity = ImageDownloadableMediaMessageProtocolEntity.fromFilePath(file_path, url, ip, to, caption=caption)
        self.toLower(entity)
    elif media_type == RequestUploadIqProtocolEntity.MEDIA_TYPE_AUDIO:
        entity = AudioDownloadableMediaMessageProtocolEntity.fromFilePath(file_path, url, ip, to)
        self.toLower(entity)
    elif media_type == RequestUploadIqProtocolEntity.MEDIA_TYPE_VIDEO:
        entity = VideoDownloadableMediaMessageProtocolEntity.fromFilePath(file_path, url, ip, to, caption=caption)
        self.toLower(entity)


def on_upload_error(self, filePath, jid):
    return


def on_upload_progress(self, filePath, jid, progress):
    return


