"""
Stunting Estimation

@author: fawdywahyu
"""

import pandas as pd
import pyreadstat

# Load the data (Riskesdas 2013, Riskesdas 2018, SSGI 2021)
riskesdas2013, meta2013 = pyreadstat.read_sav('Riskesdas 2013.sav')
riskesdas2018, meta2018 = pyreadstat.read_sav('Riskesdas 2018.sav')
ssgi2021, meta2021 = pyreadstat.read_sav('SSGI 2021.sav')

# Extract the column name and label to column name
column_and_labels2013 = meta2013.column_names_to_labels
sequence2013 = range(len(column_and_labels2013))
df_labels2013 = pd.DataFrame(column_and_labels2013, index=sequence2013).iloc[0,:]

column_and_labels2018 = meta2018.column_names_to_labels
sequence2018 = range(len(column_and_labels2018))
df_labels2018 = pd.DataFrame(column_and_labels2018, index=sequence2018).iloc[0,:]

column_and_labels2021 = meta2021.column_names_to_labels
sequence2021 = range(len(column_and_labels2021))
df_labels2021 = pd.DataFrame(column_and_labels2021, index=sequence2021).iloc[0,:]

# Load acuan stunting dari who
stunting_boys_baduta = pd.read_excel('stunting boys zscore baduta.xlsx')
stunting_girls_baduta = pd.read_excel('stunting girls zscore baduta.xlsx')

stunting_boys_2_5 = pd.read_excel('stunting boys zscore 2_5.xlsx')
stunting_girls_2_5 = pd.read_excel('stunting girls zscore 2_5.xlsx')

# Estimasi Stunting
# Di data, range umur hanya 0-59 bulan

def stunting_riskesdas(kolom_tinggi=None, kolom_umur=None,
                       kolom_kelamin=None, posisi_pengukuran=None, 
                       data_input=None):
    
    # data_input = riskesdas2013
    # kolom_tinggi = 'K02B'
    # kolom_umur = 'B4K7BLN'
    # kolom_kelamin = 'B4K4'
    # posisi_pengukuran = 'K02C'
    
    df_input = data_input.copy()
    list_stunting = []
    
    for i in range(len(df_input)):
        tinggi = df_input[kolom_tinggi].iloc[i] #cm
        umur = df_input[kolom_umur].iloc[i] # bulan
        kelamin = df_input[kolom_kelamin].iloc[i] # 1=Laki2, 2=Perempuan
        pp = df_input[posisi_pengukuran].iloc[i] # 1=Berdiri, 2=Terlentang
        
        if umur<25 and kelamin==1:
            acuan_who = stunting_boys_baduta
        elif umur>=25 and kelamin==1:
            acuan_who = stunting_boys_2_5
        elif umur<25 and kelamin==2:
            acuan_who = stunting_girls_baduta
        else:
            acuan_who = stunting_girls_2_5
        
        slice_acuan = acuan_who[acuan_who['Month'] == umur].reset_index()
        mean_acuan = slice_acuan['M'].iloc[0]
        sd_acuan = slice_acuan['SD'].iloc[0]
        
        # Adjusment on Height or not
        adjusment = 0
        if umur<25 and pp==1:
            adjusment += 0.7
        elif umur>=25 and pp==2:
            adjusment -= 0.7
        tinggi += adjusment
        
        if tinggi > (-3*sd_acuan + mean_acuan) or tinggi < (-2*sd_acuan + mean_acuan):
            stunting = 'Stunted'
        elif tinggi < (-3*sd_acuan + mean_acuan):
            stunting = 'Severely Stunted'
        else:
            stunting = 'Normal'
        
        # stunting = 'stunting' if tinggi<acuan_stunting else 'tidak stunting'
        list_stunting.append(stunting)
    
    series_stunting = pd.Series(list_stunting)
    id_prov = df_input['B1R1']
    id_kab = df_input['B1R2']
    weight = df_input['FWT']
    
    result_stunting = pd.DataFrame({'ID Provinsi': id_prov,
                                    'ID Kabupaten': id_kab,
                                    'Kondisi Stunting': series_stunting,
                                    'Weight': weight})
    
    slice_stunting = result_stunting[result_stunting['Kondisi Stunting']!='Normal']
    df_grouped = slice_stunting.groupby('ID Kabupaten').agg({'Weight':'sum'})
    
    return df_grouped
