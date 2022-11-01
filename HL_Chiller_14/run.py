import pickle,os,time
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from utils.SQL import SQL
from utils.DataProcess import Start
from utils.ClooingTowerOptimize import CT_opt
while True:
    #loadong data from DB
    sql = SQL(server = "L8BAVMSQL\SQLEXPRESS",
                database = "HL_Chiller",
                username = "vefaa2",
                password = "Aa123456")

    data = sql.get_data(datatabel = "Optimize",
                        StartDate = "{}".format((datetime.now() + relativedelta(months=-1)).strftime("%Y-%m-%d")),
                        ReturnFormat = "DataFrame")
    data.to_csv(os.path.join('input','HL_Chiller_14.csv'))

    opt = CT_opt()
    opt.df = Start('HL_14')
    opt.train()
    with open(os.path.join('model','regr.pkl'), 'wb') as f:
        pickle.dump(opt, f)



    #Write model result to DB
    with open(os.path.join('config','setting.pkl'), 'rb') as f:
        res = pickle.load(f)

    date = res['Dtime']

    columns = [
        'CH14_Tune',
        'CH_1_sug_temp',
        'CH_2_sug_temp',
        'CH_3_sug_temp',
        'CH_4_sug_temp',
        'CH_5_sug_temp',
        'CH_6_sug_temp',
        'CH_7_sug_temp',
        'CH_8_sug_temp',
        'CH_9_sug_temp',
        'CT_sug_temp'
        ]

    values = [
        str(round(res['AI_supply_temp'],2)),
        '@' + str(round(res['AI_supply_temp'],2)),
        '@' + str(round(res['AI_supply_temp'],2)),
        '@' + str(round(res['AI_supply_temp'],2)),
        '@' + str(round(res['AI_supply_temp'],2)),
        '@' + str(round(res['AI_supply_temp'],2)),
        '@' + str(round(res['AI_supply_temp'],2)),
        '@' + str(round(res['AI_supply_temp'],2)),
        '@' + str(round(res['AI_supply_temp'],2)),
        '@' + str(round(res['AI_supply_temp'],2)),
        '@' + str(round(res['best_CT'],2))
        ]

    sec = sql.update(
        datatabel = "Optimize",
        columns = columns ,
        values = values,
        date = date)

    print(datetime.strftime(date, "%Y-%m-%d %H:%M:%S"))
    print('回傳成功' if sec else '回傳失敗') 
    for c,v in zip(columns,values):
        print(c,v)


    time.sleep(300)