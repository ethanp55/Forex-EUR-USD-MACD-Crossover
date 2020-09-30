import pandas as pd
import numpy as np
import talib
from datetime import datetime, timedelta
from Oanda.Services.data_downloader import DataDownloader
import pytz as tz


class CurrentDataSequence:
    def __init__(self):
        self.current_sequence = pd.read_csv('Data/Files/current_sequence.csv')
        self.min_sequence_length = 1000

    def update_current_data_sequence(self):
        curr_date = datetime.now()
        d = datetime(curr_date.year, 3, 8)
        dston = d + timedelta(days=6-d.weekday())
        d = datetime(curr_date.year, 11, 1)
        dstoff = d + timedelta(days=6 - d.weekday())

        if dston <= curr_date.replace(tzinfo=None) < dstoff:
            hours = 2

        else:
            hours = 1

        current_time = (datetime.now(tz=tz.timezone('America/New_York')).replace(microsecond=0, second=0, minute=0) - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
        current_time = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')

        from_time = str(current_time - timedelta(hours=self.min_sequence_length))
        to_time = str(current_time)

        data_downloader = DataDownloader()
        candles, error_message = data_downloader.get_historical_data('EUR_USD', ['bid', 'ask'], 'H1', from_time, to_time)

        if error_message is not None:
            print(error_message)
            return False

        np_data = []

        for candle in candles:
            curr_date = candle.time
            curr_date = datetime.utcfromtimestamp(int(float(curr_date))).strftime('%Y-%m-%d %H:%M:%S')
            row = [curr_date, float(candle.bid.o), float(candle.bid.h), float(candle.bid.l), float(candle.bid.c), float(candle.ask.o), float(candle.ask.h), float(candle.ask.l), float(candle.ask.c)]
            np_data.append(row)

        np_data = np.array(np_data)
        self.current_sequence = pd.DataFrame(np_data, columns=['Date', 'Bid_Open', 'Bid_High', 'Bid_Low', 'Bid_Close', 'Ask_Open', 'Ask_High', 'Ask_Low', 'Ask_Close'])
        self.current_sequence['macd'], self.current_sequence['macdsignal'], self.current_sequence['macdhist'] = talib.MACD(self.current_sequence['Bid_Close'])
        self.current_sequence['ema200'] = talib.EMA(self.current_sequence['Bid_Close'], timeperiod=200)
        self.current_sequence.dropna(inplace=True)
        self.current_sequence.reset_index(drop=True, inplace=True)

        if self.current_sequence.shape[0] < 200:
            print('Current sequence length is too small: ' + str(self.current_sequence.shape[0]))
            return False

        self.current_sequence.to_csv('Data/Files/current_sequence.csv', index=False)

        return True
