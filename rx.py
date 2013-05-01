from __future__ import division
import rtlsdr
import numpy
import time
from scipy import signal
import bitarray
from pylab import *
import socket
import fir_coef

_chunk = lambda l, x: [l[i:i+x] for i in xrange(0, len(l), x)]

def _window(sequence, winSize, step=1):
	# Pre-compute number of chunks to emit
	numOfChunks = int(((len(sequence)-winSize)/step)+1)
	# Do the work
	for i in range(0,numOfChunks*step,step):
		yield sequence[i:i+winSize]


_snap = lambda levels, x: levels.flat[numpy.abs(levels - x).argmin()]

def sample(bittime):
	###print "trying to send 'hello world' at:", int(1/bittime), "bits per second"
	duration = 0.1 + bittime*8*11
	sdr = rtlsdr.RtlSdr()
	sdr.sample_rate = 2.4e6
	sdr.center_freq = 144.62e6
	sdr.gain = 'auto'
	# round to nearest 1024 samples
	sampleCt = round((duration*sdr.sample_rate)/1024)*1024
	###print sampleCt, "sampleCt"

	# trigger transmission
	
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	s.connect(("10.33.91.11", 9000))
	microseconds = int(bittime/2*1e6)
	###print microseconds, 'us'
	s.send(chr(microseconds))
	s.close()

	# get data
	samples = sdr.read_samples(sampleCt)
	return samples	

if __name__ == "__main__":
	samples = sample(0.00025)
	plot(samples, '.')
	ntaps = 10000
	txfreq = 144.64e6
	rxfreq = 144.62e6
	coeffs = fir_coef.filter('BP', txfreq-rxfreq-10e3, txfreq-rxfreq+10e3, 2.4e6, 'hamming', 10000)
	periodSamples = 0.00025/(1/2.4e6)/5
	print periodSamples
	movingAverage = np.ones(int(periodSamples))/periodSamples
	filtered = abs(numpy.convolve(samples, coeffs)[0:-ntaps+1])
	smoothed = numpy.convolve(filtered, movingAverage)
	plot(smoothed)
	show()
