import logging
import os.path

import pygst
pygst.require('0.10')
import gst


class Transcoder:
    """Audio transcoder from variable formats to Skype-compliant WAVs."""

    def __init__(self, fn_source, fn_sink):
        self.on_done = None

        self.fn_source = os.path.abspath(fn_source)
        self.fn_sink = os.path.abspath(fn_sink)

        assert(os.path.exists(self.fn_source))

        self.pipeline = self._setup_pipeline()

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self._on_message)

    def _setup_pipeline(self):
        p_str = 'decodebin name=in ! audioconvert ! audioresample' \
                '! audio/x-raw-int, channels=1, width=16, rate=16000' \
                '! wavenc name=out'
        p = gst.parse_launch(p_str)

        source = gst.element_factory_make('filesrc')
        source.set_property('location', self.fn_source)

        sink = gst.element_factory_make('filesink')
        sink.set_property('location', self.fn_sink)

        p.add(source, sink)

        gst.element_link_many(source, p.get_by_name('in'))
        gst.element_link_many(p.get_by_name('out'), sink)

        return p

    def _on_message(self, bus, message):
        t = message.type

        if t == gst.MESSAGE_EOS:
            logging.debug('%s transcoded to %s.', self.fn_source, self.fn_sink)
        elif t == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            logging.error(err)
            logging.debug(debug)
        else:
            return

        self.pipeline.set_state(gst.STATE_NULL)

        if self.on_done:
            self.on_done()

    def run(self, on_done=None):
        self.pipeline.set_state(gst.STATE_PLAYING)
        self.on_done = on_done
