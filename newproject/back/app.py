from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector
from flask import request

app = Flask(__name__)
CORS(app)


def connect_db():
    return mysql.connector.connect(host="localhost", user="root", password="ABCDEf45@", database="binance")


def execute_query(query, params=None):
    try:
        db = connect_db()
        cursor = db.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        data = cursor.fetchall()
        return data
    except Exception as e:
        return {'error': str(e)}
    finally:
        if 'db' in locals() and db.is_connected():
            db.close()


@app.route('/api/data', methods=['GET'])
def get_data():
    query = "SELECT * FROM profit ORDER BY closeTime DESC"
    data = execute_query(query)
    
    return jsonify(data)


@app.route('/api/profit', methods=['GET'])
def get_profit_data():
 
    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')


    query = "SELECT SUM(unRealizedProfit) AS total_profit FROM profit WHERE STR_TO_DATE(openTime, '%Y-%m-%d %H:%i:%s') BETWEEN '" + start_date + " 00:00:00' AND '" + end_date + " 00:00:00'"


    data = execute_query(query)
    
    return jsonify(data)

@app.route('/api/balance', methods=['GET'])
def get_balance_data():
    query = "SELECT balance FROM profit ORDER BY balance  LIMIT 1;"
    data = execute_query(query)
    
    return jsonify(data)

@app.route('/api/cumulative-profit', methods=['GET'])
def get_cumulative_profit_data():
    query = """
        SELECT openTime, unRealizedProfit, @cumulative_profit := @cumulative_profit + unRealizedProfit AS cumulative_profit
        FROM profit, (SELECT @cumulative_profit := 0) AS cp_init
        ORDER BY openTime
    """
    data = execute_query(query)
    print(data)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
