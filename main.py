import re
from turtle import color

import numpy as np
import pandas as pd
import os
import requests
import sys
import matplotlib.pyplot as plt


if __name__ == '__main__':
    if not os.path.exists('../Data'):
        os.mkdir('../Data')

    # Download data if it is unavailable.
    if 'Nobel_laureates.json' not in os.listdir('../Data'):
        sys.stderr.write("[INFO] Dataset is loading.\n")
        url = "https://www.dropbox.com/s/m6ld4vaq2sz3ovd/nobel_laureates.json?dl=1"
        r = requests.get(url, allow_redirects=True)
        open('../Data/Nobel_laureates.json', 'wb').write(r.content)
        sys.stderr.write("[INFO] Loaded.\n")

    #Stage 1/6: Load the data
    initial_data = pd.read_json(r"C:\Users\User\PycharmProjects\Nobel Laureates\Nobel Laureates\Data\Nobel_laureates.json")
    # print(initial_data.info())
    # print(initial_data.shape)
    # print(f'Duplicated columns? -> {bool(initial_data.duplicated().sum())}')
    # print(f'{bool(initial_data.duplicated().sum())}')

    #Remove rows with values missing in 'gender' column
    initial_data.dropna(axis=0, subset='gender', inplace=True)

    #Set new index values
    new_index = pd.Series([x for x in range(initial_data.shape[0])])
    initial_data.set_index(new_index, drop=True, inplace=True)
    # print(initial_data[['country', 'name']].head(20).to_dict())
    # print(initial_data.describe())

    #Stage 2/6: Correct the birthplaces

    #Function extracting country name from 'place_of_birth' column
    def get_country(row):
        try:
            el_list = row.split(',')
        except AttributeError:
            return None

        if len(el_list) > 1:
            if el_list[-1].strip() in ['US', 'United States', 'U.S.']:
                return 'USA'
            elif el_list[-1].strip() in ['United Kingdom']:
                return 'UK'
            else:
                return el_list[-1].strip()
        else:
            return None

    #New Series of country names
    country_of_birth = initial_data['place_of_birth'].apply(get_country)

    #Replace missing values with None, then with values from 'country_of_birth'
    initial_data['born_in'].replace('', None, inplace=True)
    initial_data['born_in'].fillna(country_of_birth, inplace=True)

    #Remove rows with values missing in 'born_in' column
    initial_data.dropna(axis=0, subset='born_in', inplace=True)

    #Apply uniform country acronyms for USA and UK
    initial_data['born_in'] = initial_data['born_in'].apply(lambda x: 'USA' if x in ['US', 'United States', 'U.S.'] else x)
    initial_data['born_in'] = initial_data['born_in'].apply(lambda x: 'UK' if x in ['United Kingdom'] else x)

    #Set new index values
    new_index = pd.Series([x for x in range(initial_data.shape[0])])
    initial_data.set_index(new_index, drop=True, inplace=True)
    # print(initial_data['born_in'].to_list())

    #Stage 3/6: Correct the dates

    #function extracting year from 'date_of_birth'
    def year_of_birth(row):
        pattern = '[0-9]{4}'
        return int(re.search(pattern, row)[0])

    #Creation of new columns
    initial_data['year_born'] = initial_data['date_of_birth'].apply(year_of_birth)
    initial_data['age_of_winning'] = initial_data['year'] - initial_data['year_born']

    #Stage 4/6: Plot a pie chart
    def auto_pct_val(pct):
        total = sum(country_regrouped.to_list())
        val = int(round(pct*total/100))
        return '{p:.2f}%\n({v:d})'.format(p=pct, v=val)

    country_group = initial_data['born_in'].value_counts()
    country_other = country_group.loc[country_group < 25]
    country_regrouped = country_group.loc[country_group >= 25]
    country_regrouped['Other countries'] = country_other.sum()
    country_regrouped.sort_values(ascending=False, inplace=True)
    # print(country_regrouped.to_list())

    colors = ['blue', 'orange', 'red', 'yellow', 'green', 'pink', 'brown', 'cyan', 'purple']
    explode = [0, 0, 0, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08]
    labels = country_regrouped.index.to_list()
    plt.figure(figsize=(12, 12))
    plt.pie(country_regrouped, colors=colors, explode=explode, autopct=lambda pct: auto_pct_val(pct), labels=labels)
    plt.show()

    #Stage 5/6: Plot a bar plot

    #New subset of initial data
    mf_category = initial_data[['category', 'gender']]

    #Drop rows with missing 'category' values
    mf_category = mf_category['category'].replace('', np.nan)
    mf_category = pd.DataFrame(mf_category).join(initial_data['gender'])
    mf_category['gender'] = initial_data['gender']

    mf_category.dropna(axis=0, inplace=True)
    mf_category.reset_index(inplace=True, drop=True)

    #Create new subset containing the count of Nobel prizes per category for each gender
    label_order = ['Chemistry', 'Economics', 'Literature', 'Peace', 'Physics', 'Physiology or Medicine']
    m_category = mf_category.loc[mf_category['gender'] == 'male'].value_counts()
    f_category = mf_category.loc[mf_category['gender'] == 'female'].value_counts()
    m_category = m_category.reset_index()
    f_category = f_category.reset_index()
    m_category.drop(labels='gender', axis=1, inplace=True)
    f_category.drop(labels='gender', axis=1, inplace=True)
    m_category.set_index('category', inplace=True)
    f_category.set_index('category', inplace=True)
    m_category = m_category.reindex(labels=label_order)
    f_category = f_category.reindex(labels=label_order)
    val_m_category = m_category['count'].to_list()
    val_f_category = f_category['count'].to_list()

    #Create bar plot
    x_axis = np.arange(len(label_order))
    plt.figure(figsize=(10, 10))
    plt.bar(x_axis - 0.2, val_m_category, width=0.4, label='Males', color='blue')
    plt.bar(x_axis + 0.2, val_f_category, width=0.4, label='Females', color='crimson')
    plt.xticks(x_axis, label_order)
    plt.ylabel('Nobel Laureates Count', fontsize=14)
    plt.xlabel('Category', fontsize=14)
    plt.title('The total count of male and female Nobel Prize winners by categories', fontsize=20)
    plt.legend()
    plt.show()

    #Stage 6/6: Plot a box plot

    #Create a dictionary containing winning ages for each category
    age_by_category = {}
    for i in label_order:
        age_by_category[i.lower().replace(' ', '_')] = initial_data['age_of_winning'].loc[initial_data['category'] == i].to_list()
    age_by_category['all_categories'] = initial_data['age_of_winning'].to_list()

    #Create a boxplot for winning age distribution per category
    plt.figure(figsize=(10, 10))
    data = [x for x in age_by_category.values()]
    plt.boxplot(data, labels=label_order+['All categories'], showmeans=True)
    plt.ylabel('Age of obtaining the Nobel Prize', fontsize=14)
    plt.xlabel('Category', fontsize=14)
    plt.title('Distribution of Ages by Category', fontsize=20)
    plt.show()


