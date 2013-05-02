import timeit

print "time to convolve 4096 floats with 1024 floats (fft)", \
timeit.timeit(stmt="signal.fftconvolve(signal.np.random.random(2**12), signal.np.random.random(2**10))", setup="from scipy import signal", number=1000)/1000

print "time to convolve 4096 floats with 1024 floats (naive)", \
timeit.timeit(stmt="signal.np.convolve(signal.np.random.random(2**12), signal.np.random.random(2**10))", setup="from scipy import signal", number=1000)/1000

print "time to convolve 4095 floats with 1023 floats (fft)", \
timeit.timeit(stmt="signal.fftconvolve(signal.np.random.random(2**12-1), signal.np.random.random(2**10-1))", setup="from scipy import signal", number=1000)/1000

print "time to convolve 4095 floats with 1023 floats (naive)", \
timeit.timeit(stmt="signal.np.convolve(signal.np.random.random(2**12-1), signal.np.random.random(2**10-1))", setup="from scipy import signal", number=1000)/1000
