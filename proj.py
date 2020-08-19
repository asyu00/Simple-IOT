#########################################################################
# Only works with python2 !!                                            #
# Please do not import any python3 module or run using python3 !!       #
# Install python module using "pip install" instead of "pip3 install" !!#
#########################################################################


from bme280 import readBME280All # Read from BME280 Sensor
from influxdb import InfluxDBClient as IFClient
from influxdb.client import InfluxDBClientError as ClientError
import RPi.GPIO as G
import datetime
import time
import paho.mqtt.client as mqtt

# Database related variables
USER = 'root'
PASSWORD = 'root'
DBNAME = 'projdb'
HOST = 'localhost'
PORT = '8086'
dbclient = None

# MQTT related variables
my_mqtt = mqtt.Client("client")
mqtt_broker = "m2m.eclipse.org"
topic_humi = "project/1701993F/humidity"
topic_temp = "project/1701993F/temperature"

# Setting up  GPIO pins
G.setmode(G.BCM)
G.setup(20, G.OUT) # Green LED, represents humidity is below alert
G.setup(21, G.OUT) # Red LED, represents humidity is above alert

# Returns variable "pointValues" to send to influxDB
def getSensorData(temp, humid):
    now = time.gmtime() # Gets current time

    pointValues = [{
        "time":time.strftime("%Y-%m-%d %H:%M:%S", now),
        "measurement":'reading',
        "tags": {"nodeId": "node_1"},
        "fields":{"temperature":temp, "humidity":humid},
    }] # Values to be sent to database

    return(pointValues)


# publishes temperature and humidity to phone through socket connection
def mqttPOST(temp, humid):
    my_mqtt.connect(mqtt_broker, port=1883) # connect to mqtt_broker
    temperature = "{}C".format(temp)
    humidity = "{}%".format(humid)

    try:
        my_mqtt.publish(topic_temp, temperature) # Publishes temperature
        my_mqtt.publish(topic_humi, humidity) # Publishes humidity

    except:
        print "Error publishing!"

    else:
        my_mqtt.disconnect()
        print "Disconnected!"


# Checks if humidity is above stated levels
def humidExceed(alert, humidity):
    if humidity > alert:
        G.output(21, 1)
        G.output(20, 0)
    else:
        G.output(21, 0)
        G.output(20, 1)

# Checks if temperature is above stated levels
def tempExceed(alert, temperature):
    if temperature > alert:
        G.output(21, 1)
        G.output(20, 0)
    else:
        G.output(21, 0)
        G.output(20, 1)


def main():
    dbclient = IFClient(HOST, PORT, USER, PASSWORD, DBNAME) # Connects to database
    G.output(21, 0) # Turns off led
    G.output(20, 0) # Turns off led
    time.sleep(2)
    while True:
        pass
        temp, pres, humid = readBME280All() # Read sensor from BME
        data = getSensorData(temp, humid)
        humidExceed(80, humid) # Checks if humidity exceeds 60%
        dbclient.write_points(data) # Write into database
        mqttPOST(temp, humid) # publishes to broker
        print "Written data"
        print "humidity: ", humid, "%"
        print "temperature: ", temp, "C"

        time.sleep(2)


if __name__ == '__main__':

    try:
        main()

    except KeyboardInterrupt:
        print "Exiting program..."

    except:
        print "An error has occured"

    finally:
        G.cleanup()
