# test independence example

import pandas as pd


def split_names(df):
    df['firstname'] = df['name'].apply(lambda x: x.split()[0])
    df['lastname'] = df['name'].apply(lambda x: x.split()[1])

def get_initials(df):
    df['initials'] = df['firstname'].str[0] + df['lastname'].str[0]

people_df = pd.DataFrame({'name': ['Alice Smith', 'Bob Howard', 'Charlie Ashe']}) 

def test_split_names():
    split_names(people_df)
    assert people_df['firstname'].tolist() == ['Alice', 'Bob', 'Charlie']
    assert people_df['lastname'].tolist() == ['Smith', 'Howard', 'Ashe']

def test_get_initials():
    get_initials(people_df)
    assert people_df['initials'].tolist() == ['AS', 'BH', 'CA']


def get_people_df():
    return pd.DataFrame({'name': ['Alice Smith', 'Bob Howard', 'Charlie Ashe']}) 

def test_split_names_fullsetup():
    local_people_df = get_people_df()
    split_names(local_people_df)
    assert local_people_df['firstname'].tolist() == ['Alice', 'Bob', 'Charlie']
    assert local_people_df['lastname'].tolist() == ['Smith', 'Howard', 'Ashe']

def test_get_initials_fullsetup():
    local_people_df = get_people_df()
    split_names(local_people_df)
    get_initials(local_people_df)
    assert local_people_df['initials'].tolist() == ['AS', 'BH', 'CA']
