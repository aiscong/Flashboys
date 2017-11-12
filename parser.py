import numpy as np
import pandas as pd
import datetime
import urllib
import matplotlib.pyplot as plt
import os


class Parser:
    LINK = 'https://finance.google.com/finance/getprices?i=60&q=NUGT&p=15d&f=d,o,h,l,c,v'

    @staticmethod
    def main():
        raw_data = np.array(pd.read_csv(Parser.LINK, skiprows=7, header=None))
        stocklist = np.array(pd.read_csv('StockList.csv', header=None))
        print stocklist
        print '======='
        fixed_data = Parser.dataIntegrityCheck(raw_data)
        formatted_data = Parser.constructDataFrameWithTimestamp(
            fixed_data, Parser.getTimezoneOffset(Parser.LINK))
        arr = os.listdir('.')
        formatted_data.to_csv("data", encoding='utf-8')
        print formatted_data.iloc[:380].tail()
        new_pd = pd.read_csv("data", index_col=[0])
        print '====='
        print new_pd.iloc[:380].tail()
        print '====='

    @staticmethod
    def constructDataFrameWithTimestamp(data, timezone_offset):
        dates = []
        current_date = None
        num_min = 0
        last_min = 0
        for i in range(0, len(data)):
            raw_time = data[i][0]
            if raw_time[0] == 'a':
                current_date = datetime.datetime.fromtimestamp(
                    int(raw_time.replace('a', '')) - timezone_offset)
                dates.append(current_date)
            else:
                dates.append(current_date +
                             datetime.timedelta(minutes=int(raw_time)))

        formatted_data = pd.DataFrame(data, index=dates)
        formatted_data.columns = ['RawTime',
                                  'Open',
                                  'High',
                                  'Low',
                                  'Close',
                                  'Vol']
        del formatted_data['RawTime']
        return formatted_data

    @staticmethod
    def getTimezoneOffset(link):
        timezone_offset = (int(urllib.urlopen(link).readlines()[
                           6].split('=')[1]) + 60) * 60
        return timezone_offset

    @staticmethod
    def dataIntegrityCheck(raw_data):
        i = 0
        while i < len(raw_data):
            raw_time = raw_data[i][0]
            if raw_time[0] == 'a':
                last_min = 0
            elif int(raw_time) - last_min == 1:
                last_min = int(raw_time)
            else:
                raw_data = Parser.fixMissingData(raw_data, i - 1)
                i -= 1
            i += 1

        return raw_data

    @staticmethod
    def fixMissingData(raw_data, gap_start_row):
        missing_time = int(raw_data[gap_start_row][0]) + 1
        filler_row = [str(missing_time)]
        for i in range(1, len(raw_data[gap_start_row])):
            filler_row.append(
                (float(raw_data[gap_start_row][i]) + float(raw_data[gap_start_row + 1][i])) / 2)
            if i == len(raw_data[gap_start_row]) - 1:
                filler_row[i] = int(filler_row[i])

        return np.insert(raw_data, gap_start_row + 1, np.array(filler_row, dtype=object), 0)


if __name__ == '__main__':
    Parser.main()
