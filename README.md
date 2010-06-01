SAX
===

The epitome of maturity.

Sunara got me obsessed with [EPIC SAX GUY](http://www.youtube.com/watch?v=VrdwhXNt4qw).

For some reason, sending her a billion e-mails while she's at work wasn't enough.

So, I wrote this to prank call her.

Usage
-----

    $ python sax.py
    Usage: sax.py [sax.mp3]

    sax.py: error: I need a beat.

OK

    $ python sax.py sax.mp3
    < CONNSTATUS ONLINE
    < CURRENTUSERHANDLE scottfoxtrot
    < USERSTATUS ONLINE
    echo123
    STATUS 11958: ROUTING
    STATUS 11958: ROUTING
    STATUS 11958: RINGING
    STATUS 11958: INPROGRESS
    11958 : INPUT FILE="/tmp/tmpJd9s42"
    11958 : OUTPUT FILE="/home/scott/Projects/sax/tmpu82TmG.wav"
    11958 : DURATION 1
    11958 : DURATION 2
    11958 : DURATION 3
    11958 : DURATION 4
    ...

Yup. Just give it some numbers to serenade.

    $ echo "+13107700023" | python sax.py sax.mp3
    ...

Oh yeah:

    $ play tmpu82TmG.wav
    Playing WAVE 'tmpu82TmG.wav' : Signed 16 bit Little Endian, Rate 16000 Hz, Mono

You can savor the response, forever.
