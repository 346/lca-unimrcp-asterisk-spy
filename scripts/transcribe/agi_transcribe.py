#!/usr/bin/python3
"""
    Asterisk AGI Azure bot  Demo Application

"""

import sys
from asterisk.agi import *
from dinamodb import *
from config import TRANSCRIBE_LANGUAGE
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
        self.caller_id=agi.get_variable('CHCALLERID')
        self.systemdnid=agi.get_variable('SYSTEMDNID')
        self.dinamodb= DinamodbConnector(self.channel,self.callid,self.caller_id,self.systemdnid)
        self.event="START"

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


    def get_system_dnid(self):
        """Retrieves caller_id_number from the data returned by FS"""
        # return agi.env['agi_callerid']
        agi.verbose("info",'got system dnid %s' % agi.get_variable('SYSTEMDNID'))
        return agi.get_variable('SYSTEMDNID')

    def get_call_uuid(self):
        """Retrieves current uuid from the data returned by FS"""
        return agi.env['agi_uniqueid']

    
    def get_time(self):
        time=int(datetime.now().timestamp())
        agi.verbose("info",'got_time %s' % datetime.now())
        return time

    def get_expired_at(self):
        expires_at = int((datetime.now() + timedelta(days=int(90))).timestamp())
        if self.event=='START':
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

    def verify_db_result(self,result):
        if result['status'] == True:
            if self.event=='END':
                raise AGISIGHUPHangup(f"{result['string']}")
                
            agi.verbose(result['string'])
            agi.verbose(str(result['kinesis']))
        else:
            if self.event=='END':
                raise AGISIGHUPHangup(f"{result['error_cause']}")
            agi.verbose(result['error_cause'])

    def write_event(self):
        
        result=self.dinamodb.write_event(self.get_expired_at(),self.event)
        self.verify_db_result(result)
        agi.verbose('got event %s' % self.event)
        agi.verbose('got  caller id number :  %s,got systemnumber : %s' %(self.caller_id,self.systemdnid))
        

    

    def add_segment_record(self):
        result=self.dinamodb.add_segment_record(self.get_segmentid(),self.get_start_time(),self.get_end_time(),self.get_transcript(),self.get_is_partial(),self.get_expired_at())
        self.verify_db_result(result)
        


    def get_transcript(self):
        """Retrieves score from the data returned by AWS Transcribe"""
        transcript=agi.get_variable('RECOG_INSTANCE(0/0/Results/0/Alternatives/0/Transcript)')
        agi.verbose('got transcript %s' % transcript)
        return transcript    


    def run(self):
        self.write_event()
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
agi.answer()
options = f't=3000&sct=1000&sint=15000&nit=30000&nif=json&spl={TRANSCRIBE_LANGUAGE}'
App = TranscribeApp(options)

"""to replace or register a method in the other class"""
def new_test_hangup():
    if agi._got_sighup:
        App.event='END'
        App.write_event()
        
agi.test_hangup = new_test_hangup

App.run()

