import os
import pickle
import warnings
warnings.filterwarnings("ignore")
import sklearn
import numpy as np
import pandas as pd
pd.options.plotting.backend = "plotly"
import plotly.graph_objects as go
import plotly.express as px
from plotly.graph_objs.layout import YAxis,XAxis,Margin

from dateutil.relativedelta import relativedelta
from plotly.subplots import make_subplots
from sklearn import linear_model
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
class CT_opt():
    
    def __init__(self):
        self.df = None

    def CT_train(self,x,y,power):
        data = self.df[x+y].dropna()
        data = data[data[x[2]]>0]
        data = data.reset_index()
        xdata = data[x]
        ydata = data[y]
        self.CT_sc = MinMaxScaler()
        self.CT_sc.fit(xdata)
        xdata = self.CT_sc.transform(xdata)
        self.CT_pca = PCA(n_components=5)
        self.CT_pca.fit(xdata)
        xdata = self.CT_pca.transform(xdata)
        xdata = np.array(xdata).reshape(-1,xdata.shape[1])
        ydata = np.array(ydata)
        X_train, X_test, y_train, y_test = train_test_split(xdata, ydata, test_size=0.2,shuffle=True)
        regr = sklearn.linear_model.TweedieRegressor(power=power, alpha=0, max_iter=10000)
        regr.fit(X_train,y=y_train)
        cv = sklearn.model_selection.KFold(n_splits=5,shuffle=True)
        y_cv = sklearn.model_selection.cross_val_predict(regr,X_test,y=y_test,cv=cv)
        mae = round(sklearn.metrics.mean_absolute_error(y_test,y_cv),2)
        print('冷卻水塔 MAE:',mae)
        return regr,pd.DataFrame({'true':y_test.flatten(),'pred':y_cv.flatten()})

    def CH_train(self,x,y,power):
        data =self. df[x+y].dropna()
        data = data[data[x[2]]>0]
        data = data.reset_index()
        xdata = data[x]
        ydata = data[y]
        self.CH_sc = MinMaxScaler()
        self.CH_sc.fit(xdata)
        xdata = self.CH_sc.transform(xdata)
        self.CH_pca = PCA(n_components=5)
        self.CH_pca.fit(xdata)
        xdata = self.CH_pca.transform(xdata)
        xdata = np.array(xdata).reshape(-1,xdata.shape[1])
        ydata = np.array(ydata)
        X_train, X_test, y_train, y_test = train_test_split(xdata, ydata, test_size=0.2,shuffle=True)
        regr = sklearn.linear_model.TweedieRegressor(power=power, alpha=0, max_iter=10000)
        regr.fit(X_train,y=y_train)
        cv = sklearn.model_selection.KFold(n_splits=5,shuffle=True)
        y_cv = sklearn.model_selection.cross_val_predict(regr,X_test,y=y_test,cv=cv)
        mae = round(sklearn.metrics.mean_absolute_error(y_test,y_cv),2)
        print('冰水主機 MAE:',mae)
        return regr,pd.DataFrame({'true':y_test.flatten(),'pred':y_cv.flatten()})

    def CWP_train(self,x,y,power):
        data =self. df[x+y].dropna()
        data = data[data[x[2]]>0]
        data = data.reset_index()
        xdata = data[x]
        ydata = data[y]
        self.CWP_sc = MinMaxScaler()
        self.CWP_sc.fit(xdata)
        xdata = self.CWP_sc.transform(xdata)
        self.CWP_pca = PCA(n_components=5)
        self.CWP_pca.fit(xdata)
        xdata = self.CWP_pca.transform(xdata)
        xdata = np.array(xdata).reshape(-1,xdata.shape[1])
        ydata = np.array(ydata)
        X_train, X_test, y_train, y_test = train_test_split(xdata, ydata, test_size=0.2,shuffle=True)
        regr = sklearn.linear_model.TweedieRegressor(power=power, alpha=0, max_iter=10000)
        regr.fit(X_train,y=y_train)
        cv = sklearn.model_selection.KFold(n_splits=5,shuffle=True)
        y_cv = sklearn.model_selection.cross_val_predict(regr,X_test,y=y_test,cv=cv)
        mae = round(sklearn.metrics.mean_absolute_error(y_test,y_cv),2)
        print('冷卻水泵 MAE:',mae)
        return regr,pd.DataFrame({'true':y_test.flatten(),'pred':y_cv.flatten()})

    def train(self):
        self.CT_cols  = ['condenser_supply_temp','CT_eff','Approach','Wet_bulb_temp','condenser_temp_diff','chiller_supply_temp','chiller_return_temp','loading','chiller_RT','CT_Total_KW']
        self.CH_cols  = ['condenser_supply_temp','CT_eff','Approach','Wet_bulb_temp','condenser_temp_diff','chiller_supply_temp','chiller_return_temp','loading','chiller_RT','chiller_kwh']
        self.CWP_cols = ['condenser_supply_temp','CT_eff','Approach','Wet_bulb_temp','condenser_temp_diff','chiller_supply_temp','chiller_return_temp','loading','chiller_RT','CWP_Total_KW']
        self.CT_regr_kw,  self.CT_kw_df  = self.CT_train(self.CT_cols[:-1],[self.CT_cols[-1]],2)
        self.CH_regr_kw,  self.CH_kw_df  = self.CH_train(self.CH_cols[:-1],[self.CH_cols[-1]],0)
        self.CWP_regr_kw, self.CWP_kw_df = self.CWP_train(self.CWP_cols[:-1],[self.CWP_cols[-1]],0)

    def predict(self,c):
        self.df_last = self.df.iloc[-c]
        self.WB = self.df_last['Wet_bulb_temp']
        self.RG = np.linspace(1,10,100)
        Tctws = np.array([self.WB + i for i in self.RG])
        Approach = Tctws - self.WB
        CT_eff = (self.df_last.condenser_return_temp - Tctws) / (self.df_last.condenser_return_temp - self.WB)

        a = np.array([Tctws,CT_eff,Approach])
        b = np.repeat(np.array([self.df_last[['Wet_bulb_temp','condenser_temp_diff','chiller_supply_temp','chiller_return_temp','loading','chiller_RT']]]),100, axis=0)
        self.CT_pred_kw = self.CT_regr_kw.predict(self.CT_pca.transform(self.CT_sc.transform(np.concatenate((a, b.T), axis=0).T)))
        self.CH_pred_kw = self.CH_regr_kw.predict(self.CH_pca.transform(self.CH_sc.transform(np.concatenate((a, b.T), axis=0).T)))
        self.CWP_pred_kw = self.CWP_regr_kw.predict(self.CWP_pca.transform(self.CWP_sc.transform(np.concatenate((a, b.T), axis=0).T)))

        self.Total_pred_kw = self.CH_pred_kw+self.CT_pred_kw+self.CWP_pred_kw
        d = np.diff(self.Total_pred_kw)
        # self.best_index = np.argmin(np.where(d<-0.3,0,d))
        self.best_index = np.argmin(self.Total_pred_kw)
        self.best_Tctws = round(self.RG[self.best_index],2) + self.WB
        self.best_Approach = round(self.RG[self.best_index],2)
        return round(self.WB+self.best_Tctws,2)

    def plot(self,x0,x1):

        best_Approach = min(max(self.best_Tctws,x0),x1)
        layout = go.Layout(
            # title="{}".format(self.df_last.Datetime),
            xaxis=XAxis(
                title="<b>Cooling tower water supply Temperature</b>"
            ),
            xaxis2 = XAxis(
                title="<b>{} <br> Approach </b>".format(self.df_last.Datetime),
                overlaying= 'x', 
                side= 'top',
            ),
            yaxis=dict(
                title="<b> Cost (Kw)</b>"
            ),
        )

        fig =  go.Figure(layout=layout)
        fig.add_trace(go.Scatter(x=self.RG,y=self.CT_pred_kw,mode='lines',name='CT cost', xaxis='x2',line = dict(width=4)))
        fig.add_trace(go.Scatter(x=self.RG,y=self.CH_pred_kw,mode='lines',name='CH cost', xaxis='x2',line = dict(width=4)))
        fig.add_trace(go.Scatter(x=self.RG,y=self.CWP_pred_kw,mode='lines',name='CWP cost', xaxis='x2',line = dict(width=4)))
        fig.add_trace(go.Scatter(x=self.RG,y=self.CH_pred_kw+self.CT_pred_kw+self.CWP_pred_kw,mode='lines',name='CT+CH+CWP cost', xaxis='x2',line = dict(width=6)))
        
        fig.add_trace(go.Scatter(x = np.repeat(self.df_last.Approach+self.WB,4),dx=1,
            y = np.array([
                self.df_last.system_kwh-self.df_last.CHP_Total_KW,
                self.df_last.CT_Total_KW,
                self.df_last.chiller_kwh,
                self.df_last.CWP_Total_KW
                ]), marker={'symbol':4,'size':10},mode = 'lines+markers',name = '目前策略'))
        
        fig.add_trace(go.Scatter(x = np.repeat(best_Approach,4),dx=1,
            y = np.array([
                self.CH_pred_kw+self.CT_pred_kw+self.CWP_pred_kw,
                self.CT_pred_kw,
                self.CH_pred_kw,
                self.CWP_pred_kw
                ]).T[self.best_index], marker={'symbol':4,'size':10},mode = 'lines+markers',name = '推荐策略'))

        fig.add_vrect(
            x0=x0,
            x1=x1,
            fillcolor="Green",
            opacity=0.1,
            line_width=0,
        )

        fig.update_layout(
            xaxis2=dict(range=[1,10]),
            xaxis1=dict(range=[1+self.WB,10+self.WB]),
            autosize=False,
            width=800,
            height=850,
            template='plotly_dark'
            )

        return best_Approach,fig
