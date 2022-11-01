import os
import pandas as pd
import plotly.express as px

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
    fig = px.bar(plot_dfs, x="locate", y="loads", color="loads",animation_frame="Datetime",template='plotly_dark')
    fig.update_xaxes(tickangle=45, tickfont=dict(size=12))
    fig.update_layout(yaxis_range=[0,100])
    # py.plot(fig, output_type = 'file', include_plotlyjs = True, auto_open = False, filename =  os.path.join(self.sys_path,'output','CH',f'{file_name}_RAC.html'))
    # fig.update_layout(barmode='stack', xaxis={'categoryorder': 'total descending'})
    return plot_df,fig
