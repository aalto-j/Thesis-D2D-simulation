import matplotlib.pyplot as plt
import pandas as pd
from dbConversion import *
import numpy as np

def rating_color(v):
    if v < -114: color = "00A64F"
    elif v > -90 : color = "#ED1B23"
    else: color = "#FFF200"
    return f"color: {color};"


def readMonteCarloSimulation():
    #filePath = './allResultsS001SL10T1000.csv'
    #filePath = './allResults100.csv'
    filePath = './allResultsS001SL100T1000.csv'
    f = pd.read_csv(filePath)
    f50 = f[(f['n'] == 50)]
    f10nC = f[(f['n'] == 10) & (f['harbour_bool'] == True)]

    cityin = pd.read_csv('./allResultsSparepart.csv')
    #cityout = pd.read_csv('./allResultsSparepartOut.csv')

    f = pd.concat([f50, f10nC])
    f = pd.concat([f, cityin])
    print(f)
    f['harbour_bool'].mask((f['harbour_bool'] == True), 'Harbour', inplace=True)
    f['harbour_bool'].mask((f['harbour_bool'] == False), 'City', inplace=True)
    f['indoor_ue'].mask((f['indoor_ue'] == True), 'Indoor', inplace=True)
    f['indoor_ue'].mask((f['indoor_ue'] == False), 'Outdoor', inplace=True)
    f["RFI_db"] = mw2dbm(f['RFI_max'])
    f['f'] = f['f'].div(1e6).astype('int')
    newf = f.groupby(['n','power','f','indoor_ue','harbour_bool','ch'], as_index=False).max()
    newf = newf[['n','f', 'indoor_ue', 'harbour_bool', 'ch', "RFI_db"]]
    newf.columns = ["Devices", 'Frequency', 'UE Location', 'Scenario', 'Mode', 'Maximum interference (dbm)']
    newf = newf.groupby(['Devices', 'Frequency', 'UE Location', 'Scenario', 'Mode']).first()
    #newff = f.groupby(['n','power','f','basestation','indoor_ue','harbour_bool','load','ch']).first()
    #newff = newff.reset_index()
    print(newf.columns)
    #print(newff)
    #newf['RFI_maxofmax'] = f.groupby(['n','power','f','basestation','indoor_ue','harbour_bool','load','ch'], sort=False)['RFI_max'].transform('max')
    #newf['RFI_minofmax'] = f.groupby(['n','power','f','basestation','indoor_ue','harbour_bool','load','ch'], sort=False)['RFI_max'].transform('min')
    
    #
    print(newf.sample())
    #print(f[(f['f'] == 700e6) & (f['indoor_ue'] == False) & (f['harbour_bool'] == False) & (f['basestation'] == 0) & (f['load'] == 0.1) & (f['power'] == 23)])
    styler = newf.style
    styler.map(rating_color, subset='Maximum interference (dbm)')
    styler.format(subset="Maximum interference (dbm)", precision=1) \
    .format_index(escape="latex", axis=1) \
    .format_index(escape="latex", axis=0) \
    
    #.background_gradient(cmap='YlGnBu', subset='Maximum interference (dbm)')
    
    #.apply(rating_color, subset="Maximum interference (dbm)")
    #.hide(level=0, axis=0)
    print(styler.to_latex(
    environment='longtable',
    clines='skip-last;data',
    convert_css=True,
    #position_float="centering",
    multicol_align="|c|",
    hrules=True,))# \
  #.format(precision=3, thousands=".", decimal=",") \
  #.format_index(str.upper, axis=1) \
  #.relabel_index(["row 1", "row 2"], axis=0)

readMonteCarloSimulation()