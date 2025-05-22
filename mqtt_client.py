import paho.mqtt.client as mqtt
import ssl
import hmac
import hashlib
import base64
import time
from urllib.parse import quote_plus

# Azure IoT Hub Settings
IOT_HUB_HOSTNAME = "your-iot-hub.azure-devices.net"
DEVICE_ID = "your-device-id"
SHARED_ACCESS_KEY = "your-shared-access-key"
PORT = 8883  # Secure MQTT port

# Generate the SAS token
def generate_sas_token(hostname, device_id, key, expiry=3600):
    uri = f"{hostname}/devices/{device_id}"
    encoded_uri = quote_plus(uri)
    expiry_time = int(time.time()) + expiry
    string_to_sign = f"{encoded_uri}\n{expiry_time}"
    
    key_bytes = base64.b64decode(key)
    signature = base64.b64encode(hmac.new(key_bytes, string_to_sign.encode('utf-8'), hashlib.sha256).digest())
    sas_token = f"SharedAccessSignature sr={encoded_uri}&sig={quote_plus(signature)}&se={expiry_time}"
    return sas_token

# Callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to Azure IoT Hub")
        client.subscribe(f"devices/{DEVICE_ID}/messages/devicebound/#")
    else:
        print(f"Connection failed with code {rc}")

def on_message(client, userdata, msg):
    print(f"Message received on topic {msg.topic}: {msg.payload.decode()}")

def on_disconnect(client, userdata, rc):
    print("Disconnected from Azure IoT Hub")

# Create the MQTT client
client = mqtt.Client(client_id=f"devices/{DEVICE_ID}", protocol=mqtt.MQTTv311)

# Set credentials and SSL context
sas_token = generate_sas_token(IOT_HUB_HOSTNAME, DEVICE_ID, SHARED_ACCESS_KEY)
client.username_pw_set(username=f"{IOT_HUB_HOSTNAME}/{DEVICE_ID}/?api-version=2021-04-12", password=sas_token)

# Configure SSL/TLS
client.tls_set_context(ssl.create_default_context())
client.tls_insecure_set(False)

# Assign callbacks
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# Connect to Azure IoT Hub
try:
    print("Connecting to Azure IoT Hub...")
    client.connect(IOT_HUB_HOSTNAME, PORT, keepalive=60)
    client.loop_forever()
except KeyboardInterrupt:
    print("Disconnecting from Azure IoT Hub")
    client.disconnect()
