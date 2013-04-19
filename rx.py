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


def getData(duration):
	sdr = rtlsdr.RtlSdr()

	sdr.sample_rate = 2.4e6
	sdr.center_freq = 144.62e6
	sdr.gain = 'auto'

	sampleCt = 1024 * int((duration*sdr.sample_rate)/1000)

	samples = sdr.read_samples(sampleCt)
	return samples

snap = lambda levels, x: levels.flat[numpy.abs(levels - x).argmin()]

if __name__ == "__main__":

	samples = getData(0.2)
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

	thresholded = rle.runlength_enc([threshold(d) for d in datums])
	thresholded = [(snap(levels, l), s) for (l, s) in thresholded if l < 1000]

	plt.plot([x[0] for x in thresholded], 'k.')
	plt.figure()
	plt.plot([d[2] for d in datums], [d[1] for d in datums], 'k.')
	plt.show()


data = [(250, False), (500, True), (750, False), (250, True), (0, False), (500, True), (250, False), (500, True), (250, False), (500, True), (250, False), (500, True), (750, False), (750, True), (250, False), (500, True), (750, False), (250, True), (750, False), (250, True), (500, False), (250, True), (500, False), (250, True), (500, False), (250, True), (500, False), (750, True), (750, False), (250, True), (500, False), (250, True), (0, False), (750, True), (250, False), (500, True), (250, False), (500, True), (750, False), (750, True), (250, False), (500, True), (250, False), (500, True), (750, False), (250, True), (0, False), (500, True), (250, False), (500, True), (250, False), (500, True), (250, False), (500, True), (750, False), (750, True), (250, False), (500, True), (750, False), (250, True), (750, False), (750, True), (750, False), (250, True), (500, False), (750, True), (250, False), (500, True), (250, False), (500, True), (750, False), (250, True), (750, False), (250, True), (500, False), (750, True), (250, False), (500, True), (750, False), (750, True), (250, False), (500, True), (750, False), (250, True), (750, False), (250, True), (500, False), (750, True), (750, False), (250, True), (500, False), (250, True), (0, False), (500, True), (250, False), (500, True), (750, False), (250, True)]

data2 = [(250, False), (500, True), (250, False), (500, True), (750, False), (250, True), (0, False), (500, True), (250, False), (500, True), (750, False), (250, True), (500, False), (750, True), (750, False), (250, True), (500, False), (250, True), (0, False), (500, True), (250, False), (500, True), (250, False), (500, True), (750, False), (250, True), (750, False), (250, True), (500, False), (750, True), (250, False), (500, True), (750, False), (750, True), (250, False), (500, True), (750, False), (250, True), (750, False), (250, True), (500, False), (250, True), (0, False), (500, True), (750, False), (250, True), (500, False), (750, True), (250, False), (500, True), (750, False), (250, True)]

data3 = [(750, False), (250, True), (500, False), (750, True), (250, False), (500, True), (750, False), (250, True), (0, False), (500, True), (250, False), (500, True), (750, False), (250, True), (750, False), (250, True), (500, False), (750, True), (750, False), (250, True), (500, False), (250, True), (0, False), (500, True), (250, False), (500, True), (750, False), (250, True)]

data4 = [(750, False), (750, True), (250, False), (500, True), (250, False), (500, True), (750, False), (250, True), (0, False), (750, True), (250, False), (500, True), (250, False), (500, True), (250, False), (500, True), (750, False), (750, True), (250, False), (500, True), (750, False), (250, True), (750, False), (750, True), (750, False), (250, True), (500, False), (750, True), (250, False), (500, True), (250, False), (500, True), (750, False), (250, True), (750, False), (250, True), (500, False), (250, True), (0, False), (500, True), (250, False), (500, True), (750, False), (750, True), (250, False), (500, True), (750, False), (250, True), (500, False), (250, True), (500, False), (750, True), (750, False), (250, True), (500, False), (250, True), (0, False), (500, True), (250, False), (500, True), (750, False), (250, True)]

data5 = [(250, False), (500, True), (250, False), (500, True), (250, False), (500, True), (250, False), (500, True), (750, False), (750, True), (250, False), (500, True), (750, False), (250, True), (750, False), (250, True), (500, False), (250, True), (500, False), (250, True), (500, False), (250, True), (500, False), (750, True), (750, False), (250, True), (500, False), (250, True), (0, False), (750, True), (250, False), (500, True), (250, False), (500, True), (750, False), (750, True), (250, False), (500, True), (250, False), (500, True), (750, False), (250, True), (0, False), (750, True), (250, False), (500, True), (250, False), (500, True), (250, False), (500, True), (750, False), (750, True), (250, False), (500, True), (750, False), (250, True), (750, False), (250, True), (0, False), (500, True), (750, False), (250, True), (500, False), (750, True), (250, False), (500, True), (250, False), (500, True), (750, False), (250, True), (750, False), (250, True), (500, False), (750, True), (250, False), (500, True), (750, False), (250, True), (0, False), (500, True), (250, False), (500, True), (750, False), (250, True), (750, False), (250, True), (500, False), (250, True), (0, False), (500, True), (750, False), (250, True), (500, False), (750, True), (250, False), (500, True), (750, False), (250, True)]

data6 = [(250, True), (500, False), (250, True), (500, False), (250, True), (0, False), (500, True), (750, False), (250, True), (0, False), (500, True), (250, False), (500, True), (750, False), (250, True), (0, False), (750, True), (750, False), (750, True), (750, False), (250, True), (500, False), (250, True), (0, False), (500, True), (250, False), (500, True), (750, False), (250, True), (500, False), (250, True), (500, False), (250, True), (0, False), (500, True), (250, False), (500, True), (500, False)]

data7 = [(250, True), (500, False), (250, True), (500, False), (250, True), (0, False), (500, True), (750, False), (750, True), (250, False), (500, True), (750, False), (250, True), (0, False), (750, True), (750, False), (250, True), (0, False), (500, True), (750, False), (250, True), (500, False), (750, True), (250, False), (500, True), (750, False), (250, True), (750, False), (250, True), (500, False), (750, True), (250, False), (500, True), (750, False), (750, True), (250, False), (500, True), (750, False), (250, True), (750, False), (250, True), (500, False), (250, True), (0, False), (500, True), (250, False), (500, True), (750, False), (250, True), (0, False), (500, True), (250, False), (500, True), (750, False), (250, True), (0, False), (500, True), (250, False), (500, True), (250, False), (500, True), (250, False), (500, True), (750, False), (250, True), (0, False), (500, True), (250, False), (500, True), (750, False), (250, True), (750, False), (250, True), (500, False), (250, True), (500, False), (250, True), (500, False), (250, True), (500, False), (250, True), (0, False), (500, True), (750, False), (250, True), (500, False), (250, True), (0, False), (750, True), (250, False), (500, True), (250, False), (500, True), (750, False), (750, True), (250, False), (500, True), (250, False), (500, True), (750, False), (0, True)]

