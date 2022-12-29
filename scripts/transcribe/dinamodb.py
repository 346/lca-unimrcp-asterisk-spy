#!/usr/bin/python3.6
"""
    dinamo Database Connector Routine

    This script provides helper routine for insert data to
    the dinamo db.

    * Revision: 1
    * Date: Apr 6, 2022
    * Vendor: Universal Speech Solutions LLC
    
"""

import sys
from config import *
from datetime import datetime, timedelta
import boto3
from kinesis import *
from botocore.exceptions import ClientError

class DinamodbConnector:

    """A Dinamo database connector class"""

    def __init__(self,channel,call_uuid,caller_id,system_dnid):
        """Constructor"""
        self.dynamodb = boto3.resource(service_name='dynamodb', region_name=AWS_REGION)
        self.table=self.dynamodb.Table(DINAMO_DB_TABLE)
        self.kinesisds=KinesisStream(KINESIS_DATA_STREAM_NAME)
        self.channel=channel
        self.call_uuid=call_uuid
        self.caller_id=caller_id
        self.system_dnid=system_dnid
        

    def write_event(self,expired_at,event):
        result = dict()
        result['status'] = False
        time=datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        try:
            

            Item={
                'PK': 'ce#%s' %self.call_uuid,
                'SK': 'ts#%s#et#START#c#%s' %(time,self.channel),
                'Channel': self.channel,
                'CallId': self.call_uuid,
                'EventType': event,
                'CreatedAt': time,
                'ExpiresAfter': expired_at,
            }
            response=self.table.put_item(
              Item=Item
            )
            # Item={
            #     'PK': 'ce#%s' %call_uuid,
            #     'SK': 'ts#%s#et#START#c#%s' %(time,channel),
            #     'Channel': channel,
            #     'CallId': call_uuid,
            #     'EventType': 'END',
            #     'CreatedAt': time,
            #     'ExpiresAfter': expired_at,
            # }
            # response=self.table.put_item(
            #   Item=Item
            # )
            KINItem={
                'Channel': self.channel,
                'CallId': self.call_uuid,
                'EventType': event,
                'CreatedAt': time,
                'CustomerPhoneNumber': self.caller_id,
                'SystemPhoneNumber': self.system_dnid,
            }
            response=self.kinesisds.send_stream(KINItem,self.call_uuid)
        
            result['status'] = True
            result['kinesis']=response
            result['string'] = 'Your query is successfully committed' 
            
        except Exception as e:
            result['error_cause'] = 'AWS BOTO3  Error : %s' % e
            

        return result

 
    def add_segment_record(self,segmentid,start_time,end_time,transcript,is_partial,expired_at):
        """Inserts a new record with call data"""
        result = dict()
        result['status'] = False
        
        
        try:
            time=datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

            Item={
                'PK': f'ce#{self.call_uuid}',
                'SK': f'ts#{time}#et#ADD_TRANSCRIPT_SEGMENT#c#{self.channel}',
                'Channel': self.channel,
                'CallId': self.call_uuid,
                'SegmentId': segmentid,
                'StartTime': start_time,
                'EndTime': end_time,
                'Transcript': transcript,
                'IsPartial': is_partial,
                'EventType': 'ADD_TRANSCRIPT_SEGMENT',
                'CreatedAt': time,
                'ExpiresAfter': expired_at,
                'Sentiment': None,
                'IssuesDetected': None,
            }

            
            response=self.table.put_item(
                Item=Item
            )
            KINItem={
                'Channel': self.channel,
                'CallId': self.call_uuid,
                'SegmentId': segmentid,
                'StartTime': start_time,
                'EndTime': end_time,
                'Transcript': transcript,
                'IsPartial': is_partial,
                'EventType': 'ADD_TRANSCRIPT_SEGMENT',
                'CreatedAt': time,
                'ExpiresAfter': expired_at,
                'Sentiment': None,
                'IssuesDetected': None,
            }
            response=self.kinesisds.send_stream(KINItem,self.call_uuid)
        
            result['status'] = True
            result['kinesis']=response
            result['string'] = 'Your query is successfully committed' 
            
        except ClientError as e:
            result['error_cause'] = 'AWS BOTO3  Error : %s' % e
        
            
            
        return result



#     def listttt(self):
#         dynamodb = boto3.client('dynamodb',region_name=AWS_REGION)
#         response = dynamodb.list_tables()
#         print(response)


# app= DinamodbConnector()
# app.listttt()
