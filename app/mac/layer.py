import time
import random
import shutil, os, logging

from app.utils import helper
from app.sae import sae, signals
from app.receiver import receiver
from app.models.message import Message

from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_contacts.protocolentities import *
from yowsup.layers.protocol_groups.protocolentities import *

from yowsup.layers.protocol_media.mediadownloader import MediaDownloader

class saeLayer(YowInterfaceLayer):
    PROP_CONTACTS = "whatsapp.contacts"

    def __init__(self):
        super(saeLayer, self).__init__()
    
    @ProtocolEntityCallback("success")
    def on_success(self, success_entity):
        sae.set_entity(self)
        contacts = self.getProp(self.__class__.PROP_CONTACTS, [])
        contact_entity = GetSyncIqProtocolEntity(contacts)
        self._sendIq(contact_entity, self.on_sync_result, self.on_sync_error)
        signals.initialized.send(self)

    def on_sync_result(self, result_sync_iq_entity, original_iq_entity):
        pass


    def on_sync_error(self, error_sync_iq_entity, original_iq_entity):
        pass



    @ProtocolEntityCallback("receipt")
    def on_receipt(self, entity):
        self.toLower(entity.ack())


    @ProtocolEntityCallback("message")
    def on_message(self, message_entity):
        sae.receive_message(self, message_entity)
        

        message = Message(message_entity)
        if message.valid:
            signals.message_received.send(message)
            if helper.is_command(message.message):
                signals.command_received.send(message)
            
        sae.disconnect(self)
            
    def send_message_signal(self, message_entity):
        message = Message(message_entity)
        signals.message_received.send(message)
        if helper.is_command(message.message):
            signals.command_received.send(message)
            


