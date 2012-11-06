#!/usr/bin/env python

# AppleCassette - an Apple 1 + 2 cassette file parser
# Nick Lambourne, www.lamb-chop.co.uk
# Nov 2012, inspired by ApplePy project

import array
import pygame
import numpy
import struct
import sys
import wave
import aifc

class Speaker:
    
    CPU_CYCLES_PER_SAMPLE = 60
    CHECK_INTERVAL = 1000
    
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 1)
        pygame.init()
        self.reset()
    
    def toggle(self, cycle):
        if self.last_toggle is not None:
            l = (cycle - self.last_toggle) / Speaker.CPU_CYCLES_PER_SAMPLE
            self.buffer.extend([0, 0.8] if self.polarity else [0, -0.8])
            self.buffer.extend((l - 2) * [0.5] if self.polarity else [-0.5])
            self.polarity = not self.polarity
        self.last_toggle = cycle
    
    def reset(self):
        self.last_toggle = None
        self.buffer = []
        self.polarity = False
    
    def play(self):
        sample_array = numpy.array(self.buffer)
        sound = pygame.sndarray.make_sound(sample_array)
        sound.play()
        self.reset()
    
    def update(self, cycle):
        if self.buffer and (cycle - self.last_toggle) > self.CHECK_INTERVAL:
            self.play()


class Cassette:

    def __init__(self, fn):
        self.wav = wave.open(fn, "r")
        self.raw = self.wav.readframes( self.wav.getnframes() )

        print "Sample Width: ", self.wav.getframerate()
        print "Sample Rate: ", self.wav.getsampwidth()
        print "Num Samples: ", self.wav.getnframes()

    def get_sample(self, index):
       intData = 0
       i = index * self.wav.getsampwidth()
       for j in range( 0, self.wav.getsampwidth() ):
          intData += (ord(self.raw[i + j]) & 0xFF) << (8 * j)
#          print ord(self.raw[i + j]), " ", str(intData)
       if intData & 0x80000000: #negative?
          intData &= 0x8000000
          intData = -intData
       return intData

    def write_tape(self, filename):
       out = open( filename, "wb" )
       for i in range(self.wav.getnframes()):
          out.write( str(self.get_sample( i )) )
          out.write( "\n" )
       out.close()

    def dump(self, file_name ):
       print "dump"


def usage():
    print >>sys.stderr, "AppleCassette - an Apple 1 + 2 cassette parser"
    print >>sys.stderr, "Nick Lambourne"
    print >>sys.stderr
    print >>sys.stderr, "Usage: applecassette.py [options]"
    print >>sys.stderr
    print >>sys.stderr, "    -c, --cassette Cassette wav file to load"
    print >>sys.stderr, "    -q, --quiet    Quiet mode, no sounds (default sounds)"
    sys.exit(1)


def get_options():
    class Options:
        def __init__(self):
            self.cassette = None
            self.quiet = False

    options = Options()
    a = 1
    while a < len(sys.argv):
        if sys.argv[a].startswith("-"):
            if sys.argv[a] in ("-c", "--cassette"):
                a += 1
                options.cassette = sys.argv[a]
            elif sys.argv[a] in ("-q", "--quiet"):
                options.quiet = True
            else:
                usage()
        else:
            usage()
        a += 1

    return options

if __name__ == "__main__":
    options = get_options()
    speaker = None if options.quiet else Speaker()

    #read the initial data in here - if it fails, we'll abort early
    cassette = Cassette(options.cassette) if options.cassette else None
  
    cassette.write_tape( "tape.out" )
