import time
import os
import pandas as pd
import sys

#TODO user prompt for start and stop time

#unixTimestamp = int(time.time())

startTime = 1497771600
endTime = startTime + 5

loggers = [
    ("RHIC/Rf/LowLevel/CeCPoP/Gun/LLRF_Gun_Voltage_Fast_STRIP",             "VcavKvPickup"),
    ("RHIC/Rf/LowLevel/CeCPoP/Gun/Slot3_adc_phases",                        "adcCcPpc0.2b-llrf-cec1.3:vcavPhaseDegBArrayM"),
    ("RHIC/Rf/LowLevel/CeCPoP/Bunchers/LLRF_Bunchers_Voltage_Fast_STRIP",   "VcavKvPickup1"),
    ("RHIC/Rf/LowLevel/CeCPoP/Bunchers/Slot3_adc_phases",                   "adcCcPpc0.2b-llrf-cec2.3:vcavPhaseDegBArrayM"),
    ("RHIC/Rf/LowLevel/CeCPoP/5Cell/LLRF_704_Voltage_Fast_STRIP",           "VcavKvPickup"),
    ("RHIC/Rf/LowLevel/CeCPoP/5Cell/adc_phases",                            "adcCcPpc0.2b-llrf-cec4.3:vcavPhaseDegBArrayM")
]

avgs = []

for log, dp in loggers:
    fullCommand = f'exportLoggerData -logger {log} -start {startTime} -stop {endTime} -timeform unix -arrayformat OneElementPerLine -expr "colcurravg=arrayavg(cell({dp}[.])) colcurrsigma=arraysigma(cell({dp}[.]))" -outfile test.dat'

    os.system(fullCommand)
    timestamps = []
    averages = []
    sigmas = []

    with open('test.dat', 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            
            parts = line.strip().split()
            if len(parts) == 3:
                timestamps.append(float(parts[0]))
                averages.append(float(parts[1]))
                sigmas.append(float(parts[2]))

    avgs.append((sum(averages)/len(averages), sum(sigmas)/len(sigmas)))

df = pd.DataFrame(
    [[avgs[0][1]/avgs[0][0], avgs[1][1]],
     [avgs[2][1]/avgs[2][0], avgs[3][1]],
     [avgs[4][1]/avgs[4][0], avgs[5][1]]],
    index=["Gun","Buncher","Linac"],
    columns=["Amplitude","Phase"]
)

df.to_csv(f"output-{startTime}.csv")
#df.to_excel(f"output-{startTime}.xlsx")