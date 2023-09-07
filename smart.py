from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder 
import json
import datetime
import time
import random
from PIL import Image
import boto3
from botocore.exceptions import NoCredentialsError

ENDPOINT ="a1bdk3a88grv3n-ats.iot.us-east-1.amazonaws.com"
ACCESS_KEY='FSGA5KREEF3FMYBJFI23'
SECRET_KEY='FGRUPpwAzggerg3uLP4GR31UKvct4RWem3Tw0'

DEVICES=[
  {
    "id":"baby1",
    "client_id":"smart-cradle-01",
    "certificate_path":"C:/Users/yvonn/OneDrive/Desktop/iot-smartcradle/6c14937f7af8e019a5b99f8b97af9ab9106d7061c23fc62bfad31ed42f6032db-certificate.pem.crt",
    "private_key_path":"C:/Users/yvonn/OneDrive/Desktop/iot-smartcradle/6c14937f7af8e019a5b99f8b97af9ab9106d7061c23fc62bfad31ed42f6032db-private.pem.key",
    "topic":"cradle/sensors/testing/1"
  }

]


#to generate sensors' data in json format
def generate_data(device,data_id):
  temperature=round(random.uniform(25,35),2)
  sound=round(random.uniform(50, 80), 2)
  humidity=round(random.uniform(30, 50), 2)
  heart_beat=round(random.randint(40,60))
  baby_tmp=round(random.uniform(36,37),2)

  
  return {
                'timestamp':str(datetime.datetime.now()),
                'device_id':device['client_id'],
                'data_id':data_id,
    'environment_temperature':temperature,
    'sound':sound,
                'humidity':humidity,
                'heart_beat':heart_beat,
                'baby_temperature':baby_tmp

                }

#to upload camera images to S3 bucket   
def uploadImage(local_file, bucket, s3_file):
        s3=boto3.client('s3',aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

        try:
                s3.upload_file(local_file, bucket, s3_file)
                print("Upload Successful")
                return True
        except FileNotFoundError:
                print("The file was not found")
                return False
        except NoCredentialsError:
                print("Credentials not available")
                return False



# Spin up resources
event_loop_group = io.EventLoopGroup(1)
host_resolver = io.DefaultHostResolver(event_loop_group)
client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

 
for device in DEVICES:
  #build the connectin to IoT Core
  mqtt_connection = mqtt_connection_builder.mtls_from_path(
      endpoint=ENDPOINT,
        port=8883,
      cert_filepath=device["certificate_path"],
        pri_key_filepath=device["private_key_path"],
        client_bootstrap=client_bootstrap,
        ca_filepath="C:/Users/yvonn/OneDrive/Desktop/iot-smartcradle/AmazonRootCA1.pem",
        
        client_id=device["client_id"],
        clean_session=False,
        keep_alive_secs=6,
  )
  print(device["certificate_path"])
  print("Connecting to ",ENDPOINT, " with client ID ",{device['client_id']},"...")
  connect_future = mqtt_connection.connect()

  # Future.result() waits until a result is available
  connect_future.result()
  print("Connected!")
  

#publish 20 data according to topic 
  for i in range (20):
                uploadingImg=uploadImage('C:/Users/yvonn/OneDrive/Desktop/iot-smartcradle/images/baby'+str(i)+'.jpg','baby-detector','baby'+str(i)+'.jpg')
                data = generate_data(device, i+1)
                mqtt_connection.publish(topic=device["topic"], payload=json.dumps(data),qos=mqtt.QoS.AT_LEAST_ONCE)
                print("publish data: ",json.dumps(data)," topic: ",device["topic"])
                time.sleep(10)

  print('Pubish end')

  disconnect_future=mqtt_connection.disconnect()
  disconnect_future.result()





