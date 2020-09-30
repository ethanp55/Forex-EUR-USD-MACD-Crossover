from datetime import datetime, timedelta
import time
from Data.current_data_sequence import CurrentDataSequence
from Oanda.Services.order_handler import OrderHandler
from Oanda.Services.data_downloader import DataDownloader
from Model.macd_crossover import MACDCrossover


def main():
    weekend_day_nums = [4, 5, 6]
    pips_to_risk = 30 / 10000
    n_units_per_trade = 10000
    percent_taken_after_cleared_risk = 0.25
    gain_risk_ratio = 1.5
    current_data_sequence = CurrentDataSequence()
    order_handler = OrderHandler(pips_to_risk)
    data_downloader = DataDownloader()

    open_trades, error_message = order_handler.get_open_trades()

    if error_message is not None:
        print('Error in getting open trades:\n' + error_message)
        return

    else:
        order_in_place = len(open_trades) > 0

    print('Starting new session; session started with open trades: ' + str(order_in_place))

    while True:
        utc_now = datetime.utcnow().replace(microsecond=0, minute=0, second=0)

        if utc_now.weekday() in weekend_day_nums:
            if (utc_now.weekday() == 4 and utc_now.hour >= 20) or (utc_now.weekday() == 6 and utc_now.hour <= 21) or utc_now.weekday() == 5:
                print('Weekend hours, need to wait until market opens again.')

                while True:
                    new_utc_now = datetime.utcnow().replace(microsecond=0, minute=0, second=0)

                    if new_utc_now.weekday() == 6 and new_utc_now.hour > 20:
                        break

        dt = datetime.now().replace(microsecond=0, minute=0, second=0) + timedelta(hours=1)
        print(dt)

        if not order_in_place:
            current_data_update_success = current_data_sequence.update_current_data_sequence()

            if not current_data_update_success:
                print('Error in current data sequence')
                return

            data_sequence = current_data_sequence.current_sequence

            pred = MACDCrossover.determine_trade(data_sequence)

            if pred is not None:
                print('\n---------------------------------')
                print('------- PLACING NEW ORDER -------')
                print('---------------------------------\n')

                candles, error_message = data_downloader.get_current_data('EUR_USD', ['bid', 'ask'], 'H1')

                if error_message is not None:
                    print(error_message)
                    return

                else:
                    last_candle = candles[-1]
                    curr_bid_open = last_candle.bid.o
                    curr_ask_open = last_candle.ask.o

                if pred == 'buy':
                    small_profit_price = curr_ask_open + pips_to_risk
                    profit_price = curr_ask_open + (gain_risk_ratio * pips_to_risk)

                else:
                    small_profit_price = curr_bid_open - pips_to_risk
                    profit_price = curr_bid_open - (gain_risk_ratio * pips_to_risk)

                order_handler.place_market_order(pred, int(n_units_per_trade * percent_taken_after_cleared_risk), small_profit_price, False)
                order_handler.place_market_order(pred, int(n_units_per_trade * (1 - percent_taken_after_cleared_risk)), profit_price, True)

                # Give Oanda a few seconds to place the order
                time.sleep(15)

                open_trades, error_message = order_handler.get_open_trades()

                if error_message is None and len(open_trades) > 0:
                    order_in_place = True
                    print('Placed new order: ' + str(pred) + ' -- Num orders: ' + str(len(open_trades)))

                else:
                    print('Error in placing trades')

                    if error_message is not None:
                        print(error_message)

                    return
        else:
            open_trades, error_message = order_handler.get_open_trades()

            if error_message is not None:
                print('Error in getting open trades:\n' + error_message)
                return

            print('Number of open trades: ' + str(len(open_trades)))

            if len(open_trades) == 0:
                order_in_place = False
                continue

        while datetime.now() < dt:
            time.sleep(1)


if __name__ == "__main__":
    main()
