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

sampleCt = 1024 * int((1*sdr.sample_rate)/1000)

samples = sdr.read_samples(sampleCt)
datums = []
t = 0
for datapiece in _chunk(samples, 1024):
	amplitudes = numpy.abs(numpy.fft.fft(datapiece))[0:1024/2]
	frequencies = numpy.fft.fftfreq(datapiece.shape[-1], d=1/sdr.sample_rate)[0:1024/2] + sdr.center_freq 
	index = numpy.argmax(numpy.abs(amplitudes))
	t += 1024*1/sdr.sample_rate
	datums.append((amplitudes[index], frequencies[index], t))
	

plt.plot([d[2] for d in datums], [d[0] for d in datums], 'k.')
plt.show()
