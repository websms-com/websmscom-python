#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
"""
--------------------------------------------------------------------------------------
 websms.com Gateway usage sample code
  1.) create client, 
  2.) create message, 
  3.) send message with client.
--------------------------------------------------------------------------------------
"""
import sys
import traceback
import WebSmsComToolkit

  
#--- Modify these values to your needs ----------------
username                = 'your_username'
password                = 'your_password'
gateway_url             = 'https://api.websms.com/'
recipient_address_list  = [4367612345678L]
message_text_unicode    = u"Willkommen zur BusinessPlatform SDK von websms.com! Diese Nachricht enthält 160 Zeichen. Sonderzeichen: äöüß. Eurozeichen: \u20ac. Das Ende wird nun ausgezählt43210"
max_sms_per_message     = 1

# true: do not send sms for real, just test interface
is_test                 = True
#-------------------------------------------------------

def main():
  
  try:
    
    # 1.) -- create sms client (once) ------
    client         = WebSmsComToolkit.Client(gateway_url, username, password)
#    client.verbose = True
  
    # 2.) -- create text message ----------------
    message = WebSmsComToolkit.TextMessage(recipient_address_list, message_text_unicode)
#    message = sample_message_binary_sms()
    
    # 3.) -- send message ------------------
    response = client.send(message, max_sms_per_message, is_test)
    
    print "-- Response Object --"
    print "transferId      : " + str(response.transferId)
    print "clientMessageId : " + str(response.clientMessageId)
    print "statusCode      : " + str(response.statusCode)
    print "statusMessage   : " + str(response.statusMessage)
    print "rawContent      : " + str(response.rawContent)
  
  except WebSmsComToolkit.ParameterValidationException, e:
    print "ParameterValidationException caught: " + str(e.message) + "\n"
    
  except WebSmsComToolkit.AuthorizationFailedException, e:
    print "AuthorizationFailedException caught: " + str(e.message) + "\n"
  
  except WebSmsComToolkit.ApiException, e:
    # possibility to handle API status codes e.code
    print "ApiException caught. statusMessage: " + str(e.message) + ", statusCode: " + str(e.code) + "\n"
  
  except WebSmsComToolkit.HttpConnectionException, e:
    print "HttpConnectionException caught: " + str(e.message) + "HTTP Status: " + str(e.code) + "\n"
  
  except WebSmsComToolkit.UnknownResponseException, e:
    print "UnknownResponseException caught: " + str(e.message) + "\n"
    
  except Exception, e:
    print "Exception caught: " , e
    traceback.print_exc(file=sys.stdout)

# END 

def sample_message_binary_sms():
  """
  Working messageContent sample of PDU sms containing content "Zusammengefügt."
  sent as 2 SMS segments: ("Zusammen","gefügt."). 
  First 6 Bytes per segment are sample UDH. See http://en.wikipedia.org/wiki/Concatenated_SMS
  
  $messageContentSegments = array(
      "BQAD/AIBWnVzYW1tZW4=", // 0x05,0x00,0x03,0xfc,0x02,0x01, 0x5a,0x75,0x73,0x61,0x6d,0x6d,0x65,0x6e
      "BQAD/AICZ2Vmw7xndC4="  // 0x05,0x00,0x03,0xfc,0x02,0x02, 0x67,0x65,0x66,0xc3,0xbc,0x67,0x74,0x2e
  );
  """
  import base64
  segment1 = base64.b64encode('\x05\x00\x03\xfc\x02\x01\x5a\x75\x73\x61\x6d\x6d\x65\x6e')
  segment2 = base64.b64encode('\x05\x00\x03\xfc\x02\x02\x67\x65\x66\xc3\xbc\x67\x74\x2e')
  message_content_segments = [segment1, segment2]
  user_data_header_present = True
  
  return WebSmsComToolkit.BinaryMessage(recipient_address_list, message_content_segments, user_data_header_present)


# MAIN
if __name__ == '__main__':
  main()

##----------------------------------------------------------------
## How to overwrite JsonWrapper e.G.: for version below python 2.6
##----------------------------------------------------------------
#original_json_wrapper_class = WebSmsComToolkit.JsonWrapper
# 
#class my_wrapper(object):
#  def __init__(self):
#    print "Overwrote JsonWrapper, this is printed at Client init"
#  def loads(self,response_content):
#    return json.loads(response_content)
#  def dumps(self,message_dict):
#    return json.dumps(message_dict)
#      
# 
#WebSmsComToolkit.JsonWrapper = my_wrapper