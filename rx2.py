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

sampleCt = 1 * sdr.sample_rate

def stft(x, fs, framesz, hop):
    framesamp = int(framesz*fs)
    hopsamp = int(hop*fs)
    w = scipy.hamming(framesamp)
    X = scipy.array([scipy.fft(w*x[i:i+framesamp]) 
                     for i in range(0, len(x)-framesamp, hopsamp)])
    return X

print sampleCt 
samples = sdr.read_samples(int(sampleCt))

X = stft(samples, sdr.sample_rate, 0.0001, 0.0001)
plt.figure()
plt.imshow(numpy.absolute(X.T), origin='lower', aspect='auto', interpolation='nearest')
plt.xlabel('Time')
plt.ylabel('Frequency')
plt.show()
