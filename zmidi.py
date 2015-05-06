#!/usr/bin/python3

import sys
import socket
import time

import zmq
from zocp import ZOCP

import rtmidi
from rtmidi.midiutil import open_midiport


class MidiInputHandler(object):
    def __init__(self, port, z):
        self.port = port
        self._wallclock = time.time()
        self.z = z

        
    def __call__(self, event, data=None):
        message, deltatime = event
        self._wallclock += deltatime
        z.receive_midi(self.port, self._wallclock, message)

        
class MidiInNode(ZOCP):
    # Constructor
    def __init__(self):
        super(MidiInNode, self).__init__()


    def run(self):
        self.register_string("Message", '', 're')
    
        while True:
            try:
                self.run_once()
            except (KeyboardInterrupt, SystemExit):
                break


    def receive_midi(self, port, clock, message):
        self.emit_signal("Message", str(message))
        
        command = message.pop(0)
        if command == 0xB0:
            # handle Continuous Controller
            [controller, value] = message
            controller = "/" + str(controller)
            if controller not in self.capability:
                self.register_int(controller, 0, 're', 0, 127)

            self.emit_signal(controller, value)

                
if __name__ == '__main__':
    z = MidiInNode()
    z.set_name("zmidi_in@%s" % socket.gethostname())

    port = sys.argv[1] if len(sys.argv) > 1 else None
    try:
        midi_in, port_name = open_midiport(port)
    except (EOFError, KeyboardInterrupt):
        sys.exit()

    print("Attaching MIDI input callback handler.")
    midi_in.set_callback(MidiInputHandler(port_name, z))    
    
    z.start()
    z.run()
    z.stop()
    del z

    print("Closing MIDI port...")
    del midi_in
