import sys, logging, config

from yowsup.layers.auth import AuthError
from yowsup.layers.axolotl.props import PROP_IDENTITY_AUTOTRUST
from yowsup.stacks import YowStackBuilder
from yowsup.layers import YowLayerEvent
from yowsup.layers.network import YowNetworkLayer

from app.sae.layer import saeLayer


credentials = (config.credentials['phone'], config.credentials['password'])
encryption = True


class saeStack(object):
    def __init__(self):
        builder = YowStackBuilder()

        self.stack = builder\
            .pushDefaultLayers(encryption)\
            .push(saeLayer)\
            .build()

        self.stack.setCredentials(credentials)
        self.stack.setProp(saeLayer.PROP_CONTACTS,  list(config.contacts.keys()))
        self.stack.setProp(PROP_IDENTITY_AUTOTRUST, True)

    def start(self):
        print("[Whatsapp] sae started\n")

        self.stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))

        try:
            self.stack.loop(timeout=0.5, discrete=0.5)
        except AuthError as e:
            print("Auth Error, reason %s" % e)
        except KeyboardInterrupt:
            print("\nYowsdown")
            sys.exit(0)
        
def instance():
    return saeStack()

if __name__ == "__main__":
    c = saeStack()
    c.start()
