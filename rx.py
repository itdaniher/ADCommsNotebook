from __future__ import division
import rtlsdr
import numpy
import matplotlib.pyplot as plt
import time
import scipy

sdr = rtlsdr.RtlSdr()

sdr.sample_rate = 2.4e6
sdr.center_freq = 144.62e6
sdr.gain = 'auto'

_chunk = lambda l, x: [l[i:i+x] for i in xrange(0, len(l), x)]

sampleCt = 1024 * int((0.2*sdr.sample_rate)/1000)

samples = sdr.read_samples(sampleCt)
datums = []
t = 0

def _window(sequence, winSize, step=1):
	# Pre-compute number of chunks to emit
	numOfChunks = int(((len(sequence)-winSize)/step)+1)
	# Do the work
	for i in range(0,numOfChunks*step,step):
		yield sequence[i:i+winSize]


blocksize = 100
stride = 10

for datapiece in _window(samples, blocksize, stride):
	amplitudes = numpy.abs(numpy.fft.fft(datapiece))[0:stride/2]
	frequencies = numpy.fft.fftfreq(datapiece.shape[-1], d=1/sdr.sample_rate)[0:stride/2] + sdr.center_freq 
	index = numpy.argmax(numpy.abs(amplitudes))
	t += stride*1/sdr.sample_rate
	datums.append((t, amplitudes[index], frequencies[index]))
	
mean = numpy.mean([d[1] for d in datums])
import rle

thresholded = list(rle.runlength_enc([d[1] > mean for d in datums]))
thresholded = [(l, s) for (l, s) in thresholded if l < 1000]

plt.plot(thresholded, 'k.')
plt.figure()
plt.plot([d[0] for d in datums], [d[2] for d in datums], 'k.')
plt.show()
