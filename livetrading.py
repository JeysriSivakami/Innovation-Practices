import datetime
import logging
import time
from kiteconnect import KiteConnect
from modules import auth
import csv

def calculate_ma(data):
    if not data:
        return None
    #print(sum(data) / len(data))
    return round((sum(data) / len(data)),2)

def trading_strategy(current_price, ma, kite, token, last_order_price, last_order_placed, bcount,scount, bars):
    #days = 25
    #portfolio = 2000
    stop_loss = 100
    take_profit = 10
    quantity = 1 
    if current_price > ma:
        bcount += 1
        
    else:
        bcount = 0
    logging.basicConfig(level=logging.INFO)
    userdata = auth.get_userdata()
    kite = KiteConnect(api_key=userdata['api_key'])
    kite.set_access_token(userdata['access_token'])
    current_time = datetime.datetime.now()
    if  last_order_placed == "BUY" and current_time.time() >= datetime.time(15, 14):
        logging.info("Time is 3:14 PM, selling stocks...")
        order_id = kite.place_order(
                variety=kite.VARIETY_REGULAR,
                exchange=kite.EXCHANGE_MCX,
                tradingsymbol="SILVER",
                transaction_type=kite.TRANSACTION_TYPE_SELL,
                quantity=1,
                product=kite.PRODUCT_MIS,
                order_type=kite.ORDER_TYPE_MARKET
            )
        last_order_placed = "SELL"

    if bcount >= bars:
        if last_order_placed == "SELL" or last_order_placed is None:
            logging.info("Placing a new BUY Order")
            order_id = kite.place_order(
                    variety=kite.VARIETY_REGULAR,
                    exchange=kite.EXCHANGE_NSE,
                    tradingsymbol="SILVER",
                    transaction_type=kite.TRANSACTION_TYPE_BUY,
                    quantity=1,
                    product=kite.PRODUCT_CNC,
                    order_type=kite.ORDER_TYPE_MARKET
                )
            last_order_placed = "BUY"
            last_order_price = current_price
            print("Stocks are bought")
            print("Price: "+ current_price*quantity)

    elif last_order_placed == "BUY":
        if last_order_price * quantity - current_price * quantity >= stop_loss:
            logging.info("Placing a new Sell Order (Stop Loss Hit)")
            order_id = kite.place_order(
                variety=kite.VARIETY_REGULAR,
                exchange=kite.EXCHANGE_NSE,
                tradingsymbol="SILVER",
                transaction_type=kite.TRANSACTION_TYPE_SELL,
                quantity=1,
                product=kite.PRODUCT_CNC,
                order_type=kite.ORDER_TYPE_MARKET
            )
            last_order_placed = "SELL"
            print("Stocks are sold due to stop loss")
            print("Price: "+ current_price*quantity)
        elif current_price * quantity - last_order_price * quantity >= take_profit:
            logging.info("Placing a new Sell Order (Take Profit Hit)")
            order_id = kite.place_order(
                variety=kite.VARIETY_REGULAR,
                exchange=kite.EXCHANGE_NSE,
                tradingsymbol="SILVER",
                transaction_type=kite.TRANSACTION_TYPE_SELL,
                quantity=1,
                product=kite.PRODUCT_CNC,
                order_type=kite.ORDER_TYPE_MARKET
            )
            last_order_placed = "SELL"
    if current_price < ma:
        scount += 1
        
    else:
        scount = 0

    if scount >= bars and last_order_placed == "BUY":
        logging.info("Placing a new Sell Order")
        order_id = kite.place_order(
                variety=kite.VARIETY_REGULAR,
                exchange=kite.EXCHANGE_NSE,
                tradingsymbol="SILVER",
                transaction_type=kite.TRANSACTION_TYPE_SELL,
                quantity=1,
                product=kite.PRODUCT_CNC,
                order_type=kite.ORDER_TYPE_MARKET
            )
        last_order_placed = "SELL"
        transaction += 1
    
    with open("bscount.csv", 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow([bcount,scount,last_order_price,last_order_placed])
    print("scount",scount)
    print("bcount",bcount)

def strategy(token):
    logging.basicConfig(level=logging.INFO)

    userdata = auth.get_userdata()
    kite = KiteConnect(api_key=userdata['api_key'])
    kite.set_access_token(userdata['access_token'])
    bars = 10 
        
    while True:
        current_time = datetime.datetime.now()

        if current_time.time() >= datetime.time(9, 15) and current_time.time() <= datetime.time(15, 15):
            minutes = 25*30
            with open('bscount.csv', 'r') as file:
                reader = csv.reader(file)
                row = next(reader)
                bcount = int(row[0])
                scount= int(row[1])
                last_order_price = row[2]
                last_order_placed = row[3]
            start_time = current_time - datetime.timedelta(minutes=minutes)
            historical_data = kite.historical_data(token, start_time, current_time, "30minute")
            if historical_data:
                #print('first record:', historical_data[0])
                #or record in historical_data:
                    #print(record)

                # Extract closing prices for the past minute
                minute_closes = [record['close'] for record in historical_data]
                #print(minute_closes)

                # Calculate moving average for the past minute
                ma = calculate_ma(minute_closes)

                # Execute trading strategy every one minute
                last_price = historical_data[-1]['close']  # Get the latest price for the current minute
                trading_strategy(last_price, ma, kite, token, last_order_price, last_order_placed, bcount, scount, bars)
                # Wait for the next minute
            minutes=30
            next_time = current_time + datetime.timedelta(minutes=minutes)
            time_to_wait = next_time - datetime.datetime.now()
            time_to_wait_seconds = time_to_wait.total_seconds()
            if time_to_wait_seconds > 0:
                logging.info(f"Waiting for next minute: {time_to_wait_seconds} seconds")
                time.sleep(time_to_wait_seconds)
        else:
            # Outside market hours
            logging.info("Market is closed...")
            break

def start():
    

    token = 2048769

    # Start live trading
    strategy( token)

start()
