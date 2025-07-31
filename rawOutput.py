import subprocess
import numpy as np
import matplotlib.pyplot as plt

log = 'RHIC/Rf/LowLevel/CeCPoP/5Cell/LLRF_704_Voltage_Fast_STRIP'

duration = 10

startTime = 1497771600
endTime = startTime + duration

dp = 'VcavKvPickup'

cmd = [f"exportLoggerData -logger {log} -start {startTime} -stop {endTime} -timeform unix -arrayformat OneElementPerLine -cells {dp}"]

dat = []

with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True) as proc:
    for line in proc.stdout:
        if line.startswith('#'):
            continue
        fields = line.strip().split()
        # if len(fields) == 2:
        dat.append(float(fields[1]))

data_array = np.array(dat)

fft_result = np.fft.fft(data_array)
fft_magnitude = np.abs(fft_result)

n = len(fft_magnitude)
freqs = np.fft.fftfreq(n, d=float(duration)/float(n))

positive_freqs = freqs > 0

plt.plot(freqs[positive_freqs], fft_magnitude[positive_freqs])
# plt.loglog(freqs, fft_magnitude)
plt.show()
