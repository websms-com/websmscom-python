websmscom-python
=========
### lightweight python client to send SMS through websms.com

What is it?
-----------
A lightweight Python-client-library for using websms.com SMS services.
Reduces the complexity of network-communication between client and SMS gateway, 
to help business-customer save time and money for focusing on their business logic.


#### Features:

 * Text Messages
 * Binary Messages
 * Confirmation of Delivery
 * Answers to SMS can be forwarded
 * Usable in modules and from command line

See [websms.com](http://websms.com) website to [register](https://www.websms.com/websms-testen/) for an account.

For general API specification of the server (programming language independent) visit: [https://api.websms.com](https://api.websms.com)

Documentation
-------------
The documentation available as of the date of this release is included 
in send_sms.py and WebSmsComToolkit.py.
See also WebsmsComToolkit.html or use `pydoc -w ./WebSmsComToolkit.py`

Installation
------------
Read INSTALL file

Contact
-------
For any further questions into detail the contact-email is sdk@websms.com

Changelog
---------
* Version 1.0.2: fixed senderAddressType setter
* Version 1.0.1: fixed senderAddressType getter
* Version 1.0.0: Basic text- and binary-sms-sending.
