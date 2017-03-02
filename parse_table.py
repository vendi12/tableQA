#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on Mar 2, 2017

.. codeauthor: svitlana vakulenko
    <svitlana.vakulenko@gmail.com>

'''
import unittest

import os
import pandas as pd
import numpy as np
import re
import random


PATH = './data/'
SAMPLE_TABLE = 'OOE_Wanderungen_Zeitreihe.csv'
TABLE_DATA = './data/table_data.txt'

QUESTION_TEMPLATE = 'What is the {} for {}?\t{}\t{}'
# QUESTION_TEMPLATE = 'What is the {} in {}?\t{}\t{}'

def tokenize(sent):
    '''Return the tokens of a sentence including punctuation.

    >>> tokenize('Bob dropped the apple. Where is the apple?')
    ['Bob', 'dropped', 'the', 'apple', '.', 'Where', 'is', 'the', 'apple', '?']
    '''
    return [x.strip() for x in re.split('(\W+)?', sent) if x.strip()]


def read_tables(fps, delimiter, shuffle=False, limit=False):
    '''
    Input:
    fps <list of strings>  full paths to files to read tables from

    Output:
    tables <dict> {file_path: rows_generator}
    '''
    tables = {}
    for path in fps:
        df = pd.read_csv(path, sep=delimiter)
        if shuffle:
            df_shuffled = df.iloc[np.random.permutation(len(df))]
            df_shuffled.reset_index(drop=True)
            df = df_shuffled
        if limit:
            df = df[:limit]
        tables[path] = df
    return tables


def collect_tables(files):
    # collect file paths
    fps = []
    for file in files:
        fps.append(os.path.join(PATH, file))
    print fps
    return read_tables(fps, delimiter=';')


def profile_table(table):
    columns = table.columns
    print len(table), 'rows'
    print len(columns), 'columns'
    print 'Header:', columns.values
    distribution = [len(set(table[c])) for c in table]
    print 'Number of unique values:', distribution
    print 'Mean:', np.mean(distribution)
    print 'Unique values:', [list(set(table[c]))[:5] for c in table]
    types = [type(list(set(table[c]))[0]) for c in table]
    print 'Column types:', types
    string_columns = [idx for idx, c in enumerate(table) if isinstance(list(set(table[c]))[0], str)]
    # categorical fields
    print 'String columns:', string_columns
    # exclude non-discriminative columns
    return [idx for idx in string_columns if distribution[idx] > 1]
    # print [len(set(c)) for c in columns]
    # find the column with distinct categorical values to use for question generation
    # TODO find string columns
    # value distributions in columns, e.g. number of unique values


class TableParser():
    '''
    size <int> regulates the size of the table chunks between QAs
    '''

    def __init__(self, size=2):
        self.size = size
        self.count = 0
        self.qs = []

    def generate_data(self, table, out_path=TABLE_DATA):
        with open(out_path, 'w') as self.out_file:
            self.columns = table.columns.values
            cat_columns = profile_table(table)
            print cat_columns
            self.rows = []
            for row in table.itertuples():
                self.count += 1
                # data_string = str(row[0]+1) + ' '
                data_string = str(self.count) + ' '
                # print row
                values = []
                for idx, value in enumerate(row[1:]):
                    values.append(str(self.columns[idx]) + ' : ' + str(value))
                data_string += ', '.join(values) + ' .\n'
                self.out_file.write(data_string)
                self.rows.append(row)
                # write random qa after every 2nd sample
                if self.count % self.size == 0:
                    # generate qa 
                    self.generate_qa(cat_columns[0])


    def generate_qa(self, cat):
        # print row
        # pick row at random
        s = random.randrange(0, len(self.rows))
        # make sure the values are different for the q field across columns
        # print columns
        q = random.randrange(1, len(self.columns))
        # skip
        if q == cat:
            return
        q_string = QUESTION_TEMPLATE.format(self.columns[q], self.rows[s][cat+1],
                                            self.rows[s][q+1],  s+1)
        self.count += 1
        self.out_file.write(str(self.count) + ' ' + q_string + '\n')
        # reset table
        self.count = 0
        self.rows = []

        # print columns[q], row[q]

# def generate_qa(data_path):
#     with open(data_path) as f:
#         for line in f.readlines():
#             line = line.decode('utf-8').strip()
#             sent = tokenize(line)
#             print sent


# def test_generate_qa():
#     # data = get_tables(TABLE_DATA)
#     # print data
#     generate_qa(TABLE_DATA)


def test_generate_data():
    tables = collect_tables([SAMPLE_TABLE])
    for path, table in tables.items():
        print path
        tp = TableParser()
        tp.generate_data(table)


class TestTableParser(unittest.TestCase):
    def test_collect_tables(self):
        tables = collect_tables([SAMPLE_TABLE])
        for path, table in tables.items():
            print path
            print table.columns.values

    def test_profile_table():
        tables = collect_tables([SAMPLE_TABLE])
        for path, table in tables.items():
            print path
            profile_table(table)


if __name__ == '__main__':
    # unittest.main()
    test_generate_data()
    # test_generate_qa()
    # test_profile_table()
