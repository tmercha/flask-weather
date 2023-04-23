from flask import Flask, jsonify, request
from flask import render_template
import mysql.connector
import os


app = Flask(__name__)


db_user = os.environ.get('DB_USERNAME')
db_password = os.environ.get('DB_PASSWORD')
db_host = os.environ.get('DB_HOST')
db_database = os.environ.get('DB_DATABASE')

# Establish database connection

db = mysql.connector.connect(
    host=db_host,
    user=db_user,
    password=db_password,
    database=db_database
)
cursor = db.cursor()


@app.route('/')
def hello_world():
    return render_template('home.html')


@app.route('/get-weather')
def get_weather():
    location = request.args.get('location')
    date = request.args.get('date')
    # Comma separated list of parameters specified by user
    parameters = request.args.get('parameters')

    # Split the string of parameters requested by the user into an interpretable list. Remove trailing whitespace with strip()

    if parameters:
        parameters = [parameters.strip()
                      for parameter in parameters.split(',')]
        parameters.append('date')
        parameters.append('location')
        print(parameters)

    if not parameters:
        parameters = ['location', 'date', 'wind_speed',
                      'wind_direction', 'temperature', 'humidity']

    sql_query = "SELECT " + \
        ', '.join(parameters) + \
        " FROM weather_data WHERE location=%s AND date=%s"
    cursor.execute(sql_query, (location, date))


    columns = [column[0] for column in cursor.description]
    rows = cursor.fetchall()

    if not rows: 
        error_message = f'api currently using sample data only: nothing found for {location} on {date}'
        return jsonify({'error': error_message}), 404

    results = []

    for row in rows:
        result = {}

        units = {
            'temperature': 'celsius',
            'wind_speed': 'miles per hour',
            'wind_direction': 'degrees',
            'humidity': 'percentage',
        }

        for key in list(units.keys()):
            if key not in columns:
                del units[key]

        for i, column in enumerate(columns):
            if column == 'date':
                # control the datetime
                result['date'] = row[i].strftime('%Y-%m-%d')
            else:
                result[column] = row[i]

        results.append(result)

    results.append({'units': units})

    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True)
