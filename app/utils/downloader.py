import os

from yowsup.layers.protocol_media.mediadownloader import MediaDownloader
from app.utils import helper
from app.utils import media_decrypter

def get_file(message_entity):
    enc_path = download_enc(message_entity)
    out_file = decrypt_file(message_entity, enc_path)
    

    try:
        os.remove(enc_path)
    except OSError:
        pass
    
    return out_file
    

def download_enc(message_entity):
    url = message_entity.getMediaUrl()
    return MediaDownloader().download(url.decode('ASCII'))
    
  
def decrypt_file(message_entity, enc_path):
    key = message_entity.getMediaKey()
    out = ""
    
    if helper.is_image_media(message_entity):
        out = os.path.splitext(enc_path)[0] + '.jpg'
    
    return media_decrypter.decrypt_file(enc_path, key, out)
