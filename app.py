import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

## Download and wrangle GSS data

gss = pd.read_csv("https://github.com/jkropko/DS-6001/raw/master/localdata/gss2018.csv",
                 encoding='cp1252', low_memory= False, na_values=['IAP','IAP,DK,NA,uncodeable', 'NOT SURE',
                                               'DK', 'IAP, DK, NA, uncodeable', '.a', "CAN'T CHOOSE"])

mycols = ['id', 'wtss', 'sex', 'educ', 'region', 'age', 'coninc',
          'prestg10', 'mapres10', 'papres10', 'sei10', 'satjob',
          'fechld', 'fefam', 'fepol', 'fepresch', 'meovrwrk'] 
gss_clean = gss[mycols]

gss_clean = gss_clean.rename({'wtss':'weight', 
                              'educ':'education', 
                              'coninc':'income', 
                              'prestg10':'job_prestige',
                              'mapres10':'mother_job_prestige', 
                              'papres10':'father_job_prestige', 
                              'sei10':'socioeconomic_index', 
                              'fechld':'relationship', 
                              'fefam':'male_breadwinner', 
                              'fehire':'hire_women', 
                              'fejobaff':'preference_hire_women', 
                              'fepol':'men_bettersuited', 
                              'fepresch':'child_suffer',
                              'meovrwrk':'men_overwork'},axis=1)
gss_clean.age = gss_clean.age.replace({'89 or older':'89'})
gss_clean.age = gss_clean.age.astype('float')

## Generate the individual tables and figures

### Markdown text
markdown= '''
In March 20202, the U.S. Department of Labor published a blog by Janelle Jones entitled ['5 Facts About the State of the Gender Pay Gap'](https://blog.dol.gov/2021/03/19/5-facts-about-the-state-of-the-gender-pay-gap). The blog was published to generate awareness to discrepancies between gender and pay.  A summary of 5 facts are as follows: 1. In 2020, for every dollar a man earns, a woman earns 82 cents. 2. The wage gap is even greater than 82 cents per dollar for non-white women. 3. In almost every occupation, women earn less than men. 4. When being compared at equal educational attainment levels, a woman earns less than a man of her same race. 5. The COVID pandemic is a major setback to closing the gender pay gap. The Economic Policy Institute published a report entitled ['What is the gender pay gap and is it real?'](https://www.epi.org/publication/what-is-the-gender-pay-gap-and-is-it-real)  by E. Gould, J. Scheider, and K. Geier.  The report  introduces the vast number of ways to measure gender pay and discusses the reasons specific measurement techniques create different gender pay gap results.  

The [General Social Survey (GSS)](http://www.gss.norc.org/About-The-GSS) is a national survey developed by James A. Davis in 1972 and is used to study sociological trends in the United States. The dashboard presents [GSS](http://www.gss.norc.org/About-The-GSS) data specific to income and job prestige for males and females. The biennial survey, monitors past and present sociological trends.  Adults from across the United States and coming from a random mix of rural, urban and suburban areas are the target population. Survey questions cover a vast number of topics including occupational prestige, income, age when first married, and political party affiliation. The questions are regulary adapted to address current social matters and the survey is currently offered online. GSS survey questions and documentation can be found on their [website](http://www.gss.norc.org/About-The-GSS).
'''

### Table
gsscols = ['income', 'job_prestige','socioeconomic_index', 'education', 'sex' ]

gss_table = gss_clean[gsscols]

gss_table = gss_table.rename({'job_prestige':'occupational_prestige'}, axis=1)

gss_table = gss_table.groupby('sex').agg({'income':'mean',
                             'occupational_prestige':'mean',
                             'socioeconomic_index': 'mean',
                              'education':'mean'}).reset_index().round(2)

fig_table = ff.create_table(gss_table)

### Barplot

# change datatype of `male_breadwinner` to 'category'
gss_clean['male_breadwinner']= gss_clean['male_breadwinner'].astype('category')

# reorder categories in male_breadwinner
gss_clean['male_breadwinner']= gss_clean['male_breadwinner'].cat.reorder_categories(['strongly agree', 'agree', 'disagree', 'strongly disagree'])

gss_bar = gss_clean.groupby(['sex', 'male_breadwinner']).size().reset_index()
gss_bar = gss_bar.rename({0:'count'}, axis=1)

fig_bar = px.bar(gss_bar, x='male_breadwinner', y='count', color='sex',
             color_discrete_map = {'male':'blue', 'female':'red'},
       labels={'count':'Number of people', 'male_breadwinner':"Agreement level choice"},
      barmode= 'group')

### Scatterplot
fig_scatter = px.scatter(gss_clean, x='job_prestige', y='income', 
                     color = 'sex', 
                     trendline='ols', 
                     height=600, width=600,
                     labels={'income': 'income ($)', 
                             'job_prestige':'occupational prestige'},
                     hover_data=['education', 'socioeconomic_index'])

### Boxplots
# Distribution of Income Boxplot

fig_box = px.box(gss_clean, x='income', y = 'sex', color = 'sex',
                   labels={'income':'income ($)', 'sex':''})
fig_box.update_layout(showlegend=False)

# Distribution of Occupational Prestige Boxplot

fig_box2 = px.box(gss_clean, x='job_prestige', y = 'sex', color = 'sex',
                   labels={'job_prestige':'job prestige', 'sex':''})
fig_box2.update_layout(showlegend=False)

### 2x3 Faceted Boxplots
dfcols = ['income', 'sex', 'job_prestige']

df = gss_clean[dfcols]                  # create new dataframe     

binned= pd.cut(df['job_prestige'], 6)   #create 6 equal bins for `job_prestige`

df['binned'] = binned
df = df.dropna()                        # drop all rows with missing values

fig_df = px.box(df, x='income', y = 'sex', color = 'sex',
            facet_col= 'binned', facet_col_wrap= 2,
            labels={'income':'income ($)', 'sex':''},
            color_discrete_map = {'male':'blue', 'female':'red'})
fig_df.update_layout(showlegend=False)
fig_df.for_each_annotation(lambda a: a.update(text=a.text.replace("binned=", "job prestige level =" )))


### Create app
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout=html.Div(
    [
     html.H1("Dashboard of Income for Males and Females in the United States"),
     
     html.H2("Gender Wage Gap Discussion"),
     dcc.Markdown(children = markdown),

 
     html.H2("Averages for Males and Females "),
     dcc.Graph(figure =fig_table),
 
     html.H2("Agreement Levels to 'The Male is the Breadwinner' "),
     dcc.Graph(figure=fig_bar),
 
     html.H2("Income vs Job Prestige for Males and Females"),
     dcc.Graph(figure=fig_scatter),
     
     html.Div([
         html.H2("Distribution of Income for Males and Females"),
         dcc.Graph(figure=fig_box)],style={'width': '48%', 'float': 'left'}),
 
     html.Div([
         html.H2("Distribution of Occupational Prestige for Males and Females "),
         dcc.Graph(figure=fig_box2)],style={'width': '48%', 'float': 'right'}),
     
     html.Div([
         html.H2("Income Distribution per Job Prestige Levels for Males and Females"),
         dcc.Graph(figure=fig_df)])
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True)

