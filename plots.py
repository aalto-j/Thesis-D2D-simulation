import matplotlib.pyplot as plt
import pandas as pd
from dbConversion import *
import numpy as np


def readMonteCarloSimulation(filePath):
    #filePath = './allResultsS001SL10T1000.csv'
    #filePath = './allResultsSparepart.csv'
    filePath = './allResults10dbm.csv'
    f = pd.read_csv(filePath)
    #f50 = f[(f['n'] == 50)]
    #f10nC = f[(f['n'] == 10) & (f['harbour_bool'] == True)]

    #cityin = pd.read_csv('./allResultsSparepart.csv')
    #cityout = pd.read_csv('./allResultsSparepartOut.csv')

    #f = pd.concat([f50, f10nC])
    #f = pd.concat([f, cityin])
    #f = pd.concat([f, cityout])

    #print(f)
    newf = f.groupby(['n','power','f','basestation','indoor_ue','harbour_bool','load','ch'], as_index=False).mean()
    #newff = f.groupby(['n','power','f','basestation','indoor_ue','harbour_bool','load','ch']).first()
    #newff = newff.reset_index()
    print(newf)
    #print(newff)
    #newf['RFI_maxofmax'] = f.groupby(['n','power','f','basestation','indoor_ue','harbour_bool','load','ch'], sort=False)['RFI_max'].transform('max')
    #newf['RFI_minofmax'] = f.groupby(['n','power','f','basestation','indoor_ue','harbour_bool','load','ch'], sort=False)['RFI_max'].transform('min')
    
    
    #print(newf.sample())
    #print(f[(f['f'] == 700e6) & (f['indoor_ue'] == False) & (f['harbour_bool'] == False) & (f['basestation'] == 0) & (f['load'] == 0.1) & (f['power'] == 23)])
    return newf

def caseMat(filePath):
    f = readMonteCarloSimulation(filePath)
    f = pd.concat([f[(f['basestation'] == 2) & (f['indoor_ue'] == True)], f[(f['basestation'] == 1) & (f['indoor_ue'] == False)]])
    f = f.groupby(['n','power','f','basestation','indoor_ue','harbour_bool','ch'], as_index=False).mean()
    #f = f.sort_values(by=['f', 'RFI_max'])
    f["risk"] = f['time_max']*f['RFI_max']
    #f['color'] = 'g' if (f['RFI_max'] < dbm2mw(-105)) else 'y' if ((f['RFI_max'] < dbm2mw(-95)) and (f['RFI_Q90'] < dbm2mw(-105))) else 'r'
    
    conditions  = [(f['RFI_max'] < dbm2mw(np.ones(1)*(-105))[0]), ( (f['RFI_max'] < dbm2mw(np.ones(1)*(-95))[0]) & (f['RFI_Q90'] < dbm2mw(np.ones(1)*(-105))[0]) )]
    choices     = ['green', 'yellow']
    
    f['color'] = np.select(conditions, choices, default='red')
    #f = f.sort_values(by='risk', ascending=False)
    print(f)

    fig, ax = plt.subplots()

    labels = []
    mat = np.zeros((6, 7))

    r = f['risk'].to_numpy()
    r = r.reshape((6, 8), order='F')
    r = np.fliplr(r)

    ax.imshow(r, norm='log')
    plt.show()

    #for row in range(0, 6):
    #    for column in range(0, 7):
    #        mat[row][column] = r[f[len(labels)]]
    #print(r)



def throughputInterferenceLoadPlot(mode):
    f = readMonteCarloSimulation('./allResults.csv')
    
    dataA10 = f[(f["ch"] == mode) & (f["basestation"] == 1) & f["indoor_ue"]  & ((f["harbour_bool"]) == True) & (f["f"] == 35e8) & (f["n"] == 10)]
    dataC10 = f[(f["ch"] == 'C') & (f["basestation"] == 1) & f["indoor_ue"]  & ((f["harbour_bool"]) == True) & (f["f"] == 35e8) & (f["n"] == 10)]

    dataA50 = f[(f["ch"] == mode) & (f["basestation"] == 1) & f["indoor_ue"]  & ((f["harbour_bool"]) == True) & (f["f"] == 35e8) & (f["n"] == 50)]
    dataC50 = f[(f["ch"] == 'C') & (f["basestation"] == 1) & f["indoor_ue"]  & ((f["harbour_bool"]) == True) & (f["f"] == 35e8) & (f["n"] == 50)]

    fig, [[ax1, ax5], [ax3, ax7]] = plt.subplots(2, 2)
    ax1.set_title('Aloha, 10 devices')
    ax1.set_xlabel('Channel load (G)')
    ax1.set_ylabel('Interference (dBm)', color='g')
    ax1.tick_params(axis='y', labelcolor='g')
    ax1.plot(dataA10["load"], mw2dbm(dataA10["RFI_mean"]), 'g')
    ax1.grid(True)

    ax2 = ax1.twinx()
    ax2.set_ylabel('Throughput (S)', color='b')
    ax2.tick_params(axis='y', labelcolor='b')
    ax2.plot(dataA10["load"], dataA10["throughput"], 'b')
    
    ax3.set_title('CSMA, 10 devices')
    ax3.set_xlabel('Channel load (G)')
    ax3.set_ylabel('Interference (dBm)', color='g')
    ax3.tick_params(axis='y', labelcolor='g')
    ax3.plot(dataC10["load"], mw2dbm(dataC10["RFI_mean"]), 'g')
    ax3.grid(True)

    ax4 = ax3.twinx()
    ax4.set_ylabel('Throughput (S)', color='b')
    ax4.tick_params(axis='y', labelcolor='b')
    ax4.plot(dataC10["load"], dataC10["throughput"], 'b')
    
    ax5.set_title('Aloha, 50 devices')
    ax5.set_xlabel('Channel load (G)')
    ax5.set_ylabel('Interference (dBm)', color='g')
    ax5.tick_params(axis='y', labelcolor='g')
    ax5.plot(dataA50["load"], mw2dbm(dataA50["RFI_mean"]), 'g')
    ax5.grid(True)

    ax6 = ax5.twinx()
    ax6.set_ylabel('Throughput (S)', color='b')
    ax6.tick_params(axis='y', labelcolor='b')
    ax6.plot(dataA50["load"], dataA50["throughput"], 'b')
    
    ax7.set_title('CSMA, 50 devices')
    ax7.set_xlabel('Channel load (G)')
    ax7.set_ylabel('Interference (dBm)', color='g')
    ax7.tick_params(axis='y', labelcolor='g')
    ax7.plot(dataC50["load"], mw2dbm(dataC50["RFI_mean"]), 'g')
    ax7.grid(True)

    ax8 = ax7.twinx()
    ax8.set_ylabel('Throughput (S)', color='b')
    ax8.tick_params(axis='y', labelcolor='b')
    ax8.plot(dataC50["load"], dataC50["throughput"], 'b')

    plt.show()

    

def inOutComparisonPlot(figurePath, harbour_bool):
    f = readMonteCarloSimulation('./allResults.csv')
    fig, ax = plt.subplots(2, 2)

    lst = [35e8, 26e9]

    if harbour_bool:
        hcCase = 'Harbour_'
    else:
        hcCase = 'City_'

    labels = ['Indoor-Outdoor', 'Outdoor-Outdoor']

    for idx, freq in enumerate(lst):

        dev10in     = f[(f["ch"] == 'C') & (f["basestation"] == 1) & f["indoor_ue"]  & ((f["harbour_bool"]) == harbour_bool) & (f["f"] == freq) & (f["n"] == 10)]
        dev10out    = f[(f["ch"] == 'C') & (f["basestation"] == 1) & ~f["indoor_ue"] & ((f["harbour_bool"]) == harbour_bool) & (f["f"] == freq) & (f["n"] == 10)]
        dev50in     = f[(f["ch"] == 'C') & (f["basestation"] == 1) & f["indoor_ue"]  & ((f["harbour_bool"]) == harbour_bool) & (f["f"] == freq) & (f["n"] == 50)]
        dev50out    = f[(f["ch"] == 'C') & (f["basestation"] == 1) & ~f["indoor_ue"] & ((f["harbour_bool"]) == harbour_bool) & (f["f"] == freq) & (f["n"] == 50)]
        
        l1 = ax[idx, 0].plot(dev10in["load"], mw2dbm(dev10in["RFI_mean"]), label='Indoor-Outdoor')
        l2 = ax[idx, 0].plot(dev10out["load"], mw2dbm(dev10out["RFI_mean"]), label='Outdoor-Outdoor')
        ax[idx, 1].plot(dev50in["load"], mw2dbm(dev50in["RFI_mean"]), label='Indoor-Outdoor')
        ax[idx, 1].plot(dev50out["load"], mw2dbm(dev50out["RFI_mean"]), label='Outdoor-Outdoor')

        ax[idx, 0].set_ylabel("Signal power (dBm)")
        #ax[idx, 1].set_ylabel("Signal power (dBm)")
        ax[1, idx].set_xlabel("Channel load")
        ax[idx, 0].set_title(f"f={int(freq/1e6)} MHz, 10 devices")
        ax[idx, 1].set_title(f"f={int(freq/1e6)} MHz, 50 devices")

        ax[idx, 0].grid(True)
        ax[idx, 1].grid(True)

    plt.suptitle('Indoor-Outdoor - Outdoor-Outdoor comparison\nLocation_Harbour, Mode=CSMA')
    fig.legend([l1, l2], labels=labels,
    loc="lower center")
    fig.set_size_inches(12, 10)
    fig.set_dpi(100)
    fig.savefig(figurePath + hcCase + 'InOut-OutOut' + 'CSMA' + '_compare')
    plt.show()

def plotByFrequency(figurePath, indoor_bool, harbour_bool, mode):
    
    listOfFreq = ['700M/', '3.5G/', '6G/', '26G/', '60G/', '100G/']
    listOfFreqHz = [7e8, 35e8, 6e9, 26e9, 60e9, 10e10]

    if indoor_bool:
        ioCase = 'Indoor/'
    else:
        ioCase = 'Outdoor/'
    
    if harbour_bool:
        hcCase = 'Harbour/'
    else:
        hcCase = 'City/'

    f = readMonteCarloSimulation('./allResults.csv')
    fig, ax = plt.subplots()
    f0 = f[(f["ch"] == mode) & (f["basestation"] == 1) & ((f["indoor_ue"]) == indoor_bool) & ((f["harbour_bool"]) == harbour_bool) & (f["f"] == listOfFreqHz[0]) & (f['n'] == 10)]
    f1 = f[(f["ch"] == mode) & (f["basestation"] == 1) & ((f["indoor_ue"]) == indoor_bool) & ((f["harbour_bool"]) == harbour_bool) & (f["f"] == listOfFreqHz[1]) & (f['n'] == 10)]
    f2 = f[(f["ch"] == mode) & (f["basestation"] == 1) & ((f["indoor_ue"]) == indoor_bool) & ((f["harbour_bool"]) == harbour_bool) & (f["f"] == listOfFreqHz[2]) & (f['n'] == 10)]
    f3 = f[(f["ch"] == mode) & (f["basestation"] == 1) & ((f["indoor_ue"]) == indoor_bool) & ((f["harbour_bool"]) == harbour_bool) & (f["f"] == listOfFreqHz[3]) & (f['n'] == 10)]
    f4 = f[(f["ch"] == mode) & (f["basestation"] == 1) & ((f["indoor_ue"]) == indoor_bool) & ((f["harbour_bool"]) == harbour_bool) & (f["f"] == listOfFreqHz[4]) & (f['n'] == 10)]
    f5 = f[(f["ch"] == mode) & (f["basestation"] == 1) & ((f["indoor_ue"]) == indoor_bool) & ((f["harbour_bool"]) == harbour_bool) & (f["f"] == listOfFreqHz[5]) & (f['n'] == 10)]
    
    print(f0)

    #ax.plot(bs0["load"], mw2dbm(bs0["RFI_mean"]), 'g', label='BS 0/9')
    ax.plot(f0["load"], mw2dbm(f0["RFI_mean"]), label='700 Mhz')
    ax.plot(f1["load"], mw2dbm(f1["RFI_mean"]), label='3.5 GHz')
    ax.plot(f2["load"], mw2dbm(f2["RFI_mean"]), label='6 GHz')
    ax.plot(f3["load"], mw2dbm(f3["RFI_mean"]), label='26 GHz')
    ax.plot(f4["load"], mw2dbm(f4["RFI_mean"]), label='60 GHz')
    ax.plot(f5["load"], mw2dbm(f5["RFI_mean"]), label='100 GHz')



    #ax.plot(bs0["load"], mw2dbm(bs0["RFI_max"]), 'r', label='BS 0/9')

    ax.set_ylabel("Signal power (dBm)")
    ax.set_xlabel("Channel load")
    ax.set_title(f"Location={'Harbour' if f0.iat[0, 2] else 'City'}: {'Indoor-Outdoor' if f0.iat[0, 1] else 'Outdoor-Outdoor'}, Mode={'CSMA' if f0.iat[0, 12] == 'C' else 'Aloha'}")

    plt.grid()
    plt.legend(loc='lower right')

    fig.savefig(figurePath + hcCase + ioCase + f"{'CSMA' if mode == 'C' else 'Aloha'}" + '_fmat')

    plt.show()


def plotByFrequency50(figurePath, indoor_bool, harbour_bool, mode):
    
    listOfFreq = ['700M/', '3.5G/', '6G/', '26G/', '60G/', '100G/']
    listOfFreqHz = [7e8, 35e8, 6e9, 26e9, 60e9, 10e10]
    
    if indoor_bool:
        ioCase = 'Indoor/'
    else:
        ioCase = 'Outdoor/'
    
    if harbour_bool:
        hcCase = 'Harbour/'
    else:
        hcCase = 'City/'

    f = readMonteCarloSimulation('./allResultsS001SL10T1000.csv')
    fig, ax = plt.subplots()
    #f0 = f[(f["ch"] == mode) & (f["basestation"] == 1) & ((f["indoor_ue"]) == indoor_bool) & ((f["harbour_bool"]) == harbour_bool) & (f["f"] == listOfFreqHz[0])]
    f1 = f[(f["ch"] == mode) & (f["basestation"] == 1) & ((f["indoor_ue"]) == indoor_bool) & ((f["harbour_bool"]) == harbour_bool) & (f["f"] == listOfFreqHz[1]) & (f['n'] == 50)]
    f2 = f[(f["ch"] == mode) & (f["basestation"] == 1) & ((f["indoor_ue"]) == indoor_bool) & ((f["harbour_bool"]) == harbour_bool) & (f["f"] == listOfFreqHz[2]) & (f['n'] == 50)]
    f3 = f[(f["ch"] == mode) & (f["basestation"] == 1) & ((f["indoor_ue"]) == indoor_bool) & ((f["harbour_bool"]) == harbour_bool) & (f["f"] == listOfFreqHz[3]) & (f['n'] == 50)]
    f4 = f[(f["ch"] == mode) & (f["basestation"] == 1) & ((f["indoor_ue"]) == indoor_bool) & ((f["harbour_bool"]) == harbour_bool) & (f["f"] == listOfFreqHz[4]) & (f['n'] == 50)]
    #f5 = f[(f["ch"] == mode) & (f["basestation"] == 1) & ((f["indoor_ue"]) == indoor_bool) & ((f["harbour_bool"]) == harbour_bool) & (f["f"] == listOfFreqHz[5])]
    
    print(f1)

    #ax.plot(bs0["load"], mw2dbm(bs0["RFI_mean"]), 'g', label='BS 0/9')
    #ax.plot(f0["load"], mw2dbm(f0["RFI_mean"]), label='700 Mhz')
    ax.plot(f1["load"], mw2dbm(f1["RFI_mean"]), label='3.5 GHz')
    ax.plot(f2["load"], mw2dbm(f2["RFI_mean"]), label='6 GHz')
    ax.plot(f3["load"], mw2dbm(f3["RFI_mean"]), label='26 GHz')
    ax.plot(f4["load"], mw2dbm(f4["RFI_mean"]), label='60 GHz')
    #ax.plot(f5["load"], mw2dbm(f5["RFI_mean"]), label='100 GHz')



    #ax.plot(bs0["load"], mw2dbm(bs0["RFI_max"]), 'r', label='BS 0/9')

    ax.set_ylabel("Signal power (dBm)")
    ax.set_xlabel("Channel load")
    ax.set_title(f"Location={'Harbour' if f1.iat[0, 2] else 'City'}: {'Indoor-Outdoor' if f1.iat[0, 1] else 'Outdoor-Outdoor'}, Mode={'CSMA' if f1.iat[0, 12] == 'C' else 'Aloha'}")

    plt.grid()
    plt.legend(loc='lower right')

    #fig.savefig(figurePath + hcCase + ioCase + f"{'CSMA' if mode == 'C' else 'Aloha'}" + '_fmat')

    plt.show()

def frequencyMatPlot(figurePath, indoor_bool, harbour_bool, mode):
    
    listOfFreq = ['700M/', '3.5G/', '6G/', '26G/', '60G/', '100G/']
    listOfFreqHz = [7e8, 35e8, 6e9, 26e9, 60e9, 10e10]
    #listOfFreq = ['3.5G/', '26G/']
    #listOfFreqHz = [35e8, 26e9]

    #freqDir = listOfFreq[frequencyChoise]
    
    labType = ['Interference mean', 'Interference 90th quantile', 'Interference maximum']

    labBs = ['BS1 - Hietalahdenranta', 'BS2 - Tyynenmerenkatu', 'BS3 - Matalasalmenkuja'] if harbour_bool \
    else ['BS4 - Uudenmaankatu', 'BS5 - Fredrikinkatu', 'BS6 - Yrjönkatu']

    if indoor_bool:
        ioCase = 'InOut_'
    else:
        ioCase = 'OutOut_'
    
    if harbour_bool:
        hcCase = 'Harbour_'
    else:
        hcCase = 'City_'

    #f = pd.read_csv('./allResults.csv')
    f = readMonteCarloSimulation('./allResults.csv')
    fig, ax = plt.subplots(3, 2)
    ax = ax.flat


    for idx, freq in enumerate(listOfFreqHz):

        bs0 = f[(f["ch"] == mode) & (f["basestation"] == 0) & ((f["indoor_ue"]) == indoor_bool) & ((f["harbour_bool"]) == harbour_bool) & (f["f"] == freq) & (f["n"] == 10)]
        bs1 = f[(f["ch"] == mode) & (f["basestation"] == 1) & ((f["indoor_ue"]) == indoor_bool) & ((f["harbour_bool"]) == harbour_bool) & (f["f"] == freq) & (f["n"] == 10)]
        bs2 = f[(f["ch"] == mode) & (f["basestation"] == 2) & ((f["indoor_ue"]) == indoor_bool) & ((f["harbour_bool"]) == harbour_bool) & (f["f"] == freq) & (f["n"] == 10)]

        #print(bs0)

        #if any(x > -174 for x in mw2dbm(bs0["RFI_mean"])):
        l1 = ax[idx].plot(bs0["load"], mw2dbm(bs0["RFI_mean"]), 'g')[0]#, label='BS1a')
        l2 = ax[idx].plot(bs0["load"], mw2dbm(bs0["RFI_Q90"]), 'y')[0]#, label='BS1q')
        l3 = ax[idx].plot(bs0["load"], mw2dbm(bs0["RFI_max"]), 'r')[0]#, label='BS1m')
        #if any(x > -174 for x in mw2dbm(bs1["RFI_mean"])):
        l4 = ax[idx].plot(bs1["load"], mw2dbm(bs1["RFI_mean"]), 'g--')[0]#, label='BS2a')
        l5 = ax[idx].plot(bs1["load"], mw2dbm(bs1["RFI_Q90"]), 'y--')[0]#, label='BS2q')
        l6 = ax[idx].plot(bs1["load"], mw2dbm(bs1["RFI_max"]), 'r--')[0]#, label='BS2m')
        #if any(x > -174 for x in mw2dbm(bs2["RFI_mean"])):
        l7 = ax[idx].plot(bs2["load"], mw2dbm(bs2["RFI_mean"]), color='g', linestyle='dashdot')[0]#, label='BS3a')
        l8 = ax[idx].plot(bs2["load"], mw2dbm(bs2["RFI_Q90"]), color='y', linestyle='dashdot')[0]#, label='BS3q')
        l9 = ax[idx].plot(bs2["load"], mw2dbm(bs2["RFI_max"]), color='r', linestyle='dashdot')[0]#, label='BS3m')

        #ax[idx].fill_between(bs0['load'], mw2dbm(bs0['RFI_maxofmax']), mw2dbm(bs0['RFI_minofmax']), alpha=0.2)


        ax[idx].set_ylabel("Signal power (dBm)")
        ax[idx].set_xlabel("Channel load (G)")
        ax[idx].set_title(f"f={int(listOfFreqHz[idx]/1e6)} MHz")
        #ax[idx].set_ylim(-174, -30)
        ax[idx].legend([l1, l4, l7], labBs, loc="lower right")

        ax[idx].grid(True)



    fig.suptitle(f"Location={'Harbour' if harbour_bool else 'City'}, Case={'Indoor-Outdoor' if indoor_bool else 'Outdoor-Outdoor'}, Mode={'CSMA' if (mode == 'C') else 'Aloha'}, Devices=10")
    #plt.legend(loc='lower right')
    #plt.tight_layout()

    fig.legend([l1, l2, l3], labType, loc="lower center", ncols=3)
    
    fig.set_size_inches(12, 15) #12, 15
    fig.set_dpi(75)
    #fig.savefig(figurePath + hcCase + ioCase + f"{'CSMA' if mode == 'C' else 'Aloha'}" + '_fmat')
    plt.show()

def frequencyMatPlot50(figurePath, indoor_bool, harbour_bool, mode):
    
    listOfFreq = ['3.5G/', '26G/']
    listOfFreqHz = [35e8, 6e9, 26e9, 60e9]

    #freqDir = listOfFreq[frequencyChoise]
    
    labType = ['Interference mean', 'Interference 90th quantile', 'Interference maximum']

    labBs = ['BS1 - Hietalahdenranta', 'BS2 - Tyynenmerenkatu', 'BS3 - Matalasalmenkuja'] if harbour_bool \
    else ['BS4 - Uudenmaankatu', 'BS5 - Fredrikinkatu', 'BS6 - Yrjönkatu']

    if indoor_bool:
        ioCase = 'InOut_'
    else:
        ioCase = 'OutOut_'
    
    if harbour_bool:
        hcCase = 'Harbour_'
    else:
        hcCase = 'City_'

    #f = pd.read_csv('./allResults.csv')
    f = readMonteCarloSimulation('./allResults.csv')
    fig, ax = plt.subplots(2, 2)
    ax = ax.flat


    for idx, freq in enumerate(listOfFreqHz):

        bs0 = f[(f["ch"] == mode) & (f["basestation"] == 0) & ((f["indoor_ue"]) == indoor_bool) & ((f["harbour_bool"]) == harbour_bool) & (f["f"] == freq) & (f["n"] == 50)]
        bs1 = f[(f["ch"] == mode) & (f["basestation"] == 1) & ((f["indoor_ue"]) == indoor_bool) & ((f["harbour_bool"]) == harbour_bool) & (f["f"] == freq) & (f["n"] == 50)]
        bs2 = f[(f["ch"] == mode) & (f["basestation"] == 2) & ((f["indoor_ue"]) == indoor_bool) & ((f["harbour_bool"]) == harbour_bool) & (f["f"] == freq) & (f["n"] == 50)]

        print(bs0)

        #if any(x > -174 for x in mw2dbm(bs0["RFI_mean"])):
        l1 = ax[idx].plot(bs0["load"], mw2dbm(bs0["RFI_mean"]), 'g')[0]#, label='BS1a')
        l2 = ax[idx].plot(bs0["load"], mw2dbm(bs0["RFI_Q90"]), 'y')[0]#, label='BS1q')
        l3 = ax[idx].plot(bs0["load"], mw2dbm(bs0["RFI_max"]), 'r')[0]#, label='BS1m')
        #if any(x > -174 for x in mw2dbm(bs1["RFI_mean"])):
        l4 = ax[idx].plot(bs1["load"], mw2dbm(bs1["RFI_mean"]), 'g--')[0]#, label='BS2a')
        l5 = ax[idx].plot(bs1["load"], mw2dbm(bs1["RFI_Q90"]), 'y--')[0]#, label='BS2q')
        l6 = ax[idx].plot(bs1["load"], mw2dbm(bs1["RFI_max"]), 'r--')[0]#, label='BS2m')
        #if any(x > -174 for x in mw2dbm(bs2["RFI_mean"])):
        l7 = ax[idx].plot(bs2["load"], mw2dbm(bs2["RFI_mean"]), color='g', linestyle='dashdot')[0]#, label='BS3a')
        l8 = ax[idx].plot(bs2["load"], mw2dbm(bs2["RFI_Q90"]), color='y', linestyle='dashdot')[0]#, label='BS3q')
        l9 = ax[idx].plot(bs2["load"], mw2dbm(bs2["RFI_max"]), color='r', linestyle='dashdot')[0]#, label='BS3m')

        ax[idx].set_ylabel("Signal power (dBm)")
        ax[idx].set_xlabel("Channel load (G)")
        ax[idx].set_title(f"f={int(listOfFreqHz[idx]/1e6)} MHz")
        #ax[idx].set_ylim(-174, -30)
        ax[idx].legend([l1, l4, l7], labBs, loc="lower right")

        ax[idx].grid(True)



    fig.suptitle(f"Location={'Harbour' if harbour_bool else 'City'}, Case={'Indoor-Outdoor' if indoor_bool else 'Outdoor-Outdoor'}, Mode={'CSMA' if (mode == 'C') else 'Aloha'}, Devices=50")
    #plt.legend(loc='lower right')
    #plt.tight_layout()

    fig.legend([l1, l2, l3], labType, loc="lower center", ncols=3)
    
    fig.set_size_inches(12, 12)
    fig.set_dpi(75)
    fig.savefig(figurePath + hcCase + ioCase + f"{'CSMA' if mode == 'C' else 'Aloha'}" + '_fmat50')
    plt.show()




def plotByBasestation(figurePath, frequencyChoise, indoor_bool, harbour_bool, mode):
    
    listOfFreq = ['700M/', '3.5G/', '6G/', '26G/', '60G/', '100G/']
    listOfFreqHz = [7e8, 35e8, 6e9, 26e9, 60e9, 10e10]

    freqDir = listOfFreq[frequencyChoise]
    
    if indoor_bool:
        ioCase = 'Indoor/'
    else:
        ioCase = 'Outdoor/'
    
    if harbour_bool:
        hcCase = 'Harbour/'
    else:
        hcCase = 'City/'

    f = readMonteCarloSimulation('./allResults.csv')
    fig, ax = plt.subplots()
    bs0 = f[(f["ch"] == mode) & (f["basestation"] == 0) & ((f["indoor_ue"]) == indoor_bool) & ((f["harbour_bool"]) == harbour_bool) & (f["f"] == listOfFreqHz[frequencyChoise])]
    bs1 = f[(f["ch"] == mode) & (f["basestation"] == 1) & ((f["indoor_ue"]) == indoor_bool) & ((f["harbour_bool"]) == harbour_bool) & (f["f"] == listOfFreqHz[frequencyChoise])]
    bs2 = f[(f["ch"] == mode) & (f["basestation"] == 2) & ((f["indoor_ue"]) == indoor_bool) & ((f["harbour_bool"]) == harbour_bool) & (f["f"] == listOfFreqHz[frequencyChoise])]
    ax.plot(bs0["load"], mw2dbm(bs0["RFI_mean"]), 'g', label='BS 0/9')
    ax.plot(bs0["load"], mw2dbm(bs0["RFI_Q90"]), 'y', label='BS 0/9')
    ax.plot(bs0["load"], mw2dbm(bs0["RFI_max"]), 'r', label='BS 0/9')

    ax.plot(bs1["load"], mw2dbm(bs1["RFI_mean"]), 'g--', label='BS 1/10')
    ax.plot(bs1["load"], mw2dbm(bs1["RFI_Q90"]), 'y--', label='BS 1/10')
    ax.plot(bs1["load"], mw2dbm(bs1["RFI_max"]), 'r--', label='BS 1/10')

    ax.plot(bs2["load"], mw2dbm(bs2["RFI_mean"]), color='green', linestyle='dashdot', label='BS 3/27')
    ax.plot(bs2["load"], mw2dbm(bs2["RFI_Q90"]), color='yellow', linestyle='dashdot', label='BS 3/27')
    ax.plot(bs2["load"], mw2dbm(bs2["RFI_max"]), color='red', linestyle='dashdot', label='BS 3/27')

    ax.set_ylabel("Signal power (dBm)")
    ax.set_xlabel("Channel load")
    ax.set_title(f"f={int(bs0.iat[0, 0]/1e6)} MHz, Location={'Harbour' if bs0.iat[0, 2] else 'City'}: {'Indoor-Outdoor' if bs0.iat[0, 1] else 'Outdoor-Outdoor'}, Mode={'CSMA' if bs0.iat[0, 12] == 'C' else 'Aloha'}")
    
    
    plt.grid()
    plt.legend(loc='lower right')
    fig.savefig(figurePath + ioCase + freqDir + hcCase + 'interference')
    plt.show()


def delayPlot(figurePath):

    f = readMonteCarloSimulation('./allResultsLong.csv')
    fig, ax = plt.subplots(2, 2)
    ax = ax.flat

    freq = 26e9
    dev = 10

    csmaDelayInOutH      = f[(f["ch"] == 'C') & (f["basestation"] == 0) & ((f["indoor_ue"]) == True) & ((f["harbour_bool"]) == True) & (f["f"] == freq) & (f['n'] == dev)]
    csmaDelayOutOutH     = f[(f["ch"] == 'C') & (f["basestation"] == 0) & ((f["indoor_ue"]) == False) & ((f["harbour_bool"]) == True) & (f["f"] == freq) & (f['n'] == dev)]
    alohaDelayInOutH    = f[(f["ch"] == 'A') & (f["basestation"] == 0) & ((f["indoor_ue"]) == True) & ((f["harbour_bool"]) == True) & (f["f"] == freq) & (f['n'] == dev)]
    alohaDelayOutOutH     = f[(f["ch"] == 'A') & (f["basestation"] == 0) & ((f["indoor_ue"]) == False) & ((f["harbour_bool"]) == True) & (f["f"] == freq) & (f['n'] == dev)]

    csmaDelayInOutC      = f[(f["ch"] == 'C') & (f["basestation"] == 0) & ((f["indoor_ue"]) == True) & ((f["harbour_bool"]) == False) & (f["f"] == freq) & (f['n'] == dev)]
    csmaDelayOutOutC     = f[(f["ch"] == 'C') & (f["basestation"] == 0) & ((f["indoor_ue"]) == False) & ((f["harbour_bool"]) == False) & (f["f"] == freq) & (f['n'] == dev)]
    alohaDelayInOutC    = f[(f["ch"] == 'A') & (f["basestation"] == 0) & ((f["indoor_ue"]) == True) & ((f["harbour_bool"]) == False) & (f["f"] == freq) & (f['n'] == dev)]
    alohaDelayOutOutC     = f[(f["ch"] == 'A') & (f["basestation"] == 0) & ((f["indoor_ue"]) == False) & ((f["harbour_bool"]) == False) & (f["f"] == freq) & (f['n'] == dev)]

    l1 = ax[0].plot(alohaDelayInOutH["load"],     alohaDelayInOutH["delay"],   'b')
    l2 = ax[0].plot(alohaDelayOutOutH["load"],    alohaDelayOutOutH["delay"],  'g')
    ax[1].plot(alohaDelayInOutC["load"],     alohaDelayInOutC["delay"],   'b')
    ax[1].plot(alohaDelayOutOutC["load"],    alohaDelayOutOutC["delay"],  'g')
    
    ax[2].plot(csmaDelayInOutH["load"],      csmaDelayInOutH["delay"]/100,   'b')
    ax[2].plot(csmaDelayOutOutH["load"],     csmaDelayOutOutH["delay"]/100,   'g')
    ax[3].plot(csmaDelayInOutC["load"],      csmaDelayInOutC["delay"]/100,   'b')
    ax[3].plot(csmaDelayOutOutC["load"],     csmaDelayOutOutC["delay"]/100,   'g')

    ax[0].set_title('Delay Aloha channel, Harbour 26 GHz')
    ax[1].set_title('Delay Aloha channel, City 26 GHz')
    ax[2].set_title('Delay CSMA channel, Harbour 26 GHz')
    ax[3].set_title('Delay CSMA channel, City 26 GHz')

    ax[0].set_xlabel("Channel load (G)")
    ax[1].set_xlabel("Channel load (G)")
    ax[2].set_xlabel("Channel load (G)")
    ax[3].set_xlabel("Channel load (G)")
    
    ax[0].set_ylabel("Avg. delay (t)")
    ax[1].set_ylabel("Avg. delay (t)")
    ax[2].set_ylabel("Avg. delay (t)")
    ax[3].set_ylabel("Avg. delay (t)")
    
    ax[0].grid(True)
    ax[1].grid(True)
    ax[2].grid(True)
    ax[3].grid(True)

    labels = ['Indoor-Outdoor', 'Outdoor-Outdoor']

    fig.legend([l1, l2], labels=labels,
    loc="lower center", ncol=2)
    fig.savefig(figurePath + 'delayplot')
    plt.show()

def throughputPlot(figurePath, indoor_bool, harbour_bool, mode):
    f = readMonteCarloSimulation('./allResults.csv')

    tpA = f[(f["ch"] == 'A') & (f["basestation"] == 0) & ((f["indoor_ue"]) == indoor_bool) & ((f["harbour_bool"]) == True) & (f["f"] == 3.5e9) & (f["n"] == 50)]
    tpC = f[(f["ch"] == 'C') & (f["basestation"] == 0) & ((f["indoor_ue"]) == indoor_bool) & ((f["harbour_bool"]) == True) & (f["f"] == 3.5e9) & (f["n"] == 50)]

    fig, ax = plt.subplots(2, 1)

    l1 = ax[0].plot(tpA["load"], tpA["throughput"])
    l2 = ax[1].plot(tpC["load"], tpC["throughput"])

    plt.show()

    pass

def timeAboveLimit():
    f = readMonteCarloSimulation('./allResults.csv')
    fcity = readMonteCarloSimulation('./allResultsSparepart.csv')
    fig, ax = plt.subplots()

    data = f[(f["ch"] == 'C') & (f["basestation"] == 0) & ((f["indoor_ue"]) == True) & ((f["harbour_bool"]) == True) & (f["f"] == 6e9)]

    ax.plot(data["load"], data["time_Q90"], label='90th quantile')
    ax.plot(data["load"], data["time_Q95"], label='95th quantile')
    ax.plot(data["load"], data["time_max"], label='Maximum')

    ax.set_ylim(0.0, 0.2)

    print(data["time_max"])

    plt.grid()
    plt.legend()
    plt.show()

def aboveLimitMat():
    f = readMonteCarloSimulation('./allResults.csv')
    fig, ax = plt.subplots(8, 6, sharex=True, sharey=True)
    #ax = ax.flat
    
    for idx, freq in enumerate([7e8, 35e8, 6e9, 26e9, 60e9, 10e10]):
        a = 0
        ax[a, idx].set_title(f"f={int(freq/1e6)} MHz")
        for chCase in [True, False]:
            bs = 1 if chCase else 2
            for mode in ['A', 'C']:
                for inOut in [True, False]:
                    if (idx == 0):
                        ax[a, idx].set_ylabel(f"{'Harbour' if chCase else 'City'}\n{'Aloha' if (mode == 'A') else 'CSMA'}\n{'In-Out' if inOut else 'Out-Out'}")
                    
                    data = f[(f["ch"] == mode) & (f["basestation"] == bs) & ((f["indoor_ue"]) == inOut) & ((f["harbour_bool"]) == chCase) & (f["f"] == freq) & (f['n'] == 10)]
                    ax[a, idx].plot(data["load"], data["time_Q90"], label='90th quantile')
                    ax[a, idx].plot(data["load"], data["time_Q95"], label='95th quantile')
                    ax[a, idx].plot(data["load"], data["time_max"], label='Maximum')
                
                    ax[a, idx].set_ylim(0.0, 0.2)
                    ax[a, idx].grid(True)
                    a += 1
     
    line, label = ax[a-1, idx].get_legend_handles_labels()
    fig.legend(line, label, loc="lower center", ncol=3)
    #fig.suptitle('Time of the simulation spent over limit')
    fig.text(0.5, 0.06, 'Channel load (G)', ha='center')
    fig.text(0.02, 0.5, 'Limit exeeded (1/T)', va='center', rotation='vertical')
    fig.set_size_inches(15, 15)
    fig.set_dpi(100)

    #print(data["time_max"])

    plt.show()

def main():

    figurePath = 'figures/'

    for frequencyChoise in range(0, 6):
        for indoor in [False]:#[True, False]:
            for harbour in [False]:#[True, False]:
                pass
                plotByBasestation(figurePath, frequencyChoise, indoor, harbour, 'C')

    frequencyMatPlot(figurePath, True, True, 'C') # OK
    frequencyMatPlot(figurePath, True, False, 'C') # OK
    frequencyMatPlot(figurePath, False, True, 'C') # OK
    frequencyMatPlot(figurePath, False, False, 'C') # OK
    frequencyMatPlot(figurePath, True, True, 'A') # OK
    frequencyMatPlot(figurePath, True, False, 'A') # OK
    frequencyMatPlot(figurePath, False, True, 'A') # OK
    frequencyMatPlot(figurePath, False, False, 'A') # OK

    frequencyMatPlot50(figurePath, True, True, 'A')
    frequencyMatPlot50(figurePath, False, True, 'A')
    frequencyMatPlot50(figurePath, True, True, 'C')
    frequencyMatPlot50(figurePath, False, True, 'C')

    delayPlot(figurePath) # OK
    aboveLimitMat() # OK
    
    #plotByFrequency(figurePath, True, True, 'C')
    #plotByFrequency(figurePath, True, False, 'C')
    #plotByFrequency(figurePath, False, True, 'C')
    #plotByFrequency(figurePath, False, False, 'C')

    throughputPlot(figurePath, True, True, 'C')

throughputInterferenceLoadPlot('A') #OK
#timeAboveLimit()
main()
#caseMat('./allResultsg.csv')
#readMonteCarloSimulation('./allResults.csv')
#throughputPlot('figures/', True, True, 'C')
#throughputPlot('figures/', False, False, 'C')
#inOutComparisonPlot('figures/', True)