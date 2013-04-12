from __future__ import division
import rtlsdr
import numpy
import matplotlib.pyplot as plt
import time
import scipy
from goertzel import goertzel

sdr = rtlsdr.RtlSdr()

sdr.sample_rate = 2.4e6
sdr.center_freq = 144e6
sdr.gain = 'auto'

sampleCt = 1 * sdr.sample_rate

samples = sdr.read_samples(int(sampleCt))
freqs, results = goertzel(samples, sdr.sample_rate, (0.640e6,0.645e6), (0.645e6,0.650e6))
print freqs, results
plt.plot(freqs, numpy.array(results)[:,2], 'o')  
plt.ylabel('Frequency')
plt.show()
