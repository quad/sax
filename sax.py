import os
import os.path
import re
import sys
import traceback

from optparse import OptionParser
from tempfile import NamedTemporaryFile

import pygtk
pygtk.require('2.0')

import gobject

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop


gobject.threads_init()
ML = gobject.MainLoop()


class Call(object):
    PREFIX_STATUS = 'STATUS '
    PREFIX_VAA_OUTPUT_STATUS = 'VAA_INPUT_STATUS '
    CALL_STATES_DONE = ('FINISHED', 'CANCELLED')

    def __init__(self, ringer, phone_number):
        self.Invoke = ringer.Invoke

        call_info = self.Invoke('CALL ' + phone_number)

        m = ringer.CALL_RE.match(call_info)
        assert m, call_info
        self.number = m.group('number')

        ringer.calls[self.number] = self

        self.status = None
        self.input = None
        self.output = None
        self.when_done = None

    def Notify(self, message):
        if message.startswith(self.PREFIX_STATUS):
            self.status = message[len(self.PREFIX_STATUS):]

            print 'STATUS %s: %s' % (self.number, self.status)

            if self.status in self.CALL_STATES_DONE:
                gobject.timeout_add_seconds(0, self.when_done)
            else:
                # Set the streams.
                self.input, self.output = self.input, self.output
        elif message.startswith(self.PREFIX_VAA_OUTPUT_STATUS):
            state = message[len(self.PREFIX_VAA_OUTPUT_STATUS):]

            if state == 'FALSE' and self.status not in self.CALL_STATES_DONE:
                r = self.Invoke('SET CALL %s STATUS FINISHED' % (self.number))
                assert r == 'CALL %s STATUS FINISHED' % (self.number), r
        else:
            print "%s : %s" % (self.number, message)

    @property
    def input(self):
        return self._input

    @input.setter
    def input(self, value):
        if self.status == 'INPROGRESS' and value:
            cmd = 'ALTER CALL %s SET_INPUT file="%s"' % (self.number, value)
            r = self.Invoke(cmd)
            assert cmd == r, r

        self._input = value

    @property
    def output(self):
        return self._output

    @output.setter
    def output(self, value):
        if self.status == 'INPROGRESS' and value:
            cmd = 'ALTER CALL %s SET_OUTPUT file="%s"' % (self.number, value)
            r = self.Invoke(cmd)
            assert cmd == r, r

        self._output = value


class Ringer(dbus.service.Object):
    CALL_RE = re.compile('CALL (?P<number>\d+) (?P<message>.*)')

    def __init__(self, music_fn):
        bus = dbus.SessionBus()
        dbus.service.Object.__init__(self, bus, '/com/Skype/Client')

        self.calls = {}
        self.filename = music_fn

        skype = bus.get_object('com.Skype.API', '/com/Skype')
        self.Invoke = skype.Invoke
        assert self.Invoke('NAME SergeyStepanov') == 'OK'
        assert self.Invoke('PROTOCOL 7') == 'PROTOCOL 7'

    def call(self, phone_number):
        with NamedTemporaryFile(suffix='.wav', dir=os.getcwd(), delete=False) as of:
            c = Call(self, phone_number)
            c.input = self.filename
            c.output = of.name

        return c

    @dbus.service.method(dbus_interface='com.Skype.API.Client')
    def Notify(self, message):
        m = self.CALL_RE.match(message)
        if m:
            # DBus swallows even printing exceptions.
            try:
                self.calls[m.group('number')].Notify(m.group('message'))
            except:
                traceback.print_exc()
        else:
            print "< " + message


def main(ringer):
    n = sys.stdin.readline().strip()
    if n:
        c = r.call(n)
        c.when_done = lambda: main(ringer)
    else:
        ML.quit()


if __name__ == '__main__':
    p = OptionParser('%prog [sax.mp3]',
                     epilog="Play some audio, preferrably EPIX SAX GUY's " \
                     "sweet solo, to whoever you specify on standard-input. " \
                     "Skype-friendly names and numbers, please.")
    (options, args) = p.parse_args()

    if not args:
        p.error('I need a beat.')
    elif not os.path.exists(args[0]):
        p.error('Your beat is subpar.')

    DBusGMainLoop(set_as_default=True)

    with NamedTemporaryFile() as fn:
        # Here because pygst gets impolite with our command-line.
        from transcode import Transcoder

        r = Ringer(fn.name)
        Transcoder(args[0], fn.name).run(lambda: main(r))

        ML.run()
