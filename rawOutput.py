import subprocess
import numpy as np
import matplotlib.pyplot as plt
import datetime
import sys
from scipy.signal import find_peaks

loggers = [
    ("RHIC/Rf/LowLevel/CeCPoP/Gun/LLRF_Gun_Voltage_Fast_STRIP",             "VcavKvPickup"),
    ("RHIC/Rf/LowLevel/CeCPoP/Gun/Slot3_adc_phases",                        "adcCcPpc0.2b-llrf-cec1.3:vcavPhaseDegBArrayM"),
    ("RHIC/Rf/LowLevel/CeCPoP/Bunchers/LLRF_Bunchers_Voltage_Fast_STRIP",   "VcavKvPickup1"),
    ("RHIC/Rf/LowLevel/CeCPoP/Bunchers/Slot3_adc_phases",                   "adcCcPpc0.2b-llrf-cec2.3:vcavPhaseDegBArrayM"),
    ("RHIC/Rf/LowLevel/CeCPoP/5Cell/LLRF_704_Voltage_Fast_STRIP",           "VcavKvPickup"),
    ("RHIC/Rf/LowLevel/CeCPoP/5Cell/adc_phases",                            "adcCcPpc0.2b-llrf-cec4.3:vcavPhaseDegBArrayM")
]

startTime = int(datetime.datetime(2017, 6, 18, 3, 40, 0).timestamp())  #1497771600
duration = 10

if len(sys.argv) >= 2:
    try:
        startTime = int(sys.argv[1])
    except ValueError:
        print("invalid StartTime. Must be an integer")
        sys.exit(1)

if len(sys.argv) >= 3:
    try:
        duration = int(sys.argv[2])
    except ValueError:
        print("invalid duration. Must be an integer")
        sys.exit(1)

endTime = startTime + duration

for logger, dp in loggers:
    # print(logger)

    cmd = [f"exportLoggerData -logger {logger} -start {startTime} -stop {endTime} -timeform unix -arrayformat OneElementPerLine -cells {dp}"]
    dat = []

    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, text=True) as proc:
        for line in proc.stdout:
            if line.startswith('#'):
                continue
            fields = line.strip().split()
            dat.append(float(fields[1]))

    data_array = np.array(dat)

    fft_result = np.fft.fft(data_array)
    fft_magnitude = np.abs(fft_result)

    n = len(fft_magnitude)
    freqs = np.fft.fftfreq(n, d=float(duration)/float(n))

    positive_freqs = freqs > 0
    freqs = freqs[positive_freqs]
    fft_magnitude = fft_magnitude[positive_freqs]

    peaks, _ = find_peaks(fft_magnitude, height=np.max(fft_magnitude[5:]) * 0.2)

    if "KvPickup" in dp:
        analysis = f"jitter: {np.std(data_array)/np.mean(data_array)}%"
    else:
        analysis = f"jitter: {np.std(data_array)} rad"

    plt.figure(figsize=(12, 4))
    plt.plot(freqs, fft_magnitude)
    plt.grid(True)
    plt.xlim(0, np.max(freqs))
    plt.ylim(0, np.max(fft_magnitude[4:])*1.2)

    plt.title(f"{logger}/{dp}, {analysis}")

    for peak in peaks:
        freq = freqs[peak]
        mag = fft_magnitude[peak]
        plt.annotate(f"{freq:.2f} Hz", xy=(freq, mag), xytext=(freq, mag * 1.1),
                 textcoords="data", ha='center', fontsize=8,
                 arrowprops=dict(arrowstyle='->', lw=0.5))

    plt.tight_layout()

    safe_logger_name = logger.replace("/", "_").replace(":", "_")
    filename = f"fft_{safe_logger_name}.png"
    plt.savefig(filename, dpi=150)
    plt.close()
