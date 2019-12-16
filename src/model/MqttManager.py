


import datetime
from datetime import timedelta  
import ssl
import random
import time
import threading
import os
import logging
logging.basicConfig(level=logging.DEBUG) # this will set all the debugging messages on

import json
import jwt
import paho.mqtt.client as mqtt

import chardet


#https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/iot/api-client/mqtt_example/cloudiot_mqtt_example.py

# this one is only for data storage
class MqttManager(object):

    def __init__(
        self, 
        sql_uid=1,
        on_control_callback = None,
        on_measure_callback = None,
        on_disconnect_callback = None,
        on_connect_callback = None,
        ):

        # Recieved message callbacks:
        self.on_control = on_control_callback
        self.on_measure = on_measure_callback
        self.on_disconnect_call = on_disconnect_callback
        self.on_connect_call = on_connect_callback

        # proyect constants:
        self.projectId = 'iothousemanager'
        self.cloudRegion = 'us-central1'
        self.registryId = 'univalle_registry'
        self.sql_uid = sql_uid
        self.deviceId = "sql_uid%s_gateway" % sql_uid 

        self.mqttHost = 'mqtt.googleapis.com'
        self.mqttPort = 443 # can use ports 443 8883

        
        self.privateKeyFile = os.path.abspath("./src/certs/sql_uid%s_private.pem" % sql_uid) # './src/certs/rsa_private_ghost_1.pem'; 
        self.ca_certs = os.path.abspath("./src/certs/roots.pem")
        self.algorithm = 'RS256'
    
        self.mqttClientId = "projects/{}/locations/{}/registries/{}/devices/{}".format(
            self.projectId, 
            self.cloudRegion, 
            self.registryId, 
            self.deviceId
            )

        # get the client to manage the connection
        self.client = self.get_client(
            self.projectId, 
            self.cloudRegion, 
            self.registryId, 
            self.deviceId, 
            self.privateKeyFile, 
            self.algorithm, 
            self.ca_certs,
            self.mqttHost,
            self.mqttPort        
        )


    def create_jwt(self, project_id, private_key_file, algorithm):
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
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes = 60 * 48),
                # The audience field should always be set to the GCP project id.
                'aud': project_id
        }

        # Read the private key file.
        with open(private_key_file, 'r') as f:
            private_key = f.read()

        print('Creating JWT using {} from private key file {}'.format(
                algorithm, private_key_file))

        return jwt.encode(token, private_key, algorithm=algorithm) # this is a byte object

    def error_str(self, rc):
        """Convert a Paho error to a human readable string."""
        return '{}: {}'.format(rc, mqtt.error_string(rc))


    def on_connect(self, unused_client, unused_userdata, unused_flags, rc):
        """Callback for when a device connects."""
        print('on_connect mqqtmanager message: ', mqtt.connack_string(rc))

        # After a successful connect, reset backoff time and stop backing off.
        global should_backoff
        global minimum_backoff_time
        should_backoff = False
        minimum_backoff_time = 1
        self.on_connect_call()


    def on_disconnect(self, unused_client, unused_userdata, rc):
        """Paho callback for when a device disconnects."""
        print('on_disconnect', self.error_str(rc))
        self.on_disconnect_call()

        # Since a disconnect occurred, the next loop iteration will wait with
        # exponential backoff
        global should_backoff
        should_backoff = True
        #self.client.loop_stop()


    def on_publish(self, unused_client, unused_userdata, unused_mid):
        """Paho callback when a message is sent to the broker."""
        print('__________________on_publish happened____________________')


    def on_message(self, unused_client, unused_userdata, message):
        payload = message.payload

        print('__________Received message \'{}\' on topic \'{}\' with Qos {}______'.format(
                payload, message.topic, str(message.qos)))
        
        decoded = payload.decode('ascii')
        data_dic = json.loads(decoded)

        if message.topic == "/devices/%s/commands/measure/raspberry" % self.deviceId:
            print("measure message recieved") 
            self.on_measure(data_dic)
        elif message.topic == "/devices/%s/commands/control/raspberry" % self.deviceId:
            print("control message recieved")
            self.on_control(data_dic)
        
        else:
            print("the message has other topic")

    def publish_control(self, dic_data, messageType='events/control'):
        # generate the control topic string
        deviceId = "sql_uid%s_gateway" % self.sql_uid # 'raspberry_GHOST
        mqttTopic = "/devices/{}/{}".format(deviceId, messageType)
        
        # send the data
        # print("the dictionary data is: "+str(dic_data))
        string_data = json.dumps(dic_data)
        # print("the dumped data is: "+string_data)
        self.client.publish(mqttTopic, payload=string_data, qos=0, retain=False)
        print("controlled data sended")
    
    def publish_measure(self, dic_data, messageType='events/measure'):
        # generate the control topic string
        deviceId = "sql_uid%s_gateway" % self.sql_uid # 'raspberry_GHOST
        mqttTopic = "/devices/{}/{}".format(deviceId, messageType)
        
        # send the data
        # print("the dictionary data is: "+str(dic_data))
        string_data = json.dumps(dic_data)
        # print("the dumped data is: "+string_data)
        self.client.publish(mqttTopic, payload=string_data, qos=0, retain=False)
        print("measured data sended")

    def get_client(self, 
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
                password=self.create_jwt(
                        project_id, private_key_file, algorithm))

        # Enable SSL/TLS support.
        client.tls_set(ca_certs=ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)

        # Register message callbacks. https://eclipse.org/paho/clients/python/docs/
        # describes additional callbacks that Paho supports. In this example, the
        # callbacks just print to standard out.
        client.on_connect = self.on_connect
        client.on_publish = self.on_publish
        client.on_disconnect = self.on_disconnect
        client.on_message = self.on_message

        # Connect to the Google MQTT bridge.
        client.connect(mqtt_bridge_hostname, mqtt_bridge_port)

        # start the procesing loop:
        client.loop_start() 

        # This is the topic that the device will receive configuration updates on.
        mqtt_config_topic = '/devices/{}/config'.format(device_id)

        # Subscribe to the config topic.
        client.subscribe(mqtt_config_topic, qos=1)

        # The topic that the device will receive commands on.
        mqtt_command_topic_control = '/devices/{}/commands/#'.format(device_id)
        #mqtt_command_topic_control = '/devices/{}/commands/control/raspberry'.format(device_id)
        mqtt_command_topic_measure = '/devices/{}/commands/measure/raspberry'.format(device_id)

        # Subscribe to the commands topic, QoS 1 enables message acknowledgement.
        print('Subscribing to {}'.format(mqtt_command_topic_control))
        print('Subscribing to {}'.format(mqtt_command_topic_measure))
        client.subscribe(mqtt_command_topic_control, qos=0)
        client.subscribe(mqtt_command_topic_measure, qos=0)

        return client



if __name__ == "__main__":


    # info needed to send data:
    sql_uid = 1
    messageType = 'events/control'
    deviceId = "sql_uid%s_gateway" % sql_uid # 'raspberry_GHOST
    mqttTopic = "/devices/{}/{}".format(deviceId, messageType)
    

    myMqttManager = MqttManager()

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
                "device_name": ["Electric Controller Grid 1.0"],
                "serial_number": [1000000001],
                "data_type": ["control circuito a"],
                "data": data,
                "date": string_date,
                "time": string_time,
            }
        })

        paho_client.publish(gc_topic, payload=control_data_object, qos=0, retain=False)

        print("message published: \n"+control_data_object+"\n")
        time.sleep(5)
        publish_mqtt_data(paho_client, gc_topic)




    myMqttManager.client.loop_start() # this will initite a thread to handle the asyncronous input message buffer loop_stop() to stop the thread    
    publish_mqtt_data(myMqttManager.client, mqttTopic)