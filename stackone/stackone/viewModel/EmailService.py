from stackone.core.utils.utils import constants, getHexID
from stackone.core.utils.utils import to_unicode, to_str
import stackone.core.utils.constants
constants = stackone.core.utils.constants
import traceback
from stackone.model import DBSession
from stackone.model.EmailSetup import EmailSetup
from stackone.model.Sites import Site
from datetime import datetime, date
import smtplib
from stackone.core.utils import ssmtplib
from email.MIMEText import MIMEText
from tg import session
from stackone.model.auth import User
import time
from stackone.model.Credential import Credential
from stackone.model.Entity import Entity, EntityType
from stackone.model.EmailManager import EmailManager
import transaction
import logging
LOGGER = logging.getLogger('stackone.model')
NONSECURE = 1
TLS = 2
SSL = 3
def ct_time():
    return datetime.now().ctime()

class EmailService():
    def __init__(self):
        self.sender = None
        self.receivers = None
        self.message = 'Test Message'
        self.mail_server = None
        self.port = None
        self.description = None
        self.secure_type = None
        self.text_subtype = 'plain'
        self.content = '\\Test message Send on ' + to_str(ct_time())
        self.msg = MIMEText(self.content, self.text_subtype)
        self.subject = 'Test'
        self.msg['Subject'] = self.subject

    def save_email_setup_details(self, desc, servername, port, useremail, password, secure):
        SiteRecord = DBSession.query(Site).filter(Site.name == 'Data Center').first()
        if SiteRecord:
            site_id = SiteRecord.id
            EmailRecord = DBSession.query(EmailSetup).filter(EmailSetup.site_id == site_id).filter(EmailSetup.mail_server == servername).first()
            if EmailRecord:
                return dict(success=True, msg='Duplicaate Record found in list')
            else:
                email_setup_obj = EmailSetup(servername, desc, port, secure, site_id, useremail, password)
                DBSession.add(email_setup_obj)
                emailsetupid = email_setup_obj.getEmailSetupId()
                EmailManager().add_entity(to_unicode(servername), emailsetupid, to_unicode(constants.EMAIL), None)
                return dict(success=True, msg='New Record Added Sucessfully')

    def update_email_setup_details(self, desc, servername, port, useremail, password, secure):
        emaildetails = DBSession.query(EmailSetup).filter(EmailSetup.mail_server == servername).first()
        if emaildetails:
            emaildetails.description = desc
            emaildetails.port = port
            emaildetails.use_secure = secure
            emaildetails.credential.cred_details['user_email'] = useremail
            emaildetails.credential.cred_details['password'] = password
            return dict(success=True, msg='Record updated sucessfully')
        else:
            return dict(success=False, msg='Record updation failed')

    def send_test_email(self, desc, servername, port, useremail, password, secure):
        self.sender = useremail
        Record = DBSession.query(User.email_address).filter(User.user_name == 'admin').first()
        self.receivers = Record.email_address
        self.mail_server = servername
        if port:
            self.port = int(port)
        self.secure_type = int(secure)
        self.password = password
        self.subject = 'Test Email'
        self.content = "\Test message Sent on " + to_str(ct_time())
        self.msg = MIMEText(self.content, self.text_subtype)
        self.msg['Subject'] = 'stackone Test Email'

        try:
            if self.secure_type == NONSECURE:
                EmailManager().send_nonsecure(servername, self.port, useremail, Record.email_address, self.msg.as_string())
            else:
                if self.secure_type == TLS:
                    EmailManager().send_tls(servername, self.port, useremail, password, Record.email_address, self.msg.as_string())
                else:
                    EmailManager().send_ssl(servername, self.port, useremail, password, Record.email_address, self.msg.as_string())

        except Exception as ex:
            LOGGER.error('Error sending mails:' + to_str(ex).replace("'", ''))
            raise ex

        message = 'mail send to ' + Record.email_address
        return message

    def get_mailservers(self):
        try:
            MailSetupRecord = EmailManager().get_mailservers()
            return MailSetupRecord
        except Exception as e:
            raise e

    def send_email_to_client(self, msg, receiver):
        self.receivers = receiver
        self.content = msg
        emailservers = self.get_mailservers()
        for eachmailserver in emailservers:
            if eachmailserver:
                self.mail_server = eachmailserver['MailSetup'].mail_server
                self.port = int(eachmailserver['MailSetup'].port)
                self.secure_type = int(eachmailserver['MailSetup'].use_secure)
                self.cred_details = eachmailserver['Creds'].cred_details
                self.password = self.cred_details['password']
                self.sender = self.cred_details['user_email']
                result = False
                if self.secure_type == NONSECURE:
                    result = EmailManager().send_nonsecure(self.mail_server, self.port, self.sender, receiver, msg)
                else:
                    if self.secure_type == TLS:
                        result = EmailManager().send_tls(self.mail_server, self.port, self.sender, self.password, receiver, msg)
                    else:
                        result = EmailManager().send_ssl(self.mail_server, self.port, self.sender, self.password, receiver, msg)
                if result == True:
                    return 'Test mail sent from ' + eachmailserver['MailSetup'].mail_server

    def send_email_to_user(self, msg):
        self.msg = msg
        curr_user_id = session.get('userid')
        userRecord = DBSession.query(User.email_address).filter(User.user_name == curr_user_id).first()
        if userRecord:
            self.receivers = userRecord.email_address
        emailservers = self.get_mailservers()
        for eachmailserver in emailservers:
            if eachmailserver:
                self.mail_server = eachmailserver['MailSetup'].mail_server
                self.port = int(eachmailserver['MailSetup'].port)
                self.secure_type = int(eachmailserver['MailSetup'].use_secure)
                self.cred_details = eachmailserver['Creds'].cred_details
                self.password = self.cred_details['password']
                self.sender = self.cred_details['user_email']
                result = False
                if self.secure_type == NONSECURE:
                    result = EmailManager().send_nonsecure(self.mail_server, self.port, self.sender, self.receivers, msg)
                else:
                    if self.secure_type == TLS:
                        result = EmailManager().send_tls(self.mail_server, self.port, self.sender, self.password, self.receivers, msg)
                    else:
                        result = EmailManager().send_ssl(self.mail_server, self.port, self.sender, self.password, self.receivers, msg)
                if result == True:
                    return 'Test mail sent from ' + eachmailserver['MailSetup'].mail_server

    def get_emailsetupinfo(self):
        try:
            result = EmailManager().get_emailsetupinfo()
            return result
        except Exception as e:
            raise e
            
        
    def delete_emailrecord(self, emailsetup_id):
        try:
            EmailManager().delete_emailrecord(emailsetup_id)
        except Exception as e:
            raise e
    def get_emailsetup_details(self, emailsetup_id):
        try:
            result = None
            result = EmailManager().get_emailsetup_details(emailsetup_id)
        except Exception as e:
            raise e
        return result



