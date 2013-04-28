from __future__ import division
import rtlsdr
import numpy
import time
import scipy
import bitarray

import rle

_chunk = lambda l, x: [l[i:i+x] for i in xrange(0, len(l), x)]

def _window(sequence, winSize, step=1):
	# Pre-compute number of chunks to emit
	numOfChunks = int(((len(sequence)-winSize)/step)+1)
	# Do the work
	for i in range(0,numOfChunks*step,step):
		yield sequence[i:i+winSize]


_snap = lambda levels, x: levels.flat[numpy.abs(levels - x).argmin()]

def sample(bittime):
	duration = 0.1 + bittime*8*11 + 0.2
	sdr = rtlsdr.RtlSdr()
	sdr.sample_rate = 2.4e6
	sdr.center_freq = 144.62e6
	sdr.gain = 'auto'
	# round to nearest 1024 samples
	sampleCt = round((duration*sdr.sample_rate)/1024)*1024


	# trigger transmission
	import socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	s.connect(("10.33.91.11", 9000))
	microseconds = int(bittime/5*1e6)
	print microseconds
	s.send(chr(microseconds))
	s.close()

	# get data
	samples = sdr.read_samples(sampleCt)
	datums = []
	t = 0

	# 100 sample window; slide by 5 samples
	blocksize = int(bittime*sdr.sample_rate/10)
	stride =  int(blocksize/20)
	print blocksize, stride
	# sliding FFT	
	for datapiece in _window(samples, blocksize, stride):
		amplitudes = numpy.abs(numpy.fft.fft(datapiece))[0:stride/2]
		frequencies = numpy.fft.fftfreq(datapiece.shape[-1], d=1/sdr.sample_rate)[0:stride/2] + sdr.center_freq 
		index = numpy.argmax(numpy.abs(amplitudes))
		t += stride*1/sdr.sample_rate
		datums.append((t, amplitudes[index], frequencies[index]))

	# this is going to be approximately 50% of transmit power
	meanAmplitude = numpy.mean([d[1] for d in datums])

	# make a list of the frequency bins	
	freqs = numpy.array(list(set([d[2] for d in datums])))
	# find which one is closest to our broadcast frequency
	freq = freqs[numpy.argmin(numpy.abs(freqs - 144.64e6))]
	print freq, freqs, meanAmplitude
	# if amplitude is above 50% and peak frequency is in our bin	
	threshold = lambda d: (d[1] > meanAmplitude and d[2] == freq)

	# duration-encoded thresholded values
	durationEncoded = list(rle.runlength_enc([threshold(d) for d in datums]))
	print durationEncoded
	# find the start and end of the transmission
	minmax = [i for i, x in enumerate(durationEncoded) if x[0] > 2000]
	print minmax
	# trim off before/after samples
	durationEncoded = durationEncoded[minmax[0]+1:minmax[-1]]

	print durationEncoded

	# snap to ideal mean levels for high and low
	# take the "average" duration, assuming 50% zero one division
	meanDuration = numpy.mean([l for (l, s) in durationEncoded])
	# double length mark, happens with a change in symbols ie) 01 or 10
	high = numpy.mean([l for (l, s) in durationEncoded if l > meanDuration])
	# single length mark, happens with same symbols ie) 00 or 11
	low = numpy.mean([l for (l, s) in durationEncoded if l <= meanDuration])
	# make an array of possible mark durations, include zero to take out the trash
	levels = numpy.array([0, low, high])
	# snap the durations to the levels generated above
	processed = [(_snap(levels, l), s) for (l, s) in durationEncoded]
	print levels
	
	regularized = []

	# expand double-length marks to two marks
	for (l, s) in processed:
		if l == high:
			regularized.append(s)
			regularized.append(s)
		if l == low:
			regularized.append(s)


	def demod(data):
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
		return bits

	return demod(regularized)

if __name__ == "__main__":
	count = 0.0
	correct = 0.0
	while True:
		bits = sample(0.0005)
		if bits.tobytes() == "hello world":
			correct += 1.0
		count += 1.0
		with open("log", 'a') as f:
			f.write(bits.tobytes()+', ')
			f.write(str(correct/count))
			f.write('\n')
