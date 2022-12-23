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
from botocore.exceptions import ClientError

class DinamodbConnector:

    """A Dinamo database connector class"""

    def __init__(self):
        """Constructor"""
        self.dynamodb = boto3.resource(service_name='dynamodb', region_name=AWS_REGION)
        self.table=self.dynamodb.Table(DINAMO_DB_TABLE)

    def start_call(self,channel,call_uuid,expired_at):
        result = dict()
        result['status'] = False

        try:
            time=datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

            Item={
                'PK': 'ce#%s' %call_uuid,
                'SK': 'ts#%s#et#START#c#%s' %(time,channel),
                'Channel': channel,
                'CallId': call_uuid,
                'EventType': 'START',
                'CreatedAt': time,
                'ExpiresAfter': expired_at,
            }
            response=self.table.put_item(
              Item=Item
            )
            Item={
                'PK': 'ce#%s' %call_uuid,
                'SK': 'ts#%s#et#START#c#%s' %(time,channel),
                'Channel': channel,
                'CallId': call_uuid,
                'EventType': 'END',
                'CreatedAt': time,
                'ExpiresAfter': expired_at,
            }
            response=self.table.put_item(
              Item=Item
            )
            result['status'] = True
            result['string'] = 'Your query is successfully committed' 
            
        except Exception as e:
            result['error_cause'] = 'AWS BOTO3  Error : %s' % e
            

        return result

 
    def add_segment_record(self,channel,call_uuid,segmentid,start_time,end_time,transcript,is_partial,expired_at):
        """Inserts a new record with call data"""
        result = dict()
        result['status'] = False
        
        
        try:
            time=datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')

            Item={
                'PK': f'ce#{call_uuid}',
                'SK': f'ts#{time}#et#ADD_TRANSCRIPT_SEGMENT#c#{channel}',
                'Channel': channel,
                'CallId': call_uuid,
                'SegmentId': segmentid,
                'StartTime': start_time,
                'EndTime': end_time,
                'Transcript': transcript,
                'IsPartial': is_partial,
                'EventType': 'ADD_TRANSCRIPT_SEGMENT',
                'CreatedAt': time,
                'ExpiresAfter': expired_at,
            }
            
            response=self.table.put_item(
                Item=Item
            )
        
            result['status'] = True
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