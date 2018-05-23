from blinker import signal

initialized = signal('mac_initialized')



message_received = signal('message_received') 
command_received = signal('command_received') 


receipt = signal('message_receipted')
ack = signal('message_ack')
