"""This testing code for munging data from costco visa download.
Dates and monetary values are correctly imported.

df = pd.read_csv('inventory.csv', header=None, 
                 names='model','size','width','color','qty','code'],
                 dtype = {'model':object,'size':float,
                          'width':object,'color':object,
                          'qty':int,'code': object})
df.info()

# TODO Can verbose output be sent to logging?
"""
import pandas as pd

# df = pd.read_excel("C:/Users/Conrad/Downloads/Home - Overview.xlsx", parse_dates = ['Last Call In'], verbose=True)
df = pd.read_csv('g:/downloads/Statement closed Mar 02, 2021.csv', parse_dates = ['Date'], verbose=True)

print(df)
print(df.info())