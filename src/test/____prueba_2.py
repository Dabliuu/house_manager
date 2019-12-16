
import matplotlib.pyplot as plt
import numpy as np
from scipy.fftpack import fft

# Data for plotting

fmuestreo = 1000
periodo = 1/fmuestreo
fseñal = 60
A = 1
chunk = 100


n = np.arange(chunk) # num de muestras (arange is for creating vectors with constant increment)
# x = np.linspace(2,50,100) # thi one is used when the required amount of points is known

# y axis for both axis
s = A * np.sin(2 * np.pi * fseñal * (n/fmuestreo) ) + 5
fs =  np.abs( np.fft.rfft(s))/100 # normalize it dividing by 100 # use fft for the reflected spectrum in 0

# x axes for both graphs
t = periodo * n
f = np.fft.rfftfreq(len(n)) * fmuestreo # same here, use fft for the reflected spectrum in 0

fig, (ax0, ax1) = plt.subplots(nrows=2)

# for thefirst graph:
ax0.plot(n/fmuestreo, s, 'o-')
ax0.set(xlabel='time (s)', ylabel='voltage (mV)',
       title='Signal with Furier transform')


# for thefirst graph:
ax1.plot(f, fs, '.-')
ax1.set(xlabel='frequency (hz)', ylabel='Normalized value')

plt.show()

fig.savefig("test.png")

"""
# for simple plotting:

fig, ax = plt.subplots()
ax.plot(x, y,)
plt.show()

"""