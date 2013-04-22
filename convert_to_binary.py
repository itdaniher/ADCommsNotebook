from __future__ import division
import numpy
import matplotlib.pyplot as plt
import time
import scipy

numpy.set_printoptions(threshold=numpy.nan)

sample_rate = 2.4e6
center_freq = 144.62e6
gain = 'auto'

sampleCt = 1 * sample_rate

def stft(x, fs, framesz, hop):
    framesamp = int(framesz*fs)
    hopsamp = int(hop*fs)
    w = scipy.hamming(framesamp)
    X = scipy.array([scipy.fft(w*x[i:i+framesamp]) 
                     for i in range(0, len(x)-framesamp, hopsamp)])
    return X

def load_data(npzfile):
	samples = numpy.load(npzfile)
	return samples["arr_0"]

def crop_data(X):
	return numpy.absolute(X.T[2:3,1550:3700])[0]

def get_binarystr(data):
	binstring = ''
	init_ts = data[0]
	ct = 0
	for ts in data:
		if init_ts > 100:
			if ts < 100:
				if ct > 5:
					binstring = binstring + "1"
				else:
					binstring = binstring + "0"
				ct = 0
			else:
				ct += 1
		init_ts = ts
	return binstring

def chunks(l, n):
    return [int(l[i:i+n],2) for i in range(0, len(l), n)]

def convert_to_ascii(l):
	return [chr(i) for i in l]

def plot_figure(X):
	plt.figure()
	plt.imshow(numpy.absolute(X.T[0:6,1550:3700]), origin='lower', aspect='auto', interpolation='nearest')
	plt.xlabel('Time')
	plt.ylabel('Frequency')
	plt.savefig("test.png")
	plt.show()

samples = load_data("helloWorldSamples.npz")
X = stft(samples, sample_rate, 0.0001, 0.0001)
data = crop_data(X)
binstring = get_binarystr(data)
chunked = chunks(binstring, 8)
print chunked
print convert_to_ascii(chunked)

plot_figure(X)
