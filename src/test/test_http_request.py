

import http.client
import urllib
import datetime
from datetime import timedelta  
import json
import jwt


date_now = datetime.datetime.utcnow()
init_date = str(date_now + timedelta(days=1)).split(" ")[0] 
final_date = str(date_now - timedelta(days=1)).split(" ")[0]

[string_date, string_time] = str(date_now).split(" ")
string_time = string_time[:8]


project_id = "iothousemanager"
hostname = 'us-central1-iothousemanager.cloudfunctions.net' # "127.0.0.1",
port = "443" # //8080,
path = '/get_historical_data' # "/cloud_get_history", //this is the cloud function name
method = 'POST'

# The sql stament preparation:
device_name = "Medidor Electrico UV 2.0"
serial_number = 1
data_type = "voltaje dc"
sql_uid = "1" # this corresponds to the sql db user unique id juan.ramirez.villegas@correounivalle.edu.co 

# the sert constants to test 
private_key_file = "./../src/certs/sql_uid%s_private.pem" % sql_uid # ; //'./src/certs/rsa_private_ghost_1.pem'; 
algorithm = 'RS256'


# //encode the string
def create_jwt(project_id, private_key_file, algorithm):

    """ Creates a JWT (https://jwt.io) to establish an MQTT connection.
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
        "iat": int(datetime.datetime.utcnow().timestamp()),
        # The time the token expires.
        "exp": int(datetime.datetime.utcnow().timestamp()) + 60 * 20,
        # The audience field should always be set to the GCP project id.
        "aud": project_id
     }

    #json_token = json.loads(token)
    #print("--------the json token is: ---------\n", json_token)

     # Read the private key file.
    with open(private_key_file, 'r') as f:
        private_key = f.read()
        print("--------the file readed id: -------\n", private_key)
    
    return jwt.encode({"data":token}, private_key, algorithm=algorithm) # this is a byte object


encripted_token = create_jwt(project_id, private_key_file, algorithm).decode("utf-8") 
print("---------the decoded encripted token is:--------\n", encripted_token)

measure_data = {
  "type":"measure", # //this is optional default is measure
  "sql_uid":1,
  "device_name": device_name,
  "serial_number": serial_number,
  "encripted_token": encripted_token,
  "data_type":data_type,
  "init_date": init_date,
  "final_date": final_date,
  "number_points": 10
}

# data = str(measure_data)

headers = {
    "Content-type": 'application/json',
    #'Content-Length': str(len(measure_data))
}


json_string = json.dumps(measure_data)

conn = http.client.HTTPSConnection(hostname, port, timeout=10)
conn.request(method, path, json_string, headers)
response = conn.getresponse()


print("the response status is: %s" % response.status)
print("the response reason is: %s" % response.reason)
data = response.read().decode('utf-8')
print(data)
conn.close()