from flask import Flask, jsonify, request
import psycopg2
import pandas as pd
  
# creating a Flask app
app = Flask(__name__)


# on the terminal type: curl "http://127.0.0.1:5000/rates?date_from=2016-01-01&date_to=2016-01-10&origin=CNSGH&destination=north_europe_main"
# returns a json response with relevant data when we use GET.
@app.route('/rates', methods = ['GET'])
def home():
    if(request.method == 'GET'):
        try:
            args = request.args
            date_from = args.get('date_from')
            date_to = args.get('date_to')
            origin = args.get('origin')
            destination = args.get('destination')
            
            conn = get_db_connection()
            with conn.cursor() as cur:
                cur.execute(query, [origin, origin, destination, destination, date_from, date_to])
                data_df = pd.DataFrame(cur.fetchall())

            if not data_df.empty:      
                #creating a date_list dataframe to make sure all the dates within the provides dates i.e date_from and date_to are included in the response
                date_list = pd.DataFrame(pd.date_range(start= date_from, end = date_to), columns=[0])
                data = get_final_data(data_df, date_list)
            else:
                return jsonify({'Message': 'Ah oh! looks like we dont have the data for your search at the moment, do retry in some time.'})
            
            return jsonify(data)
        except Exception:
            return jsonify({'Message': 'Facing technical issues, do retry in some time.'})
    else:
        return jsonify({'Message': 'Please retry with GET method.'})





# to connect with the db
def get_db_connection():
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


# to reformat, merge and create the final df to be sent as response
def get_final_data(db_data_df, date_list):
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

    