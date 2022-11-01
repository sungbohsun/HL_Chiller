import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.offline as offline

from stqdm import stqdm

def CT_eff_plot(v1,v2):
    fig = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = v1*100,
        mode = "gauge+number+delta",
        # title = {'text': f"<b>CT EFF</b>"},
        delta = {'reference': v2*100},
        gauge = {
            'bar': {'color': "lightgreen"},
            'axis': {'range': [None, 100]},
            'steps' : [
                {'range': [52, 53], 'color': "red"},
                {'range': [90, 100], 'color': "lightgray"}],
        })).update_layout(
            margin=dict(l=0,r=0,b=0,t=0,pad=0),
            autosize=False,
            width=400,
            height=400)
    return fig

def CT_data(df,i,th_RT=True,th_WB=True,delta=False):
    last_df = df.iloc[i]
    WB = last_df.Wet_bulb_temp
    RT = last_df.chiller_RT
    SP = last_df.condenser_supply_temp - last_df.Wet_bulb_temp
    data = df.copy()
    data = data[data.Approach<6]
    data = data[data.CT_Total_KW>0]
    data = data[data.chiller_kwh>0]
    data = data[data.CWP_Total_KW>0]
    data['delta'] = (data.condenser_supply_temp - data.Wet_bulb_temp)
    if th_RT:
        data = data[(data['chiller_RT'] < RT*1.02) & (data['chiller_RT'] > RT*0.98)]
    if th_WB:
        data = data[(data['Wet_bulb_temp'] < WB*1.02) & (data['Wet_bulb_temp'] > WB*0.98)]
    if delta:
        data = data[(data['delta'] < SP*1.02) & (data['delta'] > SP*0.98)]
    return data.reset_index(drop=True)

def CT_hist(all_df,df):      
    #歷史資料
    animation_df = pd.DataFrame()
    for i in stqdm(range(0,len(df))):
        th_df = CT_data(all_df,i,True,True,False)
        delta = (th_df.condenser_supply_temp - th_df.Wet_bulb_temp)
        target_col = ["chiller_kwh","CHP_Total_KW","CT_Total_KW","CWP_Total_KW"]
        for t in np.linspace(2,8,11):
            temp_df = th_df[(delta > t) & (delta < t+0.5)].reset_index(drop=True)
            for c in target_col:
                output = pd.DataFrame(index=[])
                output['c'] = [c]
                output['temp'] = str(round(t,2))
                output['count'] = temp_df.shape[0]
                output['Datetime'] = str(df.Datetime.iloc[i]),
                output['vaule'] = temp_df[c].mean() if temp_df.shape[0] >= 1 else 0
                animation_df = pd.concat([animation_df,output])

    fig = px.bar(animation_df, y='temp', x='vaule',color='c',animation_frame="Datetime",orientation='h',text_auto='.3s', template='plotly_dark')
    fig.update_layout(autosize=False,width=1800,height=800,template='plotly_dark',xaxis_range=[0,th_df[target_col].sum(axis=1).max()+100])
    fig.update_xaxes(title_text="<b>Total Kwh</b>")
    fig.update_yaxes(title_text="<b>Approach</b>")
    # py.plot(fig, output_type = 'file', include_plotlyjs = True, auto_open = False, filename =  os.path.join(self.sys_path,'output','CH',f'{self.file_name}_hist.html'))
    return fig

def CT_line(df,ai_col):
    AI2NUM = lambda values : float(values.replace('@','')) if type(values) != float else values
    fig = go.Figure()
    fig.add_trace(go.Scatter(x = df.Datetime , y= df.condenser_supply_temp ,mode='lines',name='Actual',line = dict(width=4)))
    fig.add_trace(go.Scatter(x = df.Datetime , y= list(map(AI2NUM,df[ai_col])) ,mode='lines',name='AI',line = dict(width=4)))
    fig.update_yaxes(title_text="<b>Cooling tower water supply Temperature</b>")
    return fig

def CH_line(df,ai_col):
    AI2NUM = lambda values : float(values.replace('@','')) if type(values) != float else values
    fig = go.Figure()
    fig.add_trace(go.Scatter(x = df.Datetime , y= df.chiller_supply_temp ,mode='lines',name='Actual',line = dict(width=4)))
    fig.add_trace(go.Scatter(x = df.Datetime , y= list(map(AI2NUM,df[ai_col])) ,mode='lines',name='AI',line = dict(width=4)))
    fig.update_yaxes(title_text="<b>chiller supply temp</b>")
    return fig

def CH_hist(all_df,df):      
    #歷史資料
    animation_df = pd.DataFrame()
    for i in stqdm(range(0,len(df))):
        data = CT_data(all_df,i,th_RT=True,th_WB=True,delta=True)
        target_col = ["chiller_kwh","CHP_Total_KW","CT_Total_KW","CWP_Total_KW"]
        rg = np.linspace(7.5,11,36)
        # rg = np.linspace(13,15,21)
        for t in rg:
            temp_df = data[(data.chiller_supply_temp > t-0.05) & (data.chiller_supply_temp < t+0.05)].reset_index(drop=True)
            # if temp_df.shape[0] < 1: continue
            for c in target_col:
                # index = np.argsort(temp_df.system_kwh)[len(temp_df)//2]
                output = pd.DataFrame(index=[])
                output['c'] = [c]
                output['temp'] = str(round(t,2))
                output['count'] = temp_df.shape[0]
                output['Datetime'] = str(df.Datetime.iloc[i]),
                output['vaule'] = temp_df[c].mean() if temp_df.shape[0] >= 1 else 0
                animation_df = pd.concat([animation_df,output])

    fig = px.bar(animation_df, y='temp', x='vaule',color='c',animation_frame="Datetime",orientation='h',text_auto='.2s', template='plotly_dark')
    fig.update_layout(autosize=False,width=1800,height=800,template='plotly_dark',xaxis_range=[0,data[target_col].sum(axis=1).max()+100],)
    fig.update_xaxes(title_text="<b>Total Kwh</b>")
    fig.update_yaxes(title_text="<b>chiller supply temp</b>")
    # py.plot(fig, output_type = 'file', include_plotlyjs = True, auto_open = False, filename =  os.path.join(self.sys_path,'output','CH',f'{self.file_name}_hist.html'))
    return fig

def PiePlot(df):
    labels = ["Chiller","CHP","CT","CWP"]
    values = list(map(int,df[["chiller_kwh","CHP_Total_KW","CT_Total_KW","CWP_Total_KW"]].iloc[-1]))
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, textinfo='label+percent')])
    # fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20,
    #                   marker=dict(colors=colors, line=dict(color='#000000', width=2)))
    fig.update_traces(hoverinfo='value', textfont_size=20,
                    marker=dict(line=dict(color='#000000', width=2)))

    fig.update_layout(
        template='plotly_dark',        
        autosize=False,
        width=500,
        height=500,
        margin=dict(l=0, r=0, t=0, b=0))
    return fig

def CH_RAC(data,cols):
    plot_dfs = pd.DataFrame()
    df_ = data[cols]
    for i in range(0,len(df_)):
        plot_df = pd.DataFrame(df_.iloc[i])
        plot_df.columns = ['loads']
        plot_df['locate'] = [c.replace('_Output','') for c in plot_df.index]
        plot_df['Datetime'] = str(data.Datetime.iloc[i])
        plot_dfs = pd.concat([plot_df,plot_dfs])
    plot_dfs = plot_dfs.reset_index(drop=True)
    fig = px.bar(plot_dfs, x="locate", y="loads", color="loads",animation_frame="Datetime",template='plotly_dark',text_auto='.2s')
    fig.update_xaxes(tickangle=45, tickfont=dict(size=12))
    fig.update_layout(yaxis_range=[0,100])
    # py.plot(fig, output_type = 'file', include_plotlyjs = True, auto_open = False, filename =  os.path.join(self.sys_path,'output','CH',f'{file_name}_RAC.html'))
    # fig.update_layout(barmode='stack', xaxis={'categoryorder': 'total descending'})
    return plot_df,fig
    
#更改網頁底色
def with_css_style(fig):
    plot_div = offline.plot(fig, config = dict({'scrollZoom': False, 'displayModeBar': True, 'editable': False}), output_type = 'div')
    template = """
    <head>
    </head>
    <body style="background-color:#111111;">
    <style>
    </style>
    <body>
    {plot_div:s}
    </body>""".format(plot_div = plot_div)
    return template

def write_html(str_html):
    str_html_new = str_html.split("<style>")[0] + '''<style> .js-line {
                stroke-dasharray: 10000;
                stroke-dashoffset: 10000;
                animation: flowAnimate 5s linear infinite;
            }

            @keyframes flowAnimate {
                from {
                    stroke-dashoffset: 100;
                }

                to {
                    stroke-dashoffset: 0;
                }
            }''' + str_html.split("<style>")[1]  + "<style>" + str_html.split("<style>")[2]
    return str_html_new

def Animation(fig): 
    return write_html(with_css_style(fig))