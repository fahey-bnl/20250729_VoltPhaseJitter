import datetime
import os
import pandas as pd

#TODO user prompt for start and stop time
currentTime = datetime.datetime.now() #.strftime("%m/%d/%Y %H:%M")
fiveMinsDelta = datetime.timedelta(minutes=5)

timeStart = currentTime - fiveMinsDelta

loggers = [
    ("RHIC/Rf/LowLevel/CeCPoP/Gun/LLRF_Gun_Voltage_Fast_STRIP",             "VcavKvPickup"),
    ("RHIC/Rf/LowLevel/CeCPoP/Gun/LLRF_Gun_phase_Fast_STRIP",               "Gun_Pickup_Phase"),
    ("RHIC/Rf/LowLevel/CeCPoP/Bunchers/LLRF_Bunchers_Voltage_Fast_STRIP",   "VcavKvPickup1"),
    ("RHIC/Rf/LowLevel/CeCPoP/Bunchers/LLRF_Bunchers_phase_Fast_STRIP",     "Buncher_Pickup_Ph"),
    ("RHIC/Rf/LowLevel/CeCPoP/5Cell/LLRF_704_Voltage_Fast_STRIP",           "VcavKvPickup"),
    ("RHIC/Rf/LowLevel/CeCPoP/5Cell/LLRF_704_phase_Fast_STRIP",             "Linac_Pickup_Phase")
]

avgs = []

for log, dp in loggers:
    fullCommand = f'exportLoggerData -logger {log} -start "{timeStart.strftime("%m/%d/%y %H:%M")}" -stop "{currentTime.strftime("%m/%d/%y %H:%M")}" -timeform unix -arrayformat OneElementPerLine -expr "colcurravg=arrayavg(cell({dp}[.])) colcurrsigma=arraysigma(cell({dp}[.]))" -outfile test.dat'

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

df.to_csv("output.csv")
#df.to_excel("output.xlsx")