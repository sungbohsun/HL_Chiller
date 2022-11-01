import os,pickle
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from streamlit_autorefresh import st_autorefresh
from datetime import datetime
from utils.EDA import *

st.set_page_config(
    page_title="❄️ 14°C 高溫冰水系統",
    page_icon="🧙",
    layout="wide")
count = st_autorefresh(interval=300*1000, key="fizzbuzzcounter")
# Run the autorefresh about every 2000 milliseconds (2 seconds) and stop
# after it's been refreshed 100 times.
with st.sidebar:
    st.success('Magichiller 啟動成功!', icon="✅")
    st.warning('右上角顯示RUNING時，請暫停操作', icon="↗️")

all_df = pd.read_csv(os.path.join('input','all_df.csv'))
df = pd.read_csv(os.path.join('input','small_df.csv'))
df1 = df.iloc[-1]
df2 = df.iloc[-2]

with open(os.path.join('config','setting.pkl'), 'rb') as f:
    res = pickle.load(f)

with open(os.path.join('model','regr.pkl'), 'rb') as p:
    opt = pickle.load(p)
    
opt.predict(1)

date = datetime.strftime(pd.to_datetime(df1.Datetime), "%Y-%m-%d %H:%M:%S")
res['Dtime'] = date


col1 = st.columns([3,1])
with col1[0]: 
    st.markdown(f"# ❄️ 14°C 高溫冰水系統")  
with col1[1]: 
    st.caption('🧙 MagiChiller')
    st.markdown('### 上次更新時間: '+res['Dtime'])

tab = st.tabs(['🌫️ 冷卻水出水溫優化','❄️ 冰水出水溫優化'])

with tab[0]:

    col2 = st.columns([3,3,3,3,3,3,2.2], gap="large")
    with col2[0]: 
        st.subheader('冰水系統 KPI')
        st.metric("system KPI", f"{round(df1.system_KPI,4)}", f"{round(df1.system_KPI - df2.system_KPI,4)}")
    with col2[1]: 
        st.subheader('冰水系統用電')
        st.metric("system kwh", f"{round(df1.system_kwh,0)}", f"{round(df1.system_kwh - df2.system_kwh,0)}")
    with col2[2]: 
        st.subheader('冰機總冷凍頓')
        st.metric("chiller RT", f"{round(df1.chiller_RT,0)}", f"{round(df1.chiller_RT - df2.chiller_RT,0)}")
    with col2[3]: 
        st.subheader('濕球溫度')
        st.metric("Wet bulb temp", f"{round(df1.Wet_bulb_temp,2)}", f"{round(df1.Wet_bulb_temp - df2.Wet_bulb_temp,2)}")
    with col2[4]: 
        st.subheader('冷卻水出水溫')
        st.metric("condenser supply_temp", f"{round(df1.condenser_supply_temp,2)}", f"{round(df1.condenser_supply_temp - df2.condenser_supply_temp,2)}")
    with col2[6]: 
            res['CT_low'] = st.number_input('AI冷卻水出水溫下限',step=0.1,value=res['CT_low'])
            res['CT_high'] = st.number_input('AI冷卻水出水溫上限',step=0.1,value= res['CT_high'])
            res['best_CT'],CT_fig = opt.plot( res['CT_low'] , res['CT_high'] )
    with col2[5]: 
        st.subheader('AI冷卻水出水溫')
        st.metric("best CT", f"{round(res['best_CT'],2)}")

    st.markdown('***') 
    st.markdown("## 🌫️ 冷卻水出水溫優化")
    st.markdown('**改變冷卻塔出水和回水溫度會增加一些成本，同時也會降低一些成本，提高冷卻塔出水和回水溫度會增加冷卻水泵和冰水主機運行成本，但會減少冷卻塔風扇需要做的工作量.因此最佳溫度不一定是塔能夠提供的最低溫度而是在所有設備的最低總運行成本（冰機 + 冷卻水泵 + 冷卻水塔）下能夠滿足特定負載的溫度。**')
    st.markdown('''
    |Controlled  Variable | Manipulated Variable | Optimization Criteria|
    |---------------------------|----------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
    |CT water supply temperature|Air flowrateobtained bylevel of fan operation | Optimum Approach is selected to keep the sum **_Fan cost_** + **_Chiller compressor cost_** + **_CT pumping cost_** to a minimum|
    ''')
    st.markdown('***')
    st.plotly_chart(CT_line(df=df,ai_col='CT_sug_temp'), use_container_width=True)
    col3 = st.columns([1,1.5], gap="large")
    with col3[0]:
        with st.expander("", expanded=True):
            st.subheader('冷卻塔熱效率 (Cooling Tower Thermal Efficiency)')
            st.markdown('**冷卻塔效率主要取決於氣候條件，特別是環境空氣的相對濕度及其濕球溫度。**')
            st.plotly_chart(CT_eff_plot(df1.CT_eff,df2.CT_eff))
            st.markdown('***')
            st.markdown(r'$$Efficiency = \frac{(T_{ctwr} - T_{ctws} )}{(T_{ctwr} - T_{wb} )} * 100$$')
            st.markdown(r'**$$T_{ctws}$$ : _Cooling tower water supply temperature_**')
            st.markdown(r'**$$T_{ctws}$$ : _Cooling tower water return temperature_**')
            st.markdown(r'**$$T_{wb}$$ : _Wet-bulb temperature_**')
            st.markdown('***')
        with st.expander("", expanded=True):
            st.subheader('運行成本 (Operating cost)')
            st.markdown('**整個冷卻系統的年運行成本可以通常分解成冰機、冰水泵、冷卻水塔與冷卻水泵**')
            st.plotly_chart(PiePlot(df), use_container_width=True)
    with col3[1]:
        with st.expander("", expanded=True):
            st.subheader('🚀 AI 最佳化冷卻水出水溫 (AI Optimize Tctws)')
            st.markdown('**運用模型預測不同冷卻水出水溫對於三項設備用電量變化量，推算出最佳溫度**')
            st.plotly_chart(CT_fig, use_container_width=True)
        with st.expander("", expanded=True):
            st.subheader('📊 成本分析模式 (Cost Analysis Model)')
            st.markdown('**相同冷凍頓與濕球溫度下，不同趨近溫度(冷卻水出水溫-濕球溫度)對於系統成本影響**')
            st.plotly_chart(CT_hist(all_df,df.iloc[-12:]), use_container_width=True)

with tab[1]:
    col2 = st.columns([3,3,3,3,3,3,2.2], gap="large")
    with col2[0]: 
        st.subheader('冰水系統 KPI')
        st.metric("system KPI", f"{round(df1.system_KPI,4)}", f"{round(df1.system_KPI - df2.system_KPI,4)}")
    with col2[1]: 
        st.subheader('冰水系統用電')
        st.metric("system KPI", f"{round(df1.system_kwh,0)}", f"{round(df1.system_kwh - df2.system_kwh,0)}")
    with col2[2]: 
        st.subheader('冰機總冷凍頓')
        st.metric("system KPI", f"{round(df1.chiller_RT,0)}", f"{round(df1.chiller_RT - df2.chiller_RT,0)}")
    with col2[3]: 
        st.subheader('冰水回水溫')
        st.metric("system KPI", f"{round(df1.chiller_return_temp,2)}", f"{round(df1.chiller_return_temp - df2.chiller_return_temp,2)}")
    with col2[4]: 
        st.subheader('冰水出水溫')
        st.metric("system KPI", f"{round(df1.chiller_supply_temp,2)}", f"{round(df1.chiller_supply_temp - df2.chiller_supply_temp,2)}")
    with col2[6]: 
            res['CH_low'] = st.number_input('AI冰水出水溫下限',step=0.1,value=res['CH_low'])
            res['CH_high'] = st.number_input('AI冰水出水溫上限',step=0.1,value=res['CH_high'])

    st.markdown("***")
    col = st.columns(2)
    with col[0]:
        st.markdown("## ❄️ 冰水出水溫優化")
        st.markdown('''
        |Controlled  Variable | Manipulated Variable | Optimization Criteria|
        |---------------------------|----------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
        |Chilled water supply temperature|Rate of chiller compressor operation| The optimum TIC set points the maximum chilled water supply temperature, which willsatisfy all the process loads|
        ''')
        st.caption("")
        st.markdown('📘 最佳化方法 (Optimization Criteria)')
        st.markdown('優化控制迴路可確保在冷凍水溫度最大化的同時，始終滿足工廠中所有冷凍水用戶的需求。 這是通過選擇工廠中開度最大的冷凍水閥並將該開度與閥位控制器的 90% 設定點進行比較來完成的。 如果即使是最大開度的閥門也低於 90% 開度，則增加冰水設定出水溫； 如果閥門開度超過 90%，則降低冰水設定出水溫。')

    with col[1]:
        st.markdown("## 🌡️ 冰水回水溫優化")
        st.markdown('''
        |Controlled  Variable | Manipulated Variable | Optimization Criteria|
        |---------------------------|----------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
        |Chilled water return temperature|Rate of chilled water pumping | The optimum TIC set point s the maximum chilled water return temperature that will satisfy all the process loads|
        ''')
        st.caption("")
        st.markdown('📘 最佳化方法 (Optimization Criteria)')
        st.markdown('調整冰水回水溫需考量冰水泵和冰水主機的綜合運行成本，因為這個 ΔT (Tchwr - Tchws)的增加會使吸入壓力升高降低壓縮機的運行成本，同時ΔT 越高，需要泵送的水越少也降低泵送成本，這個優化策略的目的是最大化這個 ΔT。')
    st.markdown("***")
    st.plotly_chart(CH_line(df=df,ai_col='CH14_Tune'), use_container_width=True)
    st.subheader('冰水重點控制閥位')
    keyword = ['RAC_B1','L35','L60']
    cols = [ q for q in list(df.columns) if  sum([q.find(w) for w in keyword]) > -len(keyword)]
    with st.expander('AI控制RAC參考點'):
        col3 = st.columns(10)
        res['select'] = [c for i,c in enumerate(cols) if col3[i%9].checkbox(f'{c}',value=True if c in res['select'] else False)]
        # res['select'] = [c for i,c in enumerate(cols) if col3[i%9].checkbox(f'{c}',value=True)]

    plot_df , fig = CH_RAC(df.iloc[-12:],res['select'])
    st.plotly_chart(fig, use_container_width=True)
    if max(plot_df.loads) > 90:
        AI_supply_temp = df1.chiller_supply_temp - 0.12
    else :
        AI_supply_temp = df1.chiller_supply_temp + 0.12

    res['AI_supply_temp'] = min(max(AI_supply_temp,res['CH_low']),res['CH_high'])

    with col2[5]: 
        st.subheader('AI冰水設定溫度')
        st.metric("AI_supply_temp", f"{round(res['AI_supply_temp'],2)}")

    st.subheader('📊 成本分析模式 (Cost Analysis Model)')
    st.markdown('**相同冷凍頓與濕球溫度下，不同趨近溫度(冷卻水出水溫-濕球溫度)對於系統成本影響**')
    show = st.checkbox('show',value=False)
    if show:
        st.plotly_chart(CH_hist(all_df,df.iloc[-12:]), use_container_width=True)

    with open(os.path.join('config','setting.pkl'), 'wb') as f:
        pickle.dump(res, f)