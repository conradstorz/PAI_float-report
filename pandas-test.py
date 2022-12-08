import pandas as pd
 
# reading the CSV file
csvFile = pd.read_csv('t.csv', parse_dates=['Date'])

# converting to string data type
print('Convert')
csvFile['Amount'] = csvFile['Amount'].astype(str)
print(csvFile)

# remove $ from Amount field
print('Convert to numeric')
#csvFile['Amount'] = csvFile['Type'].apply(lambda x: csvFile['Amount'].str.slice(1,-1) if 'Discount' else csvFile['Amount'])
#csvFile['Amount'].to_numeric(csvFile.Amount.str.strip('$'))
csvFile['Amount'] = csvFile['Amount'].str.lstrip('$')
csvFile['Amount'] = pd.to_numeric(csvFile['Amount'])
print(csvFile.dtypes)

# displaying the contents of the CSV file
print('Display')
print(csvFile)

# correct the sign of the amounts
print('Correct')
#csvFile['Amount'] = csvFile['Type'].apply(lambda x: x[-csvFile['Amount'] if 'Discount' else csvFile['Amount'])
csvFile['Amount'].where(~(csvFile.Type == 'Discount'), other=-csvFile['Amount'], inplace=True)

# displaying the contents of the CSV file
print(csvFile)

#days_tolls = csvFile.groupby('Date')['Amount'].sum()
#print(days_tolls)

days_tolls = csvFile.groupby(['Transponder', 'Date'])
def print_pd_groupby_test(X, grp=None):
    '''Display contents of a Panda groupby object
    :param X: Pandas groupby object
    :param grp: a list with one or more group names
    # TODO add special handling for sub-groups e.g. when the group key is a tuple
    '''
    def collect_subgroup(key, value):
        return (key[1], 'placeholder')
    if grp is None:
        sub_group = None
        sub_members = {}
        for k,i in X:
            print(type(k))
            if type(k) is tuple:
                print('Tuple found')
                print(k)
                print(type(i))
                if k[0] == sub_group:
                    sub_members[collect_subgroup(k, i)] = i
                else:
                    sub_group = k[0]
                    print_pd_groupby_test(sub_members)
                    sub_members = {}
                    sub_members[collect_subgroup(k, i)] = i
            else:
                print("group:", k)
                print(i)
    else:
        for j in grp:
            print("group:", j)
            print(X.get_group(j))

def print_pd_groupby_original(X, grp=None):
    '''Display contents of a Panda groupby object
    :param X: Pandas groupby object
    :param grp: a list with one or more group names
    '''
    if grp is None:
        for k,i in X:
            print("group:", k)
            print(i)
    else:
        for j in grp:
            print("group:", j)
            print(X.get_group(j))

def print_pd_groupby_with_subs(X):
    '''Display contents of a Panda groupby object
    :param X: Pandas groupby object
    :param grp: a list with one or more group names
    '''
    subgroup = None
    indent_level = 0
    for k,i in X:
        if type(k) is tuple:
            if subgroup == k[0]:
                print(f'    {k[1]}')
                print('    ', end = '')
                for x in i:
                    print(f'    {x}', end="")
                print()
            else:
                subgroup = k[0]
                print(k[0])
                print(f'    {k[1]}')
                print(i)
        else:
            print("group:", k)
            print(i)


print_pd_groupby_with_subs(days_tolls)
