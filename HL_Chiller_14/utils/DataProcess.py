import os
import numpy  as np
import pandas as pd

from scipy import stats
from dateutil.relativedelta import relativedelta
#移除離群直(3倍標準差)
def Outliner_z3(df):
    df = df.reset_index()
    remove = np.array([])
    for col in df.columns:
        try:
            if not (pd.api.types.is_datetime64_any_dtype(df[col])):
                z = np.abs(stats.zscore(df[col].dropna()))
                remove = np.concatenate((remove,np.where(z > 4)[0]))
            print(col,'remove',len(remove))
        except:
            print("pass col:",col)
            continue
    data = df.drop(np.array(np.unique(remove),dtype=np.int64))
    return data.reset_index(drop=True)


def Start(site):

    sys_path = os.getcwd()

    if site =="HL_8":

        data = pd.read_csv(os.path.join(sys_path,"input","HL_Chiller_8.csv"),encoding="big5")
        chiller_num = [1,2,3,4]

        dic = {}
        dic["Datetime"]              = "Date"
        dic["Enthalpy"]              = "OA_E1"
        dic["Wet_bulb_temp"]         = "CT_WDT_B"
        dic["chiller_supply_temp"]   = "CH_OUT_TT"
        dic["chiller_return_temp"]   = "CH_Return_TT"
        dic["condenser_supply_temp"] = "CT_OUT_TT"
        dic["condenser_return_temp"] = "CT_IN_TTA"
        dic["chiller_RT"]            = "SYS_RT"
        dic["chiller_kwh"]           = "CH_Total_Kw"
        dic['CT_Total_KW']           = 'CT_Total_Kw'
        dic['CHP_Total_KW']          = 'CHP_Total_Kw'
        dic['CWP_Total_KW']          = 'CWP_Total_Kw'

        for c in chiller_num:
            dic[f"chiller_{c:02}_kwh_A"]         = f"CH{c:02}_1_KW"
            dic[f"chiller_{c:02}_kwh_B"]         = f"CH{c:02}_2_KW"
            dic[f"chiller_{c:02}_return_temp"]   = f"CH{c:02}_Return_TT"
            dic[f"chiller_{c:02}_supply_temp"]   = f"CH{c:02}_OUT_TT"
            dic[f"chiller_{c:02}_loading_A"]     = f"CH{c:02}_1_Load"
            dic[f"chiller_{c:02}_loading_B"]     = f"CH{c:02}_2_Load"

        all_df = data.rename(columns={y: x for x, y in dic.items()}).copy()
        all_df['Datetime'] = [time.replace("上午 ","").replace("下午 ","") for time in all_df['Datetime']]
        all_df['Datetime'] = pd.to_datetime(all_df['Datetime'])
        all_df = all_df.sort_values("Datetime")
        all_df["system_kwh"] = all_df[["chiller_kwh","CT_Total_KW","CHP_Total_KW","CWP_Total_KW"]].sum(axis=1)

        for c in chiller_num:
            all_df[f"chiller_{c:02}_kwh"] = all_df[f"chiller_{c:02}_kwh_A"] + all_df[f"chiller_{c:02}_kwh_B"]
            #單機流量 = (單機耗電 /總耗電) x  (總冷凍頓 / (單機冰水出水溫−單機冰水出水溫)) x 3.024
            all_df[f"chiller_{c:02}_flow"] = all_df[f"chiller_{c:02}_kwh"]/all_df["chiller_kwh"]*all_df["chiller_RT"]/(all_df[f"chiller_{c:02}_return_temp"] - all_df[f"chiller_{c:02}_supply_temp"])*3.024
            #計算冰機附載
            all_df[f"chiller_{c:02}_loading"] = (all_df[f"chiller_{c:02}_loading_A"] + all_df[f"chiller_{c:02}_loading_B"])/2

        #計算冷卻水平均溫差 condenser_sensor_dif為冷卻水出水塔至入冰機前的溫差
        all_df["condenser_temp_diff"] = (all_df["condenser_return_temp"] - all_df["condenser_supply_temp"]) - 1
        all_df["loading"] = all_df[[f"chiller_{c:02}_loading" for c in chiller_num]].mean(axis=1)
        all_df['CT_hz_max'] = all_df[[f'CT{C:02d}_VFD_OUT' for C in range(2,12,2)]].max(axis=1)

    if site =="HL_14":

        data = pd.read_csv(os.path.join(sys_path,"input","HL_Chiller_14.csv"),encoding="big5")
        chiller_num = [1,2,3,4,5,6,7,8,9]

        dic = {}
        dic["Datetime"]              = "Date"
        dic["Enthalpy"]              = "OA_E1"
        dic["Wet_bulb_temp"]         = "CT_WDT_B"
        dic["chiller_supply_temp"]   = "CH14_Out_T"
        dic["chiller_return_temp"]   = "CH14_Return_T"
        dic["condenser_supply_temp"] = "CT_Out_T"
        dic["condenser_return_temp"] = "CT_In_T"
        dic["chiller_flow"]          = "CH14_FT"
        dic["chiller_kwh"]           = "CH14_Total_KW"

        for c in chiller_num:
            dic[f"chiller_{c:02}_kwh_A"]         = f"CH14_{c:02}_1KW"
            dic[f"chiller_{c:02}_kwh_B"]         = f"CH14_{c:02}_2KW"
            dic[f"chiller_{c:02}_return_temp"]   = f"CH14_{c:02}_INTT"
            dic[f"chiller_{c:02}_supply_temp"]   = f"CH14_{c:02}_OutTT"
            dic[f"chiller_{c:02}_loading_A"]     = f"CH{c:02}_1_loading"
            dic[f"chiller_{c:02}_loading_B"]     = f"CH{c:02}_2_loading"

        all_df = data.rename(columns={y: x for x, y in dic.items()}).copy()
        all_df['Datetime'] = [time.replace("上午 ","").replace("下午 ","") for time in all_df['Datetime']]
        all_df['Datetime'] = pd.to_datetime(all_df['Datetime'])
        all_df = all_df.sort_values("Datetime")
        all_df["CT_Total_KW"] = np.array(all_df[[f"CT{c:02}_Kw" for c in range(1,15,2)]]).sum(axis=1)
        all_df["system_kwh"] = all_df[["chiller_kwh","CT_Total_KW","CHP_Total_KW","CWP_Total_KW"]].sum(axis=1)
        all_df["chiller_RT"] = (all_df['chiller_return_temp'] - all_df['chiller_supply_temp'])*all_df['chiller_flow'] * 1000 / 3024

        for c in chiller_num:
            all_df[f"chiller_{c:02}_kwh"] = all_df[f"chiller_{c:02}_kwh_A"] + all_df[f"chiller_{c:02}_kwh_B"]
            #單機流量 = (單機耗電 /總耗電) x  (總冷凍頓 / (單機冰水出水溫−單機冰水出水溫)) x 3.024
            all_df[f"chiller_{c:02}_flow"] = all_df[f"chiller_{c:02}_kwh"]/all_df["chiller_kwh"]*all_df["chiller_RT"]/(all_df[f"chiller_{c:02}_return_temp"] - all_df[f"chiller_{c:02}_supply_temp"])*3.024
            #計算冰機附載
            all_df[f"chiller_{c:02}_loading"] = (all_df[f"chiller_{c:02}_loading_A"] + all_df[f"chiller_{c:02}_loading_B"])/2

        #計算冷卻水平均溫差 condenser_sensor_dif為冷卻水出水塔至入冰機前的溫差
        all_df["condenser_temp_diff"] = (all_df["condenser_return_temp"] - all_df["condenser_supply_temp"]) - 1
        all_df["loading"] = all_df[[f"chiller_{c:02}_loading" for c in chiller_num]].mean(axis=1)
        all_df['CT_hz_max'] = all_df[[f'CT_{C:02d}_VFD' for C in range(1,14,2)]].max(axis=1)
        
    if site =="TC_8":

        data = pd.read_csv(os.path.join(sys_path,"input","TC3.csv"),encoding="big5")
        chiller_num = [1,2,3,4,5,6]

        dic = {}
        dic["Datetime"]              = "Dtime"
        dic["Enthalpy"]              = "Outdoor_Enthaply"
        dic["Wet_bulb_temp"]         = "Wet_bulb_temp_MT012"
        dic["chiller_supply_temp"]   = "CH8_Total_supply_temp"
        dic["chiller_return_temp"]   = "CH8_Total_return_temp"
        dic["condenser_supply_temp"] = "CT_8C_supply_TT011"
        dic["condenser_return_temp"] = "CT_8C_return_TT032"
        dic["chiller_KPI"]           = "CH8_KPI"

        for c in chiller_num:
            dic[f"chiller_{c:02}_kwh"]           = f"CH8{c:02}_KW"
            # dic[f"chiller_{c:02}_return_temp"]   = f"CH14_{c:02}_INTT"
            # dic[f"chiller_{c:02}_supply_temp"]   = f"CH14_{c:02}_OutTT"
            dic[f"chiller_{c:02}_loading_A"]     = f"CH8{c:02}_Left_Loading"
            dic[f"chiller_{c:02}_loading_B"]     = f"CH8{c:02}_Right_Loading"
        
        all_df = data.rename(columns={y: x for x, y in dic.items()}).copy()
        all_df[f"chiller_01_loading_B"] = all_df[f"chiller_01_loading_A"] #8度1號機只有單頭 
        all_df['Datetime'] = [time.replace("上午 ","").replace("下午 ","") for time in all_df['Datetime']]
        all_df['Datetime'] = pd.to_datetime(all_df['Datetime'])
        all_df = all_df.sort_values("Datetime")
        all_df["CT_Total_KW"] = np.array(all_df[[f"CT{c:02}_KW" for c in range(1,13,2)]]).sum(axis=1)
        all_df["CHP_Total_KW"] = np.array(all_df[[f"CH8{c:02}_Pump_KW" for c in range(1,6)]]).sum(axis=1)
        all_df["CWP_Total_KW"] = np.array(all_df[[f"CT8{c:02}_Pump_KW" for c in range(1,6)]]).sum(axis=1)
        all_df["chiller_kwh"] = np.array(all_df[[f"chiller_{c:02}_kwh" for c in chiller_num]]).sum(axis=1)
        all_df["system_kwh"] = all_df[["chiller_kwh","CT_Total_KW","CHP_Total_KW","CWP_Total_KW"]].sum(axis=1)
        all_df["chiller_RT"] = all_df["chiller_kwh"]/all_df["chiller_KPI"]

        for c in chiller_num:
            #單機流量 = (單機耗電 /總耗電) x  (總冷凍頓 / (單機冰水出水溫−單機冰水出水溫)) x 3.024
            # all_df[f"chiller_{c:02}_flow"] = all_df[f"chiller_{c:02}_kwh"]/all_df["chiller_kwh"]*all_df["chiller_RT"]/(all_df[f"chiller_{c:02}_return_temp"] - all_df[f"chiller_{c:02}_supply_temp"])*3.024
            #計算冰機附載
            all_df[f"chiller_{c:02}_loading"] = (all_df[f"chiller_{c:02}_loading_A"] + all_df[f"chiller_{c:02}_loading_B"])/2

        #計算冷卻水平均溫差 condenser_sensor_dif為冷卻水出水塔至入冰機前的溫差
        all_df["condenser_temp_diff"] = (all_df["condenser_return_temp"] - all_df["condenser_supply_temp"]) - 1
        all_df["loading"] = all_df[[f"chiller_{c:02}_loading" for c in chiller_num]].mean(axis=1)

    if site =="TC_14":

        data = pd.read_csv(os.path.join(sys_path,"input","TC3.csv"),encoding="big5")
        chiller_num = [1,2,3,4,5,6]

        dic = {}
        dic["Datetime"]              = "Dtime"
        dic["Enthalpy"]              = "Outdoor_Enthaply"
        dic["Wet_bulb_temp"]         = "Wet_bulb_temp_MT012"
        dic["chiller_supply_temp"]   = "14CH_Out"
        dic["chiller_return_temp"]   = "14CH_In"
        dic["condenser_supply_temp"] = "CT_14C_supply_TT021"
        dic["condenser_return_temp"] = "CT_14C_return_TT031"
        dic["CHP_Total_KW"]          = "14C_CHP_KW"
        dic["CWP_Total_KW"]          = "14C_CWP_KW"
        dic["chiller_KPI"]           = "14CH_KPI"

        for c in chiller_num:
            dic[f"chiller_{c:02}_kwh"]           = f"14CH{c:02}_KW"
            # dic[f"chiller_{c:02}_return_temp"]   = f"CH14_{c:02}_INTT"
            # dic[f"chiller_{c:02}_supply_temp"]   = f"CH14_{c:02}_OutTT"
            dic[f"chiller_{c:02}_loading_A"]     = f"CH14_{c:02}_Loading_L"
            dic[f"chiller_{c:02}_loading_B"]     = f"CH14_{c:02}_Loading_R"
        
        all_df = data.rename(columns={y: x for x, y in dic.items()}).copy()
        all_df['Datetime'] = [time.replace("上午 ","").replace("下午 ","") for time in all_df['Datetime']]
        all_df['Datetime'] = pd.to_datetime(all_df['Datetime'])
        all_df = all_df.sort_values("Datetime")
        all_df["CT_Total_KW"] = np.array(all_df[[f"CT{c:02}_KW" for c in range(2,13,2)]]).sum(axis=1)
        all_df["chiller_kwh"] = np.array(all_df[[f"chiller_{c:02}_kwh" for c in chiller_num]]).sum(axis=1)
        all_df["system_kwh"] = all_df[["chiller_kwh","CT_Total_KW","CHP_Total_KW","CWP_Total_KW"]].sum(axis=1)
        all_df["chiller_RT"] = all_df["chiller_kwh"]/all_df["chiller_KPI"]

        for c in chiller_num:
            #單機流量 = (單機耗電 /總耗電) x  (總冷凍頓 / (單機冰水出水溫−單機冰水出水溫)) x 3.024
            # all_df[f"chiller_{c:02}_flow"] = all_df[f"chiller_{c:02}_kwh"]/all_df["chiller_kwh"]*all_df["chiller_RT"]/(all_df[f"chiller_{c:02}_return_temp"] - all_df[f"chiller_{c:02}_supply_temp"])*3.024
            #計算冰機附載
            all_df[f"chiller_{c:02}_loading"] = (all_df[f"chiller_{c:02}_loading_A"] + all_df[f"chiller_{c:02}_loading_B"])/2

        #計算冷卻水平均溫差 condenser_sensor_dif為冷卻水出水塔至入冰機前的溫差
        all_df["condenser_temp_diff"] = (all_df["condenser_return_temp"] - all_df["condenser_supply_temp"]) - 1
        all_df["loading"] = all_df[[f"chiller_{c:02}_loading" for c in chiller_num]].mean(axis=1)
        
    #計算系統KPI
    # all_df['chiller_KPI'] = all_df["chiller_kwh"]/all_df["chiller_RT"]
    all_df['system_KPI'] = all_df["system_kwh"]/all_df["chiller_RT"]
    all_df['Approach'] = all_df.condenser_supply_temp - all_df.Wet_bulb_temp
    all_df['CT_eff'] = (all_df.condenser_return_temp - all_df.condenser_supply_temp) / (all_df.condenser_return_temp - all_df.Wet_bulb_temp)
    #移除離群值(3倍標準差)
    all_df = all_df[all_df.Datetime>all_df.Datetime.iloc[-1] + relativedelta(months=-1)]
    all_df.to_csv(os.path.join('input','all_df.csv'),encoding='big5')
    small_df = all_df.iloc[-144:]
    small_df.to_csv(os.path.join('input','small_df.csv'),encoding='big5')
    # all_df = Outliner_z3(all_df)
    all_df = all_df.drop_duplicates('Datetime')


    return all_df

