
 
                  W E B S M S . C O M   P Y T H O N   T O O L K I T 


What is it?
-----------

  A lightweight Python-client-library for using websms.com SMS services.
  Reduces the complexity of network-communication between client and SMS gateway, 
  to help business-customer save time and money for focusing on their business logic.

Features:
---------

 * Text Messages
 * Binary Messages
 * Confirmation of Delivery
 * Answers to SMS can be forwarded
 * Usable in modules and from command line

See [websms.com](http://websms.com) website to [register](https://account.websms.com/#/) for an account.

For general API specification of the server (programming language independent) visit: [https://api.websms.com](https://api.websms.com)

Install
-------------
  Read [INSTALL.md](INSTALL.md) file

Example
-------
See [send_sms.py](send_sms.py) for an example on how to send text and binary messages

Build (optional)
-----
You can either use/install the version in [/WebSmsComToolkit-1.0.2](/WebSmsComToolkit-1.0.2) or 
build your own version: `python setup.py sdist`

See [create_dist.sh](create_dist.sh)

Documentation
-------------
  The documentation available as of the date of this release is included 
  in send_sms.py and WebSmsComToolkit.py.
  See also WebsmsComToolkit.html or use `pydoc -w ./WebSmsComToolkit.py`
  
Contact
-------
  For any further questions into detail the contact-email is developer@websms.com

Contributors
------------

* Gerd Reifenauer (Author) [@reifi](https://github.com/reifi)
   
Changelog
---------
* Version 1.0.2: fixed senderAddressType setter
* Version 1.0.1: fixed senderAddressType getter
* Version 1.0.0: Basic text- and binary-sms-sending.
