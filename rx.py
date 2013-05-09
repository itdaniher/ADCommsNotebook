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

def getMessageSamples(bittime):
	print "trying to send 'hello world' at:", int(1/bittime), "bits per second"
	duration = 2*bittime*8*11+0.2
	sdr = rtlsdr.RtlSdr()
	sdr.sample_rate = 2.4e6
	sdr.center_freq = 144.62e6
	sdr.gain = 'auto'
	# round to nearest 1024 samples
	sampleCt = round((duration*sdr.sample_rate)/1024)*1024

	# trigger transmission
	
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	s.connect(("10.33.91.11", 9000))
	microseconds = int(bittime/2*1e6)
	s.send(chr(microseconds))
	s.close()

	# get data
	samples = sdr.read_samples(sampleCt)
	return samples	

def clean(samples):
	ntaps = 512
	txfreq = 144.64e6
	rxfreq = 144.62e6
	# generate the coefficients for a finite impulse response filter with a 20kilohertz bandwidth centered around our relative frequency
	coeffs = fir_coef.filter('BP', txfreq-rxfreq-10e3, txfreq-rxfreq+10e3, 2.4e6, 'hamming', ntaps)
	# apply the filter
	filtered = signal.fftconvolve(samples, coeffs)[0:-ntaps+1]
	return filtered


def demod(messageSamples):
	periodSamples = period/(1/2.4e6)
	pulseTrain = numpy.abs(messageSamples)
	movingAverage = numpy.ones(int(periodSamples/5))/int(periodSamples/5)
	smoothed = signal.fftconvolve(pulseTrain, movingAverage)
	meanAmplitude = numpy.mean(pulseTrain)
	
	thresholded = map(lambda x: x > meanAmplitude, pulseTrain)
	# duration-encoded thresholded values
	durationEncoded = list(rle.runlength_enc(thresholded))
	
	# find the start and end of the transmission
	minmax = [i for i, x in enumerate(durationEncoded) if (x[1] == False) and (x[0] > 2000)]
	print "minmax:", minmax
	# trim off before/after samples
	durationEncoded = durationEncoded[minmax[0]+1:minmax[-1]]

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
	
	# expand double-length marks to two marks
	regularized = []
	for (l, s) in processed:
		if l == high:
			regularized.append(s)
			regularized.append(s)
		if l == low:
			regularized.append(s)
	return regularized

def decode(data):
	# recursive manchester encoding demodulator and resymbolifyier
	bits = bitarray.bitarray(endian='little')
	for i, x in enumerate(_chunk(data, 2)):
		if x == [True, True]:
			data.insert(i*2, False)
			return decode(data)
		if x == [False, False]:
			data.insert(i*2, True)
			return decode(data)
		if x == [True, False]:
			bits.append(False)
		if x == [False, True]:
			bits.append(True)
	return bits

if __name__ == "__main__":
	period = 1/4000
	samples = getMessageSamples(period)
	cleaned = clean(samples)
	demoded = demod(cleaned)
	decoded = decode(demoded)
	import crc
	print crc.reverse_crc(decoded, decoded[-32::])
	rxed = [hex(ord(x))[2::] for x in decoded.tobytes()]
	txed = ['68', '65', '6c', '6c', '6f', '20', '77', '6f', '72', '6c', '64', 'd4', 'a1', '18', '5']
	print rxed
	print txed
