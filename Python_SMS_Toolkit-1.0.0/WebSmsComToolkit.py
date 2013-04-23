#
#  WebSmsComToolkit.py
#
#  @author Gerd Reifenauer
#
'''
# WebSmsComToolkit.py
# A python module to send sms messages (text and binary) over api.websms.com Gateway


# Quick Example how to send a text message:
import sys
import traceback
import WebSmsComToolkit

username                = 'your_username'
password                = 'your_password'
gateway_url             = 'https://api.websms.com/'
recipient_address_list  = [4367612345678L]
message_text_unicode    = u'Willkommen zur BusinessPlatform SDK von websms.com! Diese Nachricht enth\u00E4lt 160 Zeichen. Sonderzeichen: \u00E4\u00F6\u00FC\u00DF. Eurozeichen: \u20ac. Das Ende wird nun ausgez\u00E4hlt43210'
max_sms_per_message     = 1
# true: do not send sms for real, just test interface
is_test                 = False

try:
  client  = WebSmsComToolkit.Client(gateway_url, username, password)
  message = WebSmsComToolkit.TextMessage(recipient_address_list, message_text_unicode)
  response = client.send(message, max_sms_per_message, is_test)
  
  print "Transferred/Sent"  
  print "transferId      : " + str(response.transferId)
  print "clientMessageId : " + str(response.clientMessageId)
  
except WebSmsComToolkit.ParameterValidationException, e:
  print "ParameterValidationException caught: " + str(e.message)
    
except WebSmsComToolkit.AuthorizationFailedException, e:
  print "AuthorizationFailedException caught: " + str(e.message)
  
except WebSmsComToolkit.ApiException, e:
  print "ApiException caught. statusMessage: " + str(e.message) + ", statusCode: " + str(e.code)
  
except WebSmsComToolkit.HttpConnectionException, e:
  print "HttpConnectionException caught: " + str(e.message) + " HTTP Status: " + str(e.code)
  
except WebSmsComToolkit.UnknownResponseException, e:
  print "UnknownResponseException caught: " + str(e.message)
    
except Exception, e:
  print "Exception caught: " , e
  traceback.print_exc(file=sys.stdout)
'''

__author__  = 'Gerd Reifenauer'
__version__ = '1.0.0'

import urllib2
import ssl
import re
import base64
import platform
from warnings import warn
from sys import hexversion

try:
  from json import dumps,loads
except ImportError:
  try:
    from simplejson import dumps,loads
  except ImportError:
    pass
    # ImportWarning.
    # Neither 'json' nor 'simplejson' module found.
    # Just install 'simplejson' or consider overwriting WebSmsComToolkit.JsonWrapper() for your own alternative.

class JsonWrapper(object):
  """This class can be used to offer a custom 'loads' and 'dumps' function for JSON by overwriting it
  """
  def __init__(self):
    try:
      dumps
      loads
    except NameError:
      warn("(ImportWarning). Neither 'json' nor 'simplejson' module found. Just install 'simplejson' or consider overwriting WebSmsComToolkit.JsonWrapper() for your own alternative.", Warning)
    
  def loads(self,param):
    return loads(param)
    
  def dumps(self,param):
    return dumps(param)

class ApiException(Exception):
  """ Exception for API Responses that did not return OK.(2000 or 2001)
      contains the API status code
  """
  def __init__(self, message, code):
    self.message = message
    self.code    = code
      
class AuthorizationFailedException(Exception):
  """ Authorization failed. Invalid or inactive Username/Password 
      in e.G.: Basic Authentication
  """
  def __init__(self, message, code = 401):
    self.message = message
    self.code    = code
      
class HttpConnectionException(Exception):
  """ HTTP Connection failed.
  """
  def __init__(self, message, code = 0):
    self.message = message
    self.code    = code
      
class UnknownResponseException(Exception):
  """ Response is unknown
  """
  def __init__(self, message, code = 0):
    self.message = message
    self.code    = code

class ParameterValidationException(Exception):
  """ Some parameter given is invalid
  """
  def __init__(self, message, code = 0):
    self.message = message
    self.code    = code
  

class Message(object):
  """ Abstract Base Message object
      inherited by TextMessage and BinaryMessage
  """
  
  availableSenderAdressType = ['national', 'international', 'alphanumeric', 'shortcode']
  
  def __init__(self, recipients):
    
    self._data = {}
    
    self._data['recipientAddressList']     = []
    self._data['senderAddress']            = None
    self._data['senderAddressType']        = None 
    self._data['sendAsFlashSms']           = None
    self._data['notificationCallbackUrl']  = None
    self._data['clientMessageId']          = None
    self._data['priority']                 = None
    
    self.set_recipient_address_list(recipients);
  
  
  def check_recipient_address_list(self, recipientAddressList):
    """Used internally to check validity of recipient_address_list (list of long)"""
    if not isinstance(recipientAddressList, list): 
      raise ParameterValidationException("Argument 'recipientAddressList' (list) invalid while contructing " . self.__class__.__name__)
    
    for msisdn in recipientAddressList:
      
      if (type(msisdn) != long):
        raise ParameterValidationException("Recipient '" + str(msisdn) + "' is invalid. (must be of type long)");
      if (msisdn <= 9999L or msisdn >= 999999999999999L):
        raise ParameterValidationException("Recipient '" + str(msisdn) + "' is invalid. (max. 15 digits full international MSISDN. Example: 4367612345678)")
    
    return True
  
  def get_recipient_address_list(self):
    """
    Get recipient_address_list (list of long) from message
    Returns: list
    """
    return self._data['recipientAddressList']
    
  def set_recipient_address_list(self, recipients):
    """
    Set recipient_address_list(recipients)
    Params: - recipients:  (list of long containing full international MSISDNs) e.G.: [4367612345678L, long("4912345678")]
    Throws: - ParameterValidationException
    """
    if (self.check_recipient_address_list(recipients)):
      self._data['recipientAddressList'] = recipients
  
  recipient_address_list = property(get_recipient_address_list, set_recipient_address_list)
  
  def data(self):
    """
    Read message data()
    
    Returns: dict representation of Message object (only set values)
    """
    defined_data = {};
    for k, v in self._data.iteritems():
      if (v is not None): defined_data[k] = v
    return defined_data

  def get_sender_address(self):
    """
    Get sender_address from message
    
    Returns: senderAddress of Message object
    """
    return self._data['senderAddress']
    
  def set_sender_address(self, senderAddress):
    """
    Set sender_address
    available sender address is dependend on user account
    
    Params: - senderAddress: string of sender address (msisdn or alphanumeric)
    
    Returns: senderAddress of Message object
    
    Throws: ParameterValidationException
    """
    if (senderAddress is not None):
      if (type(senderAddress) == str):
        self._data['senderAddress'] = senderAddress
      else:
        raise ParameterValidationException("sender_address '" + str(senderAddress) + "' is invalid. Must be string containing numeric or alphanumeric value");
    
    return self._data['senderAddress']
  
  sender_address = property(get_sender_address, set_sender_address)

  def get_sender_address_type(self):
    """
    Get sender_address_type
    
    Returns: a string of ['national', 'international', 'alphanumeric' or 'shortcode']"""
    self._data['senderAddressType']
    
  def set_sender_address_type(self, senderAddressType):
    """
    Set sender_address_type
      available one of: ('national', 'international', 'alphanumeric' or 'shortcode')
    
    Returns: sender_adress_type  set
    
    Throws: ParameterValidationException
    """
    if (senderAdressType in availableSenderAdressType):
      self._data['senderAddressType'] = senderAddressType
    elif (senderAddressType is None):
      self._data['senderAddressType'] = None
    else:
      raise ParameterValidationException("sender_address_type '" + str(senderAddressType) + "' invalid. Must be one of '" + availableSenderAdressType + "'.")
    return self._data['senderAddressType']
  
  sender_address_type = property(get_sender_address_type, set_sender_address_type)

  def get_send_as_flash_sms(self):
    """
    Get send_as_flash_sms
    returns: set sendAsFlashSms of Message object
    """
    return self._data['sendAsFlashSms']
    
  def set_send_as_flash_sms(self,sendAsFlashSms):
    """
    Set send_as_flash_sms(bool)
    
    Params:  boolean: True, False or None
    
    Returns: set sendAsFlashSms of Message object
    """
    if (type (sendAsFlashSms) == bool or sendAsFlashSms is None):
      self._data['sendAsFlashSms'] = sendAsFlashSms
    return self._data['sendAsFlashSms']
  
  send_as_flash_sms = property(get_send_as_flash_sms, set_send_as_flash_sms)
  
  def get_notification_callback_url(self):
    """
    Get notification_callback_url
    Returns: set notificationCallbackUrl of Message object
    """
    return self._data['notificationCallbackUrl']
  
  def set_notification_callback_url(self,notificationCallbackUrl):
    """
    Set notification_callback_url
    
    Params: - notificationCallbackUrl: string of notification callback URI
      customers URI that listens for delivery report notifications
      or replies for this message
      
    Returns: set notificationCallbackUrl of Message object
    
    Throws: ParameterValidationException
    """
    if (type(notificationCallbackUrl) == str or notificationCallbackUrl is None):
      self._data['notificationCallbackUrl'] = notificationCallbackUrl
    else:
      raise ParameterValidationException("notification_callback_url '" + str(notificationCallbackUrl) + "' invalid. Must be string. ")
    return self._data['notificationCallbackUrl']
  
  notification_callback_url = property(get_notification_callback_url, set_notification_callback_url)
  
  def get_client_message_id(self):
    """
    Get client_message_id
    Returns: clientMessaegId set for this Message object
    """
    return self._data['clientMessageId']
    
  def set_client_message_id(self, clientMessageId):
    """
    Set client_message_id(string)
    
    Params: - clientMessageId: string with message id for this message. 
              This message id is returned with the response to the send request
              and used for notifications
    
    Returns: clientMessaegId set for this Message object
    
    Throws: ParameterValidationException
    """
    if (type(clientMessageId) == str or type(clientMessageId) == unicode or clientMessageId is None):
      self._data['clientMessageId'] = clientMessageId
    else:
      raise ParameterValidationException("client_message_id '" + clientMessageId + "' invalid. Must be string.")
    return self._data['clientMessageId']
  
  client_message_id = property(get_client_message_id, set_client_message_id)

  def get_priority(self):
    """
    Get priority
    Returns: priority set for this Message object
    """
    return self._data['priority']
    
  def set_priority(self, priority):
    """
    Set priority(priority)
    
    Params: - priority: message priority as integer (1 to 9)
      (level height must be supported by account settings)
    
    Returns: priority set for this Message object
    
    Throws: ParameterValidationException
    """
    if (type(priority) == int or priority is None):
      self._data['priority'] = priority
    else: 
      raise ParameterValidationException("priority '" + str(priority) + "' invalid. Must be a number.")
    return self._data['priority']
    
  priority = property(get_priority, set_priority)
    
    

class TextMessage(Message):
  """ 
  Text Message Class for sending utf8 text message over Client.
  Compared to the BinaryMessage class, a TextMessage has one messageContent that will be sent as one or multiple sms.
  The 'maxSmsPerMessage' parameter when sending the message limits the generated sms amount
  
  Example for creating message object: 
  
    message = WebSmsComToolkit.TextMessage([4367612345678L,43676123456789L], u'Hallo Welt')
  """
  def __init__(self, recipients, message_content):
    """
    Constructor
    
    Params: - recipients      : list of long 
            - message_content : unicode
            
    Throws ParameterValidationException
    """
    super(TextMessage, self).__init__(recipients)
    self._data['messageContent']           = None
    self.set_message_content(message_content)
  
  
  def get_message_content(self):
    """
    Get message_content
    
    Returns: messageContent set for this Message object
    """
    return self._data['messageContent']
    
  def set_message_content(self, message_content):
    """
    Set message_content(unicode)
    
    Params: - message_content: unicode string
    
    Returns: set messageContent of this Message object
    
    Throws: ParameterValidationException
    """
    if (message_content is not None and type(message_content) == unicode):
      self._data['messageContent'] = message_content
    else:
      raise ParameterValidationException("Invalid message_content for TextMessage. Must be unicode.")
    return self._data['messageContent']
    
  message_content = property(get_message_content, set_message_content)



class BinaryMessage(Message):
  """ 
  Binary Message object for sending binary segments over Client.
  Compared to the TextMessage class, a BinaryMessage contains its message content as a list of message segments.
  Therefore when sending a BinaryMessage 'maxSmsPerMessage' parameter is not supported
  
  Example for creating binary message object:
  
    message = WebSmsComToolkit.BinaryMessage([4367612345678L, 43676123456789L], ["BQAD/AIBWnVzYW1tZW4=","BQAD/AICZ2Vmw7xndC4="], True)
  """
  def __init__(self, recipients, message_content, user_data_header_present = False):
    """
    Constructor
    
    Params: - recipients              : list of long
            - message_content         : list of string/unicode (containing binary encoded with base64) 
            - user_data_header_present: bool
    
    Throws: ParameterValidationException
    """
    super(BinaryMessage, self).__init__(recipients)
    
    self._data['messageContent']           = []
    self._data['userDataHeaderPresent']    = False
  
    if (self.set_message_content(message_content) is None):
      raise ParameterValidationException("message_content is None")
  
    self.set_user_data_header_present(user_data_header_present);
  
  def get_message_content(self):
    """
    Get message_content
    
    Returns: messageContent (list of string/unicode) set for this message obejct
    """
    return self._data['messageContent']
    
  def set_message_content(self, message_content):
    """
    Set message_content
    
    Params: - message_content (list of string/unicode containing base64 encoded binary)
              e.G.: message.message_content(['BQAD/AIBWnVzYW1tZW4=','BQAD/AICZ2Vmw7xndC4=']);
    
    Returns: messageContent set for this Message object
    
    Throws: ParameterValidationException
    """
    if (message_content is not None and type(message_content) == list):
      self._data['messageContent'] = message_content
    else:
      raise ParameterValidationException("message_content parameter must be list of strings containing Base64 encoded Binary")
    return self._data['messageContent']
    
  message_content = property(get_message_content, set_message_content)
  
  
  def get_user_data_header_present(self):
    """
    Get user_data_header_present
    
    Returns: userDataHeaderPresent set for this Message object (bool)
    """
    return self._data['userDataHeaderPresent']
    
  def set_user_data_header_present(self, userDataHeaderPresent):
    """
    Set user_data_header_present(userDataHeaderPresent)
    
    Params: - userDataHeaderPresent: (bool)
              Set it to True when the binary that was base64 encoded contained user a data header
    
    Returns: userDataHeaderPresent set for this Message object
    
    Throws: ParameterValidationException
    """
    if ( type(userDataHeaderPresent) == bool):
      self._data['userDataHeaderPresent'] = userDataHeaderPresent
    else:
      raise ParameterValidationException("user_data_header_present parameter must be bool")
    return self._data['userDataHeaderPresent']
  
  user_data_header_present = property(get_user_data_header_present, set_user_data_header_present)
    

class Response(object):
  """
  Response object returned by Client
  Offers properties:
      - rawContent      : response content of send request (unicode)
      - statusCode      : status code returned from API (int)
      - statusMessage   : description of status code (string)
      - transferId      : the id of the message transfer to the API (unicode)
      - clientMessageId : the message id (unicode)
  """
  def __init__(self, raw_content, statusCode, statusMessage, transferId, clientMessageId = None):
    self.rawContent      = raw_content
    self.statusCode      = statusCode
    self.statusMessage   = statusMessage
    self.transferId      = transferId
    self.clientMessageId = clientMessageId


class Client(object):
  """
  Client used to send sms messages (TextMessage or BinaryMessage objects)
  Create once and send messages with its send() method
  
  Example:
    client = WebSmsComToolkit.Client('http://api.websms.com/', username, password)
  """
  VERSION = "1.0.0"
  
  def __init__(self, url_base, username, password):
    """
    Constructor requiring base url, username and password
    You only need to create the client once.
    """
    
    url_base = re.sub(r'\/+$',r'',url_base)
    
    self.user_agent_string = "Python SDK Client (v" + self.VERSION + ", Python " + platform.python_version() + ", " + platform.platform() + ")"
    
    self.config = {}

    self.config['timeout']          = 10
    self.config['endpoint']         = url_base
    self.config['endpoint_base']    = "/json/smsmessaging"
    self.config['endpoint_text']    = "/text"
    self.config['endpoint_binary']  = "/binary"
    self.config['user']             = username
    self.config['pass']             = password
    self.config['verbose']          = False
  
    ## Error-Messages ##
    self.error_msg = {}
    self.error_msg['internal']  = "An internal error occurred.";
    
    self.json_wrapper = JsonWrapper()
    
  def get_verbose(self):
    """
    Get verbose mode of Client
    
    Returns: verbose mode (bool)
    """
    return self.config['verbose']
  
  def set_verbose(self, bool_verbose):
    """
    Set verbose mode of Client
    
    Params: - bool_verbose (boolean)
    
    Returns: verbose mode set
    """
    if type(bool_verbose) == bool:
      self.config['verbose'] = bool_verbose
      
    return self.config['verbose']
  
  verbose = property(get_verbose, set_verbose, None, "verbose mode")
  
  def get_timeout(self):
    """
    Get timeout of urllib2 client
    
    Returns: seconds (int)
    """
    return self.config['timeout']
  
  def set_timeout(self, seconds):
    """
    Set timeout of urllib2  (default is 10)
    
    !ATTENTION! 
    Will only work for python 2.6+, The optional timeout parameter specifies a timeout in 
    seconds for blocking operations like the connection attempt.
    
    For python <2.6, the global default timeout setting can be used, 
    but are not affected by this timeout
    
    Params: - seconds (int)
    
    Returns: seconds set
    """
    if type(seconds) == int:
      self.config['timeout'] = seconds
      
    return self.config['timeout']
  
  timeout = property(get_timeout, set_timeout)
  
  def _do_request(self, url, content):
    """
    Internally used to send request with urllib2
    """
    base64string = base64.encodestring(
                '%s:%s' % (self.config['user'], self.config['pass']))[:-1]
    authheader =  "Basic %s" % base64string
    
    headers = { 
      'User-Agent'   : self.user_agent_string, 
      'Content-Type' : 'application/json;charset=UTF-8',
      'Authorization': authheader}
        
    data    = content

    req = urllib2.Request(url, data, headers)
    
    if (self.config['verbose']):
      print "-- Request Info --"
      print "Url: "
      print url
      print "\nHeader Items: "
      print req.header_items()
      print "\nData:"
      print req.get_data()
      print "-----------------"
    
    response = None
    
    try:
      if hexversion >= 0x020600F0:
        response = urllib2.urlopen(req, None, self.config['timeout'])
      else:
        response = urllib2.urlopen(req)
    except IOError, e:
      if hasattr(e, 'code'):
        if e.code == 401:
          raise AuthorizationFailedException(e)
        else:
          raise HttpConnectionException("HTTP Error " + str(e.code) + " " + e.read())
      else: 
        raise HttpConnectionException(str(e))
    
    if response is None:
      raise HttpConnectionException("Empty response")
      
    response_content = response.read()
    
    if (self.config['verbose']):
      print "-- Response Info --"
      print "Content:",
      print response_content
      print "-------------------"
      
    json_response = self.json_wrapper.loads(response_content);
    
    return json_response
  
  
  
  def send(self, message_object = None, max_sms_per_message = None, is_test = None):
    """
    Send message to websms.com API
    
    Params: - message_object      : Must be instanceof TextMessage or BinaryMessage
            - max_sms_per_message : int (1-255) )limiting the maximum set sms per message (For TextMessage. Set it to None for BinaryMessage)
            - is_test             : bool indicating if message is a test message (False is default). 
                                    Test Messages will not be sent, but generate a successful response.
    Returns: - response of type Response
    
    Throws: - ParameterValidationException
            - AuthorizationFailedException
            - ApiException
            - HttpConnectionException
            - Exception
    """
    
    if (max_sms_per_message is not None 
    and (type(max_sms_per_message) != int
    or max_sms_per_message < 1 
    or max_sms_per_message == 0)):
      raise ParameterValidationException("max_sms_per_message parameter has to be a number > 0 (or None for binary messages)");
    
    endpoint_url = self.config['endpoint'] + self.config['endpoint_base'];
  
    if (isinstance(message_object, TextMessage)):
      endpoint_url = endpoint_url + self.config['endpoint_text']
    elif (isinstance(message_object, BinaryMessage)):
      if (max_sms_per_message is not None):
        raise ParameterValidationException("BinaryMessage does not support 'max_sms_per_message' parameter. Set to None to prevent this warning.")
      endpoint_url = endpoint_url + self.config['endpoint_binary']
    else:
      raise ParameterValidationException("Invalid message object " + message_object.__class__.__name__ + ", must be of TextMessage or BinaryMessage.")
    
    msg = message_object.data()
    
    if (is_test is not None):
      msg['test'] = is_test
  
    if (max_sms_per_message is not None):
      msg['maxSmsPerMessage'] = max_sms_per_message
    
    json_string = self.json_wrapper.dumps(msg)
  
    json_response = self._do_request(endpoint_url, json_string)
    if (json_response is None):
      raise Exception("No HTTP Response")
    
    statusCode = json_response.get('statusCode',0)
    if (statusCode < 2000 or statusCode > 2001):
      raise ApiException(json_response.get('statusMessage','<missing statusMessage, invalid reponse>'), statusCode)
    
    response = Response(json_response, statusCode, json_response.get('statusMessage'), json_response.get('transferId'), json_response.get('clientMessageId'))
    return response
