import json, uuid, boto3
from config import *
from botocore.exceptions import ClientError

class KinesisStream(object):
    
    def __init__(self, stream):
        self.stream = stream

    def _connected_client(self):
        """ Connect to Kinesis Streams """
        return boto3.client('kinesis',region_name=AWS_REGION)

    def send_stream(self, data, partition_key):
        result = dict()
        result['status'] = False

        if partition_key == None:
            partition_key = uuid.uuid4()

        try:
            client = self._connected_client()
            response= client.put_record(
                StreamName=self.stream,
                Data=json.dumps(data),
                PartitionKey=partition_key
            )
            result['status'] = True
            result['string'] = response.text
        except ClientError as e:
            result['error_cause'] = 'AWS BOTO3  Error : %s' % e

        return result