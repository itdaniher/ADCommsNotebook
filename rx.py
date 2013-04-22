from __future__ import division
import rtlsdr
import numpy
import matplotlib.pyplot as plt
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
	duration = 0.35
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
		amplitudes = numpy.abs(numpy.fft.fft(datapiece))[0:stride/2]
		frequencies = numpy.fft.fftfreq(datapiece.shape[-1], d=1/sdr.sample_rate)[0:stride/2] + sdr.center_freq 
		index = numpy.argmax(numpy.abs(amplitudes))
		t += stride*1/sdr.sample_rate
		datums.append((t, amplitudes[index], frequencies[index]))
	
	mean = numpy.mean([d[1] for d in datums])
	
	freqs = numpy.array(list(set([d[2] for d in datums])))
	freq = freqs[numpy.argmin(numpy.abs(freqs - 144.64e6))]
	
	levels = numpy.array([0, 250, 500, 750])

	threshold = lambda d: (d[1] > mean and d[2] == freq)

	durationEncoded = list(rle.runlength_enc([threshold(d) for d in datums]))

	print durationEncoded
	
	processed = []

	for (l, s) in durationEncoded:
		if (100 < l < 1000):
			processed.append((snap(levels, l), s))
		if l > 2000:
			print numpy.argmin(numpy.abs(numpy.array([l for (l, s) in durationEncoded])-l)), l
	
	print processed
	#print len(_chunk([s for (l, s) in processed], 2))

	plt.plot([x[0] for x in processed], 'k.')
	plt.figure()
	plt.plot([d[2] for d in datums], [d[1] for d in datums], 'k.')
	plt.figure()
	plt.plot([d[0] for d in datums], [d[1] for d in datums], 'k.')
	plt.show()


