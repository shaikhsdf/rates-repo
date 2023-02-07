from flask import Flask, jsonify, request
import psycopg2
import pandas as pd
# https://pypi.org/project/pydantic/
from pydantic import BaseModel
from datetime import date
  
# creating a Flask app
app = Flask(__name__)


class Params(BaseModel):
    date_from: date
    date_to: date
    origin: str
    destination: str


@app.route('/rates', methods = ['GET'])
def home():
    '''
        Captures the dates, origin and destination and returns the average price for the said said between orign and destination. 
        To access it on the terminal type: 
        curl "http://127.0.0.1:5000/rates?date_from=2016-01-01&date_to=2016-01-10&origin=CNSGH&destination=north_europe_main"
        or http://127.0.0.1:5000/rates?date_from=2016-01-01&date_to=2016-01-10&origin=CNSGH&destination=north_europe_main on any browser or postman.
        url: http://127.0.0.1:5000/rates
        params: date_from: date
                date_to:date
                origin:string
                destination:string
        returns: A json response with dates and average price
    '''
    if(request.method == 'GET'):
        try:
            parameters = request.args
            args = Params(**parameters)

            date_from = args.date_from
            date_to = args.date_to
            origin = args.origin
            destination = args.destination
            
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute(query, [origin, origin, destination, destination, date_from, date_to])
                data_df = pd.DataFrame(cur.fetchall())

            if not data_df.empty:      
                #creating a date_list dataframe to make sure all the dates between recieved date_from and date_to are included in the response
                date_list = pd.DataFrame(pd.date_range(start= date_from, end = date_to), columns=[0])
                data = get_final_data(data_df, date_list)
            else:
                return jsonify({'Message': 'Ah oh! looks like we dont have the data for your search at the moment, do retry in some time.'})
            
            return jsonify(data)
        except Exception as e:
            return jsonify({'Message': 'Facing technical issues, do retry in some time. ' + repr(e)})
    else:
        return jsonify({'Message': 'Please retry with GET method.'})



def get_db_connection():
    '''
        method to connect to postgres db instance
    '''
    conn = psycopg2.connect(host='localhost',
                            database='postgres',
                            user='postgres',
                            password='ratestask')
    return conn


# SQL querry to fetch the data with dynamic value rendering
query = '''
            SELECT 
                day,
                (CASE WHEN COUNT(price) >= 3 THEN ROUND(AVG(price)) 
                     ELSE NULL END) average_price
                FROM 
                prices
            WHERE
                orig_code in (
                    SELECT code FROM ports
                    JOIN regions ON ports.parent_slug = regions.slug
                    WHERE ports.parent_slug = %s 
                    OR 
                    ports.code = %s
                )
            AND
                dest_code in (
                    SELECT code FROM ports
                    JOIN regions ON ports.parent_slug = regions.slug
                    WHERE ports.parent_slug = %s
                    OR
                    ports.code = %s
                )
            AND
                day BETWEEN %s AND %s
                GROUP BY day
                ORDER BY day
        '''


def get_final_data(db_data_df, date_list):
    '''
        Method to reformat dates, merge and create the final df to be sent as response
    '''

    db_data_df[0] = pd.to_datetime(db_data_df[0]).dt.strftime('%Y-%d-%d')

    date_list[0] = pd.to_datetime(date_list[0]).dt.strftime('%Y-%d-%d')
    date_list[1] = 0

    # merging the datafram basis the dates data and include all missing dates if any
    final_df = date_list.merge(db_data_df, on=0, how="outer")
    final_df = final_df.drop("1_x", axis=1)
    final_df.rename(columns={0: 'day', "1_y": 'average_price'}, inplace=True)

    # to display null against the dates which has no data
    final_df = final_df.fillna('null')
    return final_df.to_dict(orient='records')

  
  
# driver function
if __name__ == '__main__':  
    app.run(debug = True)

    