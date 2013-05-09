from __future__ import division
import rtlsdr
import numpy
import time
from scipy import signal
import bitarray
import socket
import fir_coef
import rle
from pylab import *

_chunk = lambda l, x: [l[i:i+x] for i in xrange(0, len(l), x)]

_snap = lambda levels, x: levels.flat[numpy.abs(levels - x).argmin()]

def getMessageSamples(bittime):
	print "trying to send 'hello world' at:", int(1/bittime), "bits per second"
	duration = 0.5
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
	movingAverage = numpy.ones(int(periodSamples/100))/int(periodSamples/100)
	smoothed = signal.fftconvolve(pulseTrain, movingAverage)
	meanAmplitude = numpy.mean(pulseTrain)
	thresholded = map(lambda x: x > meanAmplitude, pulseTrain)
	# duration-encoded thresholded values
	durationEncoded = list(rle.runlength_enc(thresholded))
	durationEncoded = filter(lambda x: x[0] < 2000, durationEncoded)
	figure()
	from collections import Counter
	cfalse = Counter([x[0] for x in durationEncoded if x[1] == False])
	ctrue = Counter([x[0] for x in durationEncoded if x[1] == True])
	f = numpy.array(cfalse.items()).T
	fmean = numpy.mean(f[0])
	t = numpy.array(ctrue.items()).T
	tmean = numpy.mean(t[0])
	plot(f[0], f[1], 'k.')
	vlines(tmean, 0, max(t[1]), color='r', linestyles='solid')
	plot(t[0], t[1], 'r.')
	vlines(fmean, 0, max(f[1]), color='k', linestyles='solid')
	# find the start and end of the transmission
	means = {True: tmean, False: fmean}
	processed = [(l > means[s], s) for (l, s) in durationEncoded]
	
	# expand double-length marks to two marks
	regularized = []
	for (l, s) in processed:
		if l == True:
			regularized.append(s)
			regularized.append(s)
		if l == False:
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
	import struct
	period = 1/4000
	samples = getMessageSamples(period)
	cleaned = clean(samples)
	figure()
	t = linspace(0, len(cleaned)/2.4e6, len(cleaned))
	tstart = t[(numpy.abs(cleaned) > 0.5).argmax()]
	tstop = t[-(numpy.abs(cleaned) > 0.5)[::-1].argmax()]
	vlines(tstart, 0, 1, color='r', linestyles='solid', lw = 10)	
	vlines(tstop, 0, 1, color='k', linestyles='solid', lw = 10)	
	plot(t, numpy.abs(cleaned))
	demoded = demod(cleaned)
	decoded = decode(demoded)
	print len(decoded)/(tstop-tstart)
	print decoded[0:-32].tobytes()
	import crc	
	CRCofMessage = hex(crc.crc32(decoded[0:-32].tobytes()))[2::]
	CRCfromMessage = ''.join([hex(ord(x))[2::] for x in decoded[-32::].tobytes()])
	print CRCofMessage, CRCfromMessage
	print "good?", CRCofMessage == CRCfromMessage
	show()
