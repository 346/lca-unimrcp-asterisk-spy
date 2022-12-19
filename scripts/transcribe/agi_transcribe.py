#!/usr/bin/python3
"""
    Asterisk AGI Azure bot  Demo Application

"""

import sys
from asterisk.agi import *
from dinamodb import *
import json
from datetime import datetime, timedelta


"""

    Asterisk AWS Transcribe  Application

    This script interacts with AWS Transcribe   API via UniMRCP server.

    * Revision: 1
    * Date: Apr 6, 2022
    * Vendor: Universal Speech Solutions LLC

"""




class TranscribeApp:

    """A class representing Azure bot application"""

    def __init__(self, options):
        """Constructor"""
        self.options = options
        self.status = None
        self.cause = None
        self.action = agi.get_variable("ACTION") 
        self.channel= agi.get_variable("SPYCHANNEL")
        self.callid=agi.get_variable("GLOBALID")

    def recog(self):
        """This is an internal function which calls MRCPRecog"""
        self.grammars = "builtin:speech/transcribe?" 
        args = "\\\"%s\\\",%s" % (self.grammars, self.options)
        agi.set_variable('RECOGSTATUS', ' ')
        agi.set_variable('RECOG_COMPLETION_CAUSE', ' ')
        self.action = None
        agi.appexec('MRCPRecog', args)
        self.status = agi.get_variable('RECOGSTATUS') 
        agi.verbose('got status %s' % self.status)
        if self.status == 'OK':
            self.cause = agi.get_variable('RECOG_COMPLETION_CAUSE')
            # agi.verbose('got completion cause %s' % self.cause)
        else:
            agi.verbose('Recognition completed abnormally')
        self.cause = agi.get_variable('RECOG_COMPLETION_CAUSE')
        # agi.verbose('got completion cause %s' % self.cause)

   
    def get_caller_id(self):
        """Retrieves caller_id_number from the data returned by FS"""
        return agi.env['agi_callerid']


    def get_call_uuid(self):
        """Retrieves current uuid from the data returned by FS"""
        return agi.env['agi_uniqueid']

    
    def get_time(self):
        time=int(datetime.now().timestamp())
        agi.verbose("info",'got_time %s' % datetime.now())
        return time

    def get_expired_at(self):
        expires_at = int((datetime.now() + timedelta(days=int(90))).timestamp())
        agi.verbose('got segmentid %s' % expires_at)
        return expires_at

    def get_segmentid(self):
        """Retrieves segmentid from the data returned by AWS Transcribe"""
        segmentid=agi.get_variable('RECOG_INSTANCE(0/0/Results/0/ResultId)')
        agi.verbose('got segmentid %s' % segmentid)
        return segmentid

    def get_start_time(self):
        """Retrieves start_time from the data returned by AWS Transcribe"""
        start_time=agi.get_variable('RECOG_INSTANCE(0/0/Results/0/StartTime)')
        agi.verbose('got start_time %s' % start_time)
        return start_time

    def get_end_time(self):
        """Retrieves end_time from the data returned by AWS Transcribe"""
        end_time=agi.get_variable('RECOG_INSTANCE(0/0/Results/0/EndTime)')
        agi.verbose('got end_time %s' % end_time)
        return end_time

    def get_is_partial(self):
        """Retrieves is_partial from the data returned by AWS Transcribe"""
        is_partial=agi.get_variable('RECOG_INSTANCE(0/0/Results/0/IsPartial)')
        agi.verbose('got is_partial %s' % is_partial)
        is_partial=eval(is_partial.title())
        agi.verbose('got is_partial %s' % is_partial)
        return is_partial

    def start(self):
        agi.verbose('got dcfdfffffffffffffffffffffffffffffffff %s' % self.callid)
        result=dinamo_db.start_call(self.channel,self.callid,self.get_expired_at())
        if result['status'] == True:
            agi.verbose(result['string'])
        else:
            agi.verbose(result['error_cause'])

    def add_segment_record(self):
        result=dinamo_db.add_segment_record(self.channel,self.callid,self.get_segmentid(),self.get_start_time(),self.get_end_time(),self.get_transcript(),self.get_is_partial(),self.get_expired_at())
        if result['status'] == True:
            agi.verbose(result['string'])
        else:
            agi.verbose(result['error_cause'])


    def get_transcript(self):
        """Retrieves score from the data returned by AWS Transcribe"""
        transcript=agi.get_variable('RECOG_INSTANCE(0/0/Results/0/Alternatives/0/Transcript)')
        agi.verbose('got transcript %s' % transcript)
        return transcript    


    def run(self):
        self.start()
        processing = True
        while processing:
            self.recog()
            processing = True
            if self.status == 'OK':
                if self.cause == '000':         
                    self.add_segment_record() 

                elif self.cause != '001' and self.cause != '002':
                    processing = False
            elif self.cause != '001' and self.cause != '002':
                processing = False




agi = AGI()
options = 't=3000&sct=1000&sint=15000&nit=10000&nif=json'
dinamo_db = DinamodbConnector()
App = TranscribeApp(options)

App.run()
agi.verbose('exiting')