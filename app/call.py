import sys, time, getopt, os

sys.path.append("./most-voip/python/src/")
# import the Voip Library
from most.voip.api import VoipLib
from most.voip.constants import VoipEvent

argument_list = sys.argv[1:]
short_options = "he:c:i:"
long_options = ["help", "extension=", "caller=", "ip="]

arguments, values = getopt.getopt(argument_list, short_options, long_options)
caller = None
extension = None
asterisk_ip = None

for current_argument, current_value in arguments:
    if current_argument in ("-h", "--help"):
        print ("python main.py -e <extension> -c <caller> --ip <host>")
        sys.exit(0)
    elif current_argument in ("-e", "--extension"):
        extension = current_value
    elif current_argument in ("-c", "--caller"):
        caller = current_value
    elif current_argument in ("-i", "--ip"):
        asterisk_ip = current_value

# instanziate the lib
my_voip = VoipLib()

voip_params = {
    u'username': caller,  # a name describing the user
    u'sip_server_address': asterisk_ip,  # the ip of the remote sip server (default port: 5060)
    u'sip_server_user': caller, # the username of the sip account
    u'sip_server_pwd': u'test',  #  the password of the sip account
    u'sip_server_transport' :u'udp', # the transport type (default: tcp)
    u'log_level' : 1,  # the log level (greater values provide more informations)
    u'debug' : False  # enable/disable debugging messages
}

def notify_events(voip_event_type, voip_event, params):
    print "Received Event Type:%s -> Event: %s Params: %s" % (voip_event_type, voip_event, params)
    if (voip_event == VoipEvent.ACCOUNT_REGISTERED):
        if extension is not None:
            my_voip.make_call(extension)
    elif (voip_event in [VoipEvent.CALL_REMOTE_DISCONNECTION_HANGUP, VoipEvent.CALL_REMOTE_HANGUP, VoipEvent.CALL_HANGUP]):
        print "Call terminated"
        my_voip.destroy_lib()
        sys.exit(0)

# initialize the lib passing the dictionary and the callback method defined above:
my_voip.init_lib(voip_params, notify_events)

if caller is not None and asterisk_ip is not None:
    my_voip.register_account()

while(True):
    time.sleep(1)
