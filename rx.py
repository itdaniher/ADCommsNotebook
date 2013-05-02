from __future__ import division
import rtlsdr
import numpy
import time
from scipy import signal
import bitarray
import socket
import fir_coef
import rle

_chunk = lambda l, x: [l[i:i+x] for i in xrange(0, len(l), x)]

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
	s.connect(("10.33.91.11", 9001))
	microseconds = int(bittime/2*1e6)
	###print microseconds, 'us'
	s.send(chr(microseconds))
	s.close()

	# get data
	samples = sdr.read_samples(sampleCt)
	print "sampled"
	return samples	

def clean(samples):
	ntaps = 500
	txfreq = 144.64e6
	rxfreq = 144.62e6
	periodSamples = 0.00025/(1/2.4e6)
	print periodSamples
	coeffs = fir_coef.filter('BP', txfreq-rxfreq-10e3, txfreq-rxfreq+10e3, 2.4e6, 'hamming', ntaps)
	movingAverage = numpy.ones(int(periodSamples/5))/(periodSamples/5)
	filtered = abs(signal.convolve(samples, coeffs)[0:-ntaps+1])
	#smoothed = numpy.convolve(filtered, movingAverage)
	print "cleaned"
	return filtered#smoothed	


def demod(pulseTrain):
	meanAmplitude = numpy.mean(pulseTrain)
	
	thresholded = map(lambda x: x > meanAmplitude, pulseTrain)
	# duration-encoded thresholded values
	durationEncoded = list(rle.runlength_enc(thresholded))
	
	# find the start and end of the transmission
	minmax = [i for i, x in enumerate(durationEncoded) if (x[1] == False) and (x[0] > 1000)]
	print "minmax:", minmax
	# trim off before/after samples
	durationEncoded = durationEncoded[minmax[0]+1:minmax[-1]]

	###print durationEncoded, 'durationEncoded'

	# snap to ideal mean levels for high and low
	# take the "average" duration, assuming 50% zero one division
	meanDuration = numpy.mean([l for (l, s) in durationEncoded])
	# double length mark, happens with a change in symbols ie) 01 or 10
	high = int(numpy.mean([l for (l, s) in durationEncoded if l > meanDuration]))
	# single length mark, happens with same symbols ie) 00 or 11
	low = int(numpy.mean([l for (l, s) in durationEncoded if l <= meanDuration]))
	# make an array of possible mark durations, include zero to take out the trash
	levels = numpy.array([0, low, high])
	# snap the durations to the levels generated above
	processed = [(_snap(levels, l), s) for (l, s) in durationEncoded]
	###print levels
	regularized = []

	# expand double-length marks to two marks
	for (l, s) in processed:
		if l == high:
			regularized.append(s)
			regularized.append(s)
		if l == low:
			regularized.append(s)
	print "demodulated"
	return regularized

def decode(data):
	# recursive manchester encoding demodulator and resymbolifyier
	bits = bitarray.bitarray(endian='little')
	for i, x in enumerate(_chunk(data, 2)):
		if x == [True, True]:
			data.insert(i*2, False)
			return demod(data)
		if x == [False, False]:
			data.insert(i*2, True)
			return demod(data)
		if x == [True, False]:
			bits.append(False)
		if x == [False, True]:
			bits.append(True)
	print "decoded"
	return bits

if __name__ == "__main__":
	f = open("data.json", 'a')
	while True:
		samples = sample(0.00025)
		cleaned = clean(samples)
		demoded = demod(cleaned)
		decoded = decode(demoded)
		print decoded.tobytes()
		if decoded.tobytes() != "hello world":
			f.write(json.dumps((samples, cleaned, demoded, decoded)))
