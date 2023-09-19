import json
import random
import boto3
import time

topic = ""
region = ""
endpoint = ""

iot = boto3.client('iot-data', region_name=region,
                   endpoint_url=endpoint)


def lambda_handler(event, context):
    data = {
        "timestamp": time.time(),
        "temperature": random.uniform(0.0, 100.0),
        "humidity": random.uniform(0.0, 100.0),
        "pressure": random.uniform(0.0, 100.0)
    }

    try:
        response = iot.publish(
            topic=topic,
            qos=1,
            payload=json.dumps(data)
        )
        print(response)

        return {
            'statusCode': 200,
            'body': json.dumps('Dummy data published to IoT topic!')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }
