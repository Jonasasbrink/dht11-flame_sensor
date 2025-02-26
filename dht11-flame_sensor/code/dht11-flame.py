import time
import board
import adafruit_dht
import RPi.GPIO as GPIO
import requests

# ThingSpeak API detaljer
api_key = "Borttagen för säkerhet"
channel_url = "https://api.thingspeak.com/update"

# DHT11 sensor inställningar
dht_sensor = adafruit_dht.DHT11(board.D4)  #GPIO-pin DHT11

# Flame sensor inställningar
FLAME_PIN = 17  # GPIO-pin Flamesensor

# Ställ in GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(FLAME_PIN, GPIO.IN)

# Funktion för att läsa från DHT11
def read_dht11():
    try:
        temperature = dht_sensor.temperature
        humidity = dht_sensor.humidity
        return temperature, humidity
    except RuntimeError as e:
        print(f"Fel vid läsning av DHT11: {e}")
        return None, None

# Funktion för att läsa från flame sensor
def read_flame_sensor():
    if GPIO.input(FLAME_PIN):  # HIGH signal (flame detected)
        return 0  # Sänd numeriskt värde
    else:  # LOW signal (no flame detected)
        return 1  # Sänd numeriskt värde

# Skicka data till ThingSpeak
def send_to_thingspeak(temperature, humidity, flame_status):
    payload = {
        "api_key": api_key,
        "field1": temperature,  # Temperatur
        "field2": humidity,     # Luftfuktighet
        "field3": flame_status  # Flamestatus (1 eller 0)
    }

    try:
        response = requests.post(channel_url, params=payload)
        if response.status_code == 200:
            print(f"Data skickad till ThingSpeak: Temp={temperature}°C, Humidity={humidity}%, Flame={flame_status}")
        else:
            print(f"Fel vid sändning till ThingSpeak: {response.status_code}")
    except Exception as e:
        print(f"Fel vid HTTP-anrop: {e}")

# Huvudprogrammet
if __name__ == "__main__":
    try:
        while True:
            # Läs från DHT11 sensor
            temperature, humidity = read_dht11()
            if temperature is not None and humidity is not None:
                # Läs från flame sensor
                flame_status = read_flame_sensor()
                
                # Skicka data till ThingSpeak
                send_to_thingspeak(temperature, humidity, flame_status)

            # Vänta en stund innan nästa uppdatering
            time.sleep(15)
    except KeyboardInterrupt:
        print("Programmet avbröts.")
    finally:
        GPIO.cleanup()  # Rensa upp GPIO-inställningar
  
