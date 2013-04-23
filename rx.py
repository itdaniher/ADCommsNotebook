from __future__ import division
import rtlsdr
import numpy
import time
import scipy

import rle

_chunk = lambda l, x: [l[i:i+x] for i in xrange(0, len(l), x)]

def _window(sequence, winSize, step=1):
	# Pre-compute number of chunks to emit
	numOfChunks = int(((len(sequence)-winSize)/step)+1)
	# Do the work
	for i in range(0,numOfChunks*step,step):
		yield sequence[i:i+winSize]


snap = lambda levels, x: levels.flat[numpy.abs(levels - x).argmin()]

if __name__ == "__main__":
	duration = 0.1 + 0.002*8*11 + 0.1
	sdr = rtlsdr.RtlSdr()
	sdr.sample_rate = 2.4e6
	sdr.center_freq = 144.62e6
	sdr.gain = 'auto'
	sampleCt = 1024 * int((duration*sdr.sample_rate)/1000)


	import socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	s.connect(("10.33.91.11", 80))
	s.send('\xff')
	s.close()
	samples = sdr.read_samples(sampleCt)
	datums = []
	t = 0

	blocksize = 100
	stride = 10
	
	for datapiece in _window(samples, blocksize, stride):
	#if False:
		amplitudes = numpy.abs(numpy.fft.fft(datapiece))[0:stride/2]
		frequencies = numpy.fft.fftfreq(datapiece.shape[-1], d=1/sdr.sample_rate)[0:stride/2] + sdr.center_freq 
		index = numpy.argmax(numpy.abs(amplitudes))
		t += stride*1/sdr.sample_rate
		datums.append((t, amplitudes[index], frequencies[index]))
	numpy.save("datums", datums)
	#datums = numpy.load("datums.npy")
	mean = numpy.mean([d[1] for d in datums])
	
	freqs = numpy.array(list(set([d[2] for d in datums])))
	freq = freqs[numpy.argmin(numpy.abs(freqs - 144.64e6))]
	
	levels = numpy.array([0, 250, 500])

	threshold = lambda d: (d[1] > mean and d[2] == freq)

	durationEncoded = list(rle.runlength_enc([threshold(d) for d in datums]))

	print durationEncoded
	minmax = [i for i, x in enumerate(durationEncoded) if x[0] > 2000]

	print minmax

	processed = [(snap(levels, l), s) for (l, s) in durationEncoded[minmax[0]+1:minmax[-1]]]

	print processed
	expanded = []
	for (l, s) in processed:
		for i in range(int(l/250)):
			expanded.append((l,s))
	print expanded
	import bitarray
	regularized = [x[1] for x in expanded]
	def demod(regularized):
		bits = bitarray.bitarray(endian='little')
		for i, x in enumerate(_chunk(regularized, 2)):
			if x == [True, True]:
				regularized.insert(i*2, False)
				return demod(regularized)
			if x == [False, False]:
				regularized.insert(i*2, True)
				return demod(regularized)
			if x == [True, False]:
				bits.append(False)
			if x == [False, True]:
				bits.append(True)
		return bits
	bits = demod(regularized)
	print bits, map(lambda x: hex(ord(x)), bits.tobytes()), bits.tobytes()
