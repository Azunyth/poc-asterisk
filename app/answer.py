# append the most voip library location to the pythonpath
import sys, time, getopt, os
sys.path.append("./most-voip/python/src/")

# import the Voip Library
from most.voip.api import VoipLib
from most.voip.constants import VoipEvent


argument_list = sys.argv[1:]
short_options = "hr:i:"
long_options = ["help", "register=", "ip="]

arguments, values = getopt.getopt(argument_list, short_options, long_options)
register = None
asterisk_ip = None

for current_argument, current_value in arguments:
    if current_argument in ("-h", "--help"):
        print ("python main.py -r <register> --ip <host>")
        sys.exit(0)
    elif current_argument in ("-r", "--register"):
        register = current_value
    elif current_argument in ("-i", "--ip"):
        asterisk_ip = current_value

# instanziate the lib
my_voip = VoipLib()

# build a dictionary containing all parameters needed for the Lib initialization

voip_params = {  
    u'username': register,  # a name describing the user
    u'sip_server_address': asterisk_ip,  # the ip of the remote sip server (default port: 5060)
    u'sip_server_user': register, # the username of the sip account
    u'sip_server_pwd': u'test',  #  the password of the sip account
    u'sip_server_transport' :u'udp', # the transport type (default: tcp)
    u'log_level' : 1,  # the log level (greater values provide more informations)
    u'debug' : False  # enable/disable debugging messages
}

end_of_call = False

# implement a method that will capture all the events triggered by the Voip Library
def notify_events(voip_event_type,voip_event, params):
    print "Received Event Type:%s  Event:%s -> Params: %s" % (voip_event_type, voip_event, params)

    # event triggered when the account registration has been confirmed by the remote Sip Server
    if (voip_event==VoipEvent.ACCOUNT_REGISTERED):
        print "Account %s registered: ready to accept call!" % my_voip.get_account().get_uri()

    # event triggered when a new call is incoming
    elif (voip_event==VoipEvent.CALL_INCOMING):
        print "INCOMING CALL From %s" % params["from"]
        time.sleep(2)
        print "Answering..."
        my_voip.answer_call()

    # event triggered when the call has been established
    elif(voip_event==VoipEvent.CALL_ACTIVE):
        print "The call with %s has been established"  % my_voip.get_call().get_remote_uri()

        dur = 5
        print "Waiting %s seconds before hanging up..."  % dur
        time.sleep(dur)
        my_voip.hangup_call()

    # events triggered when the call ends for some reasons
    elif (voip_event in [VoipEvent.CALL_REMOTE_DISCONNECTION_HANGUP, VoipEvent.CALL_REMOTE_HANGUP, VoipEvent.CALL_HANGUP]):
        print "End of call. Destroying lib..."
        my_voip.destroy_lib()

    # event triggered when the library was destroyed
    elif (voip_event==VoipEvent.LIB_DEINITIALIZED):
        print "Call End. Exiting from the app."
        end_of_call = True

    # just print informations about other events triggered by the library
    else:
        print "Received unhandled event type:%s --> %s" % (voip_event_type,voip_event)

# initialize the lib passing the dictionary and the callback method defined above:
my_voip.init_lib(voip_params, notify_events)

# register the account
my_voip.register_account()

while (end_of_call==False):
    time.sleep(2)