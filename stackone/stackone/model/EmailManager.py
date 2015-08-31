import smtplib
import traceback
import tg
import stackone.core.utils.utils
constants = stackone.core.utils.constants
from stackone.model.DBHelper import DBHelper
from stackone.model import DBSession
from stackone.model.EmailSetup import EmailSetup
from email.MIMEText import MIMEText
from stackone.core.utils import ssmtplib
from stackone.model.Sites import Site
from stackone.model.Entity import Entity, EntityType
from stackone.core.utils.utils import to_str, to_unicode
import logging
LOGGER = logging.getLogger('stackone.model')
class EmailManager():
    def __init__(self):
        pass

    def send_email(self, email, message, subject='', mimetype=None):
        sent = False
        servers = DBSession.query(EmailSetup).all()
        if len(servers) == 0L:
            LOGGER.error('No EmailServers are setup. Can not send e-mail.')
            return False

        for server in servers:
            try:
                self.send_mail(server, email, message, subject, mimetype)
                sent = True

            except Exception as e:
                traceback.print_exc()
                LOGGER.error('Error sending mails:' + to_str(e))

            if sent:
                return True
        return False

        
    def send_mail(self, server, email, message, subject, mimetype='plain'):
        #[NODE: 0&44]
        details = server.credential.cred_details
        server_user_name = details['user_email']
        server_user_psswd = details['password']
        if server_user_name is None or server_user_name == '':
            server_user_name = tg.config.get('email_from')

        message = MIMEText(message, mimetype)
        message['Subject'] = subject
        if server.use_secure == constants.NONSECURE:
            self.send_nonsecure(server.mail_server, int(server.port), server_user_name, email, message.as_string())
        else:
            if server.use_secure == constants.TLS:
                self.send_tls(server.mail_server, int(server.port), server_user_name, server_user_psswd, email, message.as_string())
            else:
                self.send_ssl(server.mail_server, int(server.port), server_user_name, server_user_psswd, email, message.as_string())

        return None

        

    def add_entity(self, name, entity_id, entityType, parent):
        try:
            type = DBHelper().find_by_name(EntityType, entityType)
            e = Entity()
            e.name = name
            e.type = type
            e.entity_id = entity_id
            e.parent = parent
            DBHelper().add(e)

        except Exception as e:
            raise e

        return e


    def send_nonsecure(self, mail_server, port, sender, receivers, msg):
        smtpObj = smtplib.SMTP(mail_server, port)
        smtpObj.sendmail(sender, receivers, msg)
        smtpObj.close()

    def send_tls(self, mail_server, port, sender, password, receivers, msg):
        server = smtplib.SMTP(mail_server, port)
        server.set_debuglevel(False)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender, password)
        server.sendmail(sender, receivers, msg)
        server.close()

        
    def send_ssl(self, mail_server, port, sender, password, receivers, msg):
        server = ssmtplib.SMTP_SSL(mail_server, port)
        server.login(sender, password)
        try:
            server.sendmail(sender, receivers, msg)
        finally:
            server.close()
            
            
    def get_mailservers(self):
        MailSetupRecord = []
        SiteRecord = DBSession.query(Site).filter(Site.name == 'Data Center').first()
        if SiteRecord:
            site_id = SiteRecord.id

        emailsetuprecords = DBHelper().filterby(EmailSetup, [], [EmailSetup.site_id == site_id])

        for emailSetupobj in emailsetuprecords:
            MailSetupRecord.append(dict(MailSetup = emailSetupobj, Creds = emailSetupobj.credential))

        return MailSetupRecord


    def get_emailsetupinfo(self):
        result = []
        emailsetups = DBHelper().get_all(EmailSetup)

        for obj in emailsetups:
            result.append(dict(emailsetup_id = obj.id, servername = obj.mail_server, desc = obj.description, username = obj.credential.cred_details['user_email'], port = obj.port))

        return result


    def delete_emailrecord(self, emailsetup_id):
        emailSetupobj = DBHelper().find_by_id(EmailSetup, emailsetup_id)
        DBHelper().delete(emailSetupobj)
        entity_obj = DBSession.query(Entity).filter(Entity.entity_id == emailsetup_id).first()
        DBHelper().delete(entity_obj)

    def get_emailsetup_details(self, emailsetup_id):
        result = []
        emailSetupobj = DBHelper().find_by_id(EmailSetup, emailsetup_id)
        result.append(dict(emailsetup_id = emailSetupobj.id, servername = emailSetupobj.mail_server, desc = emailSetupobj.description, port = emailSetupobj.port, use_secure = emailSetupobj.use_secure, username = emailSetupobj.credential.cred_details['user_email'], password = emailSetupobj.credential.cred_details['password']))
        return result



__author__ = 'root'
__date__ = '$Jan 18, 2010 5:57:18 PM$'
if __name__ == '__main__':
    print 'Hello'

