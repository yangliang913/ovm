from tg import session
from datetime import datetime
class SessionManager(object):
    def getSession(self):
        id = session.id
        if session.has_key('sessionInfo'):
            return session['sessionInfo']
        sessionInfo = SessionInfo(id)
        session['sessionInfo'] = sessionInfo
        session.save()
        return sessionInfo




class SessionInfo(object):
    def __init__(self, id):
        self.id = id
        self.isValid = 0
        self.username = ''
        self.password = ''
        self.group = ''
        self.role = ''

    def login(self, username, password, id):
        self.username = username
        self.password = password
        self.role = 'superUser'
        self.group = 'superGroup'
        self.isValid = 1
        self.id = id
        session['sessionInfo'] = self
        session.save()

    def logout(self):
        self.isValid = 0
        session.delete()

    def toXml(self, xml):
        sess = xml.createElement('sessionInfo')
        sess.setAttribute('id', str(self.id))
        sess.setAttribute('valid', str(self.isValid))
        sess.setAttribute('username', self.__getattribute__('username'))
        return sess



