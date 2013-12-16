comlink
=======

Community linkages via email and forum-like interfaces

In the interest of shipping more quickly, we have made certain assumptions about the interlink mailing lists which may or may not suit everyone's needs.

- the reply-to address for mail from a list is the original sender, not the entire list
- attachments are neither saved nor sent to the list, but a removal note is appended to the message
- incoming messages are parsed for a single text message and a single html message (not multiple MIME messages)
- you can set the frequency of mail fetching by changing the value in CELERYBEAT_SCHEDULE in your settings.py or local_settings.py
- loops and bounces are silently dropped
- any email sent to a list which is not in a subscriber's user or membership record is moderated
- the sender of a message receives a copy of the message like any other subscriber


installation
===

* add to your requirements.txt file: `git+https://git@github.com/opendoor/comlink.git`
* re-run pip `install -r requirements.txt`
* add 'comlink' to your settings.py file, under INSTALLED_APPS
* create a mailgun account and set up your MX records as directed in their
  instructions for sending and receiving. 
* add MAILGUN_API_KEY and LIST_DOMAIN to your settings.py or local_settings.py.
  LIST_DOMAIN is the domain regstered with mailgun that you wish to send and
  receive via. 





