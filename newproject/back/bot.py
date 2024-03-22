from datetime import datetime, timedelta, time
from binance.client import Client
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import json
import schedule
import logging 
import mysql.connector
import time as tm
import logging
Format = '%(asctime)s-%(message)s'
logging.basicConfig(level=logging.INFO,format=Format)
class HistoricalData:
   
    @staticmethod
    def update_daily():
        today_date = datetime.today().date()
        midnight = time(0, 0, 0)
        start_date = datetime.combine(today_date - timedelta(days=1000), midnight)
        end_date = datetime.combine(today_date, midnight)
        logging.info(f'     start_date = {start_date}')
        start_timestamp = int(start_date.timestamp() * 1000)
        end_timestamp = int(end_date.timestamp() * 1000)
        symbol = 'BTCUSDT'
        interval = '1d'
  
        df = HistoricalData.getting_Binance_data(symbol, interval, start_timestamp, end_timestamp)
        HistoricalData.plot_moving(df)
       
    
    # Create API endpoint
    @staticmethod
    def getting_Binance_data(symbol, interval, start, end):  # Added 'start' and 'end' parameters
        endpoint = 'https://api.binance.com/api/v3/klines'
        limit = 1000
        request_params = {'symbol': symbol, 'interval': interval, 'startTime': start, 'endTime': end, 'limit': limit}
        df = pd.DataFrame(json.loads(requests.get(endpoint, params=request_params).text))
        df = df.iloc[:, 0:6]
        df.columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
        df.index = [datetime.fromtimestamp(x / 1000.0) for x in df.Date]
        
        df["Close"] = pd.to_numeric(df["Close"], errors='coerce')
        
        df["Lag Price"] =df["Close"].shift(1)
        df["MA20"]=df["Lag Price"].rolling(20) .mean()
        df["MA100"] =df["Lag Price"].rolling(100) .mean()
        df.dropna(inplace=True)  # Added 'inplace=True' to drop NaN values from DataFrame
        df["lag_ma20"]= df["MA20"].shift(1)
        df["lag_ma100"]= df["MA100"].shift(1)
        df.dropna(inplace=True)  # Added 'inplace=True' to drop NaN values from DataFrame
        return df
        
    @staticmethod
    def plot_moving(df): 
        """plt.rcParams['figure.figsize']=(15,9)
        df["MA20"].plot(label="MA20",color='red')
        df["MA100"].plot(label="MA100",color='blue')
        df["Close"].plot(label="Close_price",color='black')
        plt.legend()
        plt.show()"""
        
        HistoricalData.condition(df)
        
    @staticmethod  
    def condition(df):               
        # Logic of moving average
        condition =[ (df["MA20"]>df["MA100"]),(df["MA20"]<=df["MA100"])]
    
        decision =[1,-1]
        df["Decision"]= np.select(condition,decision,default=0)
        df["Shift"] = df["Decision"].shift(1)
        df["Change Price"]=df["Close"].diff(1)
        df["profit"]= df["Close"].diff(1)*df["Shift"]/df["Close"]
        df["Cum_profit"] = df["profit"].cumsum()
        df.dropna(inplace=True)  # Added 'inplace=True' to drop NaN values from DataFrame
        df.tail()
        HistoricalData.cumulative(df)
     
    @staticmethod
    def cumulative(df):  
        # Plotting graph
        # df["Cum_profit"].plot(label="Cum_profit", color='red')
        # plt.locator_params(axis='x', nbins=7)
        # plt.legend()
        # plt.show()
        
        Last_Cum_Profit = df["Cum_profit"].iloc[-1]
        Last_day_decision = df["Decision"].iloc[-1]
        logging.info(f'     Last_Cum_Profit = {Last_Cum_Profit}')
        logging.info(f'     Today Profit/Loss = {df["profit"].iloc[-1]}')
        logging.info(f'     Today Open Price = {df["Open"].iloc[-1]} ')
        logging.info(f'     Today Close Price = {df["Close"].iloc[-1]}')
        
        instance_x = shedule_Orders() 
        instance_x.calling_for_trade(Last_day_decision)
        
        
       #return df
class API:
        api_key = "b6ba865a8a866e27a29769183953ae47762ea98861118d3e67c0ea0f52f04488"
        secret_key = "af692e426d8f9a27a83c7daeea25a81da4270e22bb8337eb7e858488738babd3"
        client = Client(api_key = api_key, api_secret = secret_key, tld = "com", testnet = True)
    

class shedule_Orders:
    
    usdt_balance_before =0
    usdt_balance_after = 0
    ROI =0
    entry_price=0
    marketPrice =0
    orderId =0
    unRealizedProfit=0
    profit =0
    size=0
    symbol ="BTCUSDT"
    leverage = 0
    coin = None
    closeTime = None
    openTime = None
    def calling_for_trade(self,Last_day_decision):
        logging.info(f'     from history data Desicion = {"Buy" if Last_day_decision == 1 else "Sell"} ')
        
        shedule_Orders.leverage = 10
        shedule_Orders.size = 0.002
        shedule_Orders.coin = "BTC"
        client = API.client
        client.futures_change_leverage(symbol =shedule_Orders.symbol , leverage = shedule_Orders.leverage)
        shedule_Orders.balance_before(client)
        database_connector.retrive_data("pass")
        
        
        if(Last_day_decision==1 and database_connector.retrive_data("pass")==1  ):
            #schedule.every(5).seconds.do(open_trade_buy)
            #schedule.every(5).seconds.do(close_trade_buy)
            shedule_Orders.open_trade_buy(client,shedule_Orders.size)
            
            shedule_Orders.SL_TP(client,shedule_Orders.symbol,Last_day_decision)
            
        if (Last_day_decision==-1 and  database_connector.retrive_data("pass")==1):
            shedule_Orders.open_trade_sell(client,shedule_Orders.size)
            shedule_Orders.SL_TP(client,shedule_Orders.symbol,Last_day_decision)
        if((Last_day_decision==1 or Last_day_decision==-1)and database_connector.retrive_data("pass")==0):
            logging.info(f'     One Trade is running')
            
    #stopLoss/ TakeProfit
    def SL_TP(client,symbol,Last_day_decision):

        if(Last_day_decision==1 ):
                tp = 1.3*shedule_Orders.entry_price#1.75
                sl = 0.85*shedule_Orders.entry_price#0.75
                tp = round(tp, 2)
                sl = round(sl, 2)
                stop_loss =client.futures_create_order(symbol = symbol, side = "SELL",type = "STOP_MARKET", stopPrice=sl, closePosition= 'true')
                Take_Profit = client.futures_create_order(symbol = "BTCUSDT", side = "SELL",type = "TAKE_PROFIT_MARKET", stopPrice=tp, closePosition= 'true')
        
        if(Last_day_decision==-1 ):
                tp = 0.75*shedule_Orders.entry_price#0.75
                sl = 1.20*shedule_Orders.entry_price#1.25
                tp = round(tp, 2)
                sl = round(sl, 2)
                stop_loss =client.futures_create_order(symbol = symbol, side = "BUY",type = "STOP_MARKET", stopPrice=sl, closePosition= 'true')
                Take_Profit = client.futures_create_order(symbol = "BTCUSDT", side = "BUY",type = "TAKE_PROFIT_MARKET", stopPrice=tp, closePosition= 'true')
            

        isTrading = True
        while isTrading:
            positions = client.futures_position_information()
            for i in positions: 
                if i['symbol'] ==symbol :
                    if float(i['positionAmt']) == 0 and float(i['entryPrice']) == 0 and float(i['breakEvenPrice']) == 0:
                        if(Last_day_decision ==1):
                            client.futures_cancel_all_open_orders(symbol=symbol)
                            shedule_Orders.close_trade_buy(client)
                            
                        if(Last_day_decision ==-1):
                            client.futures_cancel_all_open_orders(symbol=symbol)
                            shedule_Orders.close_trade_sell(client)
                            
                        
                        isTrading = False
                    
                    else:
                        tm.sleep(1)
                        #print("price = ",i['markPrice'])
                        
                    break
            
            
            #profitMargin>=75 or profitMargin<=-25
            
            
                #logging.info(f'     profitMargin = {profitMargin}')
            
     
    #Get balance
    
                
    def order_history(client,symbol,orderId,openOrClose):
        trade_details = client.futures_account_trades(symbol =symbol)
        for i in trade_details:
            #print(i)
            if((i['orderId'])==(orderId)):
                if(openOrClose=="close"):
                    shedule_Orders.marketPrice =float(i['price'])
                    logging.info(f'     Market Price    =      {shedule_Orders.marketPrice}  ')
                    shedule_Orders.unRealizedProfit = float(i['realizedPnl'])
                    shedule_Orders.ROI = round(((shedule_Orders.marketPrice - shedule_Orders.entry_price) / shedule_Orders.entry_price) * 100*shedule_Orders.leverage, 2)
                    break
                if(openOrClose=="open"):
                
                    shedule_Orders.entry_price =float(i['price'])
                                        
                break      
              
    
    def balance_before (client):
        account_info=client.futures_account()
        
        for asset in account_info['assets']:
            if asset['asset'] == 'USDT':
                shedule_Orders.usdt_balance_before = float(asset['marginBalance'])
                break

        if shedule_Orders.usdt_balance_before is not None:
            for i in range(1,5):
                print(" ")
            print("LIVE MARKET TRADING")
            print(" ")
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print(" ")
            
            
        else:
            logging.info(f'     USDT balance not found')
    
    
    def balance_after_PNL(client):
        positions = client.futures_position_information()
        account_info=client.futures_account()
        shedule_Orders.usdt_balance_after = None
        for asset in account_info['assets']:
            if asset['asset'] == 'USDT':
                shedule_Orders.usdt_balance_after = float(asset['marginBalance'])
                break

        if shedule_Orders.usdt_balance_after is not None:
            logging.info(f'     Before trading USDT balance: {shedule_Orders.usdt_balance_before}')
            logging.info(f'     After trading USDT balance: {shedule_Orders.usdt_balance_after}')
            
        else:
            logging.info(f'     USDT balance not found')
        shedule_Orders.profit =(shedule_Orders.usdt_balance_after -shedule_Orders.usdt_balance_before )
        
        
        
        logging.info(f'     profit USDT     =   {shedule_Orders.profit}')
        logging.info(f'     Size            =   {shedule_Orders.size} ')
        logging.info(f'     Leverage        =   {shedule_Orders.leverage} ')
        logging.info(f'     Coin            =   {shedule_Orders.coin}')
        logging.info(f'     Entry Price     =   {shedule_Orders.entry_price} ')
        logging.info(f'     Market Price    =   {shedule_Orders.marketPrice}')
        logging.info(f'     Unrealize Profit=   {shedule_Orders.unRealizedProfit}' )
        logging.info(f'     ROI %           =   {shedule_Orders.ROI}' )
        logging.info(f'     Open Time       =   {shedule_Orders.openTime}' )
        print(" ")
        print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        
        database_connector.insert_data(shedule_Orders.orderId ,shedule_Orders.openTime,shedule_Orders.closeTime,shedule_Orders.size,shedule_Orders.coin,shedule_Orders.symbol,shedule_Orders.leverage,
shedule_Orders.usdt_balance_after,shedule_Orders.entry_price,shedule_Orders.marketPrice,shedule_Orders.unRealizedProfit,shedule_Orders.ROI) 

           
    
    #Buy trade          
    
    def open_trade_buy(client,size):
        
        logging.info(f'     Buy Trade was opened')
        order_open = client.futures_create_order(symbol = "BTCUSDT", side = "BUY",type = "MARKET", quantity = size)
        order_open
        shedule_Orders.openTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        database_connector.retrive_data("open")
        shedule_Orders.orderId = order_open['orderId']
        shedule_Orders.order_history(client,shedule_Orders.symbol,shedule_Orders.orderId,"open")
        
        
        
        


    def close_trade_buy(client):
        #import time
        #change the time or logic
        #time.sleep(5)
        logging.info(f'     Buy Trade was closed')
        trade_details = client.futures_account_trades(symbol =shedule_Orders.symbol)
        
        #order_close = client.futures_create_order(symbol = "BTCUSDT", side = "SELL",type = "MARKET", quantity = size, reduce_Only = True)
        #order_close
        shedule_Orders.orderId = trade_details[-1]['orderId'] 
        shedule_Orders.closeTime =  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        shedule_Orders.order_history(client,shedule_Orders.symbol,shedule_Orders.orderId,"close" )
        shedule_Orders.balance_after_PNL(client)
        database_connector.retrive_data("close")
        
        
        
    #Sell trade
    def open_trade_sell(client,size):
        logging.info(f'     Sell Trade was opened')
        order_open = client.futures_create_order(symbol = "BTCUSDT", side = "SELL",type = "MARKET", quantity = size, reduce_Only = True)
        order_open 
        shedule_Orders.openTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        database_connector.retrive_data("open")
        shedule_Orders.orderId = order_open['orderId']
        shedule_Orders.order_history(client,shedule_Orders.symbol,shedule_Orders.orderId,"open")
        

    def close_trade_sell(client):
        #import time
        #change the time or logic
        #time.sleep(5)
        logging.info(f'     Sell Trade was closed')
        #order_close = client.futures_create_order(symbol = "BTCUSDT", side = "BUY",type = "MARKET", quantity = size)
        #order_close
        trade_details = client.futures_account_trades(symbol =shedule_Orders.symbol)
        
        #order_close = client.futures_create_order(symbol = "BTCUSDT", side = "SELL",type = "MARKET", quantity = size, reduce_Only = True)
        #order_close
        shedule_Orders.orderId = trade_details[-1]['orderId'] 
        shedule_Orders.closeTime =  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        shedule_Orders.order_history(client,shedule_Orders.symbol,shedule_Orders.orderId,"close" )
        shedule_Orders.balance_after_PNL(client)
        database_connector.retrive_data("close")

class database_connector:
    #variable_value =1
    
    def insert_data(OrderId,openTime, closeTime, size, coin, symbol, leverage, balance, entryPrice, marketPrice, unRealizedProfit, ROI):
        try:  
            mydb = mysql.connector.connect(host="localhost", user="root", password="ABCDEf45@",database="binance")
            mycursor = mydb.cursor()
            sql = "INSERT INTO profit (OrderId,openTime, closeTime, size, coin, symbol, leverage, balance, entryPrice, marketPrice, unRealizedProfit, ROI ) VALUES (%s,%s,%s, %s, %s,%s,%s, %s, %s,%s, %s, %s)"
            val = (OrderId,openTime, closeTime, size, coin, symbol, leverage, balance, entryPrice, marketPrice, unRealizedProfit, ROI)
            mycursor.execute(sql, val)
            mydb.commit()
        except mysql.connector.Error as err:
            logging.error(f'Error inserting data: {err}')
        finally:
            if mydb.is_connected():
                mydb.close()
                

    def retrive_data(string):
        try: 
            mydb = mysql.connector.connect(host="localhost", user="root", password="ABCDEf45@", database="binance")
            cursor1 = mydb.cursor()
            cursor1.execute("SELECT * FROM variable")
            rows = cursor1.fetchall()

            for row in rows:
                variable_name, variable_value = row
                if string == "open":
                    cursor1.execute("SET SQL_SAFE_UPDATES = 0")
                    cursor1.execute("UPDATE variable SET value1 = 0 WHERE name1 = 'c'")
                    mydb.commit()
                    # Fetch the updated value from the database again
                    cursor1.execute("SELECT value1 FROM variable WHERE name1 = 'c'")
                    variable_value = cursor1.fetchone()[0]
                    
                elif string == "close":
                    cursor1.execute("SET SQL_SAFE_UPDATES = 0")
                    cursor1.execute("UPDATE variable SET value1 = 1 WHERE name1 = 'c'")
                    mydb.commit()
                    cursor1.execute("SELECT value1 FROM variable WHERE name1 = 'c'")
                    variable_value = cursor1.fetchone()[0]
                    
                elif string == "pass":
                    
                    return variable_value
        except Exception as e:
            logging.info(f'     Something worng :{e}')
        finally:
            if mydb.is_connected():
                mydb.close()

        

object1 = HistoricalData()
# object1.update_daily()
schedule.every().day.at("01:00:00").do(object1.update_daily)

# Run the scheduling loop
while True:
    schedule.run_pending()
    tm.sleep(1)




