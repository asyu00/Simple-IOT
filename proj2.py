import time
import RPi.GPIO as G
import paho.mqtt.client as mqtt

G.setmode(G.BCM)

G.setup(22, G.OUT) # Yellow LED, signals instruction received from phone
G.setup(16, G.OUT) # Light Bulb, represents air conditioner
G.setup(24, G.OUT) # Buzzer, represents aircon sound when turned on

bulb = G.PWM(16, 50) # 50Hz frequency
bulb.start(0) # 0% Duty Cycle

mqttPost = mqtt.Client("post") # Unique Client ID
broker = "m2m.eclipse.org"

def on_message(client, userdata, message):
	print message.topic, "payload: ", message.payload
	if message.payload == "on" and not G.input(22):
		buzz(1)
		G.output(22, 1) # Turns on Yellow LED
		bulb.ChangeDutyCycle(25) # Sets default value of 25% duty cycle on light bulb

	elif message.payload == "off" and G.input(22):
		buzz(2)
		G.output(22, 0) # Turns off Yellow LED
		bulb.ChangeDutyCycle(0) # Turns off light bulb

	elif "temp" in message.payload and G.input(22): # If Yellow LED is turned on and "temp" is in message
		tem = message.payload.split(" ") # Split by spacebar
		try: # Try to set tem[1] as an integer, if invalid, prompt user to enter a valid number
			t = int(tem[1]) # 13C to 28C
			if t < 13 or t > 28:
				print("Enter a temperature of value between 13C and 28C!")
				mqttPOST("Enter a temperature of value between 13C and 28C!")
				return # If user enters a value lower than 13 or more than 28, return
			t2DC = (((t - 13) * (100 - 25)) / (28 - 13)) + 25 # t to Duty Cycle, linear increment 
			if t2DC > 100:
				t2DC = 100 #if t2DC over 100, set Duty Cycle to 100
			buzz(1)
			bulb.ChangeDutyCycle(t2DC) # Change duty cycle of bulb to user stated value
		except:
			print("Enter a valid number !")
			mqttPOST("Enter a valid number !")

	else:
		print("Error processing command...")
		mqttPOST("Error processing command...")
		time.sleep(2)
		print("You either tried to turn on the aircon when it is already on, or vice versa, or tried to set the temperature when the aircon is turned off.")
		mqttPOST("You either tried to turn on the aircon when it is already on, or vice versa, or tried to set the temperature when the aircon is turned off.")

def buzz(choice): # 2 different type of buzzer sound
	if choice == 1:
		G.output(24, 1)
		time.sleep(0.3)
		G.output(24, 0)

	elif choice == 2:
		for i in range(2):
			G.output(24, 1)
			time.sleep(0.1)
			G.output(24, 0)
			time.sleep(0.1)

def mqttSubscribe():
	my_mqtt = mqtt.Client("subscribe") # Unique client ID
	my_mqtt.on_message = on_message
	my_mqtt.connect(broker, port=1883)
	my_mqtt.subscribe("1701993F/aircon")
	my_mqtt.loop_start()
	print "Subbed to topic"

def mqttPOST(msg):
	mqttPost.connect(broker, port=1883)

	try:
		mqttPost.publish("1701993F/messages", msg)

	except:
		print "Error Publishing"

	else:
		mqttPost.disconnect()

def main():
	mqttSubscribe()
	while True:
		time.sleep(0.5)

if __name__ == "__main__":
	try:
		main()

	except KeyboardInterrupt:
		G.cleanup()
