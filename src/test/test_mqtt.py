

import datetime
from datetime import timedelta  
import ssl
import random
import time
import threading

import http.client
import json
import jwt
import paho.mqtt.client as mqtt

def create_jwt(project_id, private_key_file, algorithm):
    """Creates a JWT (https://jwt.io) to establish an MQTT connection.
        Args:
         project_id: The cloud project ID this device belongs to
         private_key_file: A path to a file containing either an RSA256 or
                 ES256 private key.
         algorithm: The encryption algorithm to use. Either 'RS256' or 'ES256'
        Returns:
            An MQTT generated from the given project_id and private key, which
            expires in 20 minutes. After 20 minutes, your client will be
            disconnected, and a new JWT will have to be generated.
        Raises:
            ValueError: If the private_key_file does not contain a known key.
        """

    token = {
            # The time that the token was issued at
            'iat': datetime.datetime.utcnow(),
            # The time the token expires.
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            # The audience field should always be set to the GCP project id.
            'aud': project_id
    }

    # Read the private key file.
    with open(private_key_file, 'r') as f:
        private_key = f.read()

    print('Creating JWT using {} from private key file {}'.format(
            algorithm, private_key_file))

    return jwt.encode(token, private_key, algorithm=algorithm) # this is a byte object

def error_str(rc):
    """Convert a Paho error to a human readable string."""
    return '{}: {}'.format(rc, mqtt.error_string(rc))


def on_connect(unused_client, unused_userdata, unused_flags, rc):
    """Callback for when a device connects."""
    print('on_connect', mqtt.connack_string(rc))

    # After a successful connect, reset backoff time and stop backing off.
    global should_backoff
    global minimum_backoff_time
    should_backoff = False
    minimum_backoff_time = 1


def on_disconnect(unused_client, unused_userdata, rc):
    """Paho callback for when a device disconnects."""
    print('on_disconnect', error_str(rc))

    # Since a disconnect occurred, the next loop iteration will wait with
    # exponential backoff.
    global should_backoff
    should_backoff = True


def on_publish(unused_client, unused_userdata, unused_mid):
    """Paho callback when a message is sent to the broker."""
    print('on_publish happened')


def on_message(unused_client, unused_userdata, message):
    """Callback when the device receives a message on a subscription."""
    payload = str(message.payload)
    print('Received message \'{}\' on topic \'{}\' with Qos {}'.format(
            payload, message.topic, str(message.qos)))


def get_client(
        project_id, cloud_region, registry_id, device_id, private_key_file,
        algorithm, ca_certs, mqtt_bridge_hostname, mqtt_bridge_port):
    """Create our MQTT client. The client_id is a unique string that identifies
    this device. For Google Cloud IoT Core, it must be in the format below."""
    client_id = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(
            project_id, cloud_region, registry_id, device_id)
    print('Device client_id is \'{}\''.format(client_id))

    client = mqtt.Client(client_id=client_id)

    # With Google Cloud IoT Core, the username field is ignored, and the
    # password field is used to transmit a JWT to authorize the device.
    client.username_pw_set(
            username='unused',
            password=create_jwt(
                    project_id, private_key_file, algorithm))

    # Enable SSL/TLS support.
    client.tls_set(ca_certs=ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)

    # Register message callbacks. https://eclipse.org/paho/clients/python/docs/
    # describes additional callbacks that Paho supports. In this example, the
    # callbacks just print to standard out.
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect
    client.on_message = on_message

    # Connect to the Google MQTT bridge.
    client.connect(mqtt_bridge_hostname, mqtt_bridge_port)

    # This is the topic that the device will receive configuration updates on.
    mqtt_config_topic = '/devices/{}/config'.format(device_id)

    # Subscribe to the config topic.
    client.subscribe(mqtt_config_topic, qos=1)

    # The topic that the device will receive commands on.
    mqtt_command_topic = '/devices/{}/commands/#'.format(device_id)

    # Subscribe to the commands topic, QoS 1 enables message acknowledgement.
    print('Subscribing to {}'.format(mqtt_command_topic))
    client.subscribe(mqtt_command_topic, qos=0)

    return client

projectId = 'iothousemanager'
cloudRegion = 'us-central1'
registryId = 'univalle_registry'
sql_uid = 1
deviceId = "sql_uid%s_gateway" % sql_uid # 'raspberry_GHOST

mqttHost = 'mqtt.googleapis.com'
mqttPort = 443 # can use ports 443 8883
privateKeyFile = "./../src/certs/sql_uid%s_private.pem" % sql_uid # './src/certs/rsa_private_ghost_1.pem'; 
ca_certs = "./../src/certs/roots.pem" 
algorithm = 'RS256'
messageType = 'events/control' # state or events configured in gc /'events/electric_power' to a specific subfolder;

mqttClientId = "projects/{}/locations/{}/registries/{}/devices/{}".format(projectId, cloudRegion, registryId, deviceId)
mqttTopic = "/devices/{}/{}".format(deviceId, messageType)

if __name__ == "__main__":
    
    
    myClient = get_client(
        projectId, 
        cloudRegion, 
        registryId, 
        deviceId, 
        privateKeyFile, 
        algorithm, 
        ca_certs,
        mqttHost,
        mqttPort        
    )

    


    def publish_mqtt_data(paho_client, gc_topic):
    
        date_now = datetime.datetime.utcnow()
        [string_date, string_time] = str(date_now).split(" ")
        string_time = string_time[:8]

        rand_int = random.randint(0, 1)
        data = "on" if rand_int == 0 else "off"

        control_data_object = json.dumps({
            "sql_uid": sql_uid, 
            "mqtt_sub_folder": "electric_control",
            "operation":"send-save",
            "message":{
                "device_name": "Electric Controller Grid 1.0",
                "serial_number": 1000000001,
                "data_type": "control circuito a",
                "data": data,
                "date": string_date,
                "time": string_time,
            }
        })

        paho_client.publish(gc_topic, payload=control_data_object, qos=0, retain=False)

        print("message published: \n"+control_data_object+"\n")
        time.sleep(5)
        publish_mqtt_data(paho_client, gc_topic)


    myClient.loop_start() # this will initite a thread to handle the asyncronous input message buffer loop_stop() to stop the thread    
    publish_mqtt_data(myClient, mqttTopic)

    """
    my_publish_thread = threading.Thread(
        target = publish_mqtt_data, 
        args = (myClient, mqttTopic),
        daemon = True
        )
    my_publish_thread.start()

    myClient.loop_start() # this will initite a thread to handle the asyncronous input message buffer loop_stop() to stop the thread    
    # myClient.loop_forever()  # this is a blocking method to handle the input buffer

    print("do something baby")
    while True:
        pass
    """


    

