from flask import Flask, jsonify
from influxdb import InfluxDBClient as IFClient


app = Flask(__name__)
dbclient = IFClient(username="root", password="root", database="projdb" )

temp = dbclient.query("SELECT temperature, time FROM reading") # DB Query
humid = dbclient.query("SELECT humidity, time FROM reading") # DB Query

rsTemp = list(temp.get_points(measurement='reading')) # Change resultSet to  list
rsHumid = list(humid.get_points(measurement='reading'))	# Change resultSet to list

@app.route('/')
def test():
    return '<h1 style="color:blue;">Hello World</h1>'


@app.route('/temperature/all', methods=['GET'])
def get_all_temperature():
	return jsonify({"Temperature":rsTemp})


@app.route('/humidity/all', methods=['GET'])
def get_all_humidity():
	return jsonify({"Humidity":rsHumid})


app.run(host="0.0.0.0", port=8080, debug=True)
