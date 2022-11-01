import pickle,os,time
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from utils.SQL import SQL
from utils.DataProcess import Start
from utils.ClooingTowerOptimize import CT_opt
# os.chdir('HL_Chiller_8')
while True:
    #loadong data from DB
    sql = SQL(server = "L8BAVMSQL\SQLEXPRESS",
                database = "HL_8CH_AIcontrol",
                username = "vefaa2",
                password = "Aa123456")

    data = sql.get_data(datatabel = "control",
                        StartDate = "{}".format((datetime.now() + relativedelta(months=-1)).strftime("%Y-%m-%d")),
                        ReturnFormat = "DataFrame")

    data.to_csv(os.path.join('input','HL_Chiller_8.csv'))

    #Data process & Training model
    opt = CT_opt()
    opt.df = Start('HL_8')
    opt.train()
    
    with open(os.path.join('model','regr.pkl'), 'wb') as f:
        pickle.dump(opt, f)



    #Write model result to DB
    with open(os.path.join('config','setting.pkl'), 'rb') as f:
        res = pickle.load(f)

    date = res['Dtime']

    columns = [
        'CH08_Set_Temp',
        'CH08_01_Tune',
        'CH08_02_Tune',
        'CH08_03_Tune',
        'CH08_04_Tune',
        'CT_Out_Tune']

    values = [
        str(round(res['AI_supply_temp'],2)),
        '@' + str(round(res['AI_supply_temp'],2)),
        '@' + str(round(res['AI_supply_temp'],2)),
        '@' + str(round(res['AI_supply_temp'],2)),
        '@' + str(round(res['AI_supply_temp'],2)),
        '@' + str(round(res['best_CT'],2))]

    sec = sql.update(
        datatabel = "control",
        columns = columns ,
        values = values,
        date = date)
    
    print(datetime.strftime(date, "%Y-%m-%d %H:%M:%S"))
    print('回傳成功' if sec else '回傳失敗') 
    for c,v in zip(columns,values):
        print(c,v)


    time.sleep(300)