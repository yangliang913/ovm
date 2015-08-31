from repoze.what.predicates import Predicate
from tg import request, session
from stackone.model.auth import Role, User
from stackone.model.DBHelper import DBHelper
class has_role(Predicate):
	message = 'The current user must have %(role)s role.'
	def __init__(self, role, **kwargs):
		self.role = role
		super(has_role, self).__init__(**kwargs)

	def evaluate(self, environ, credentials):
		if not request.identity:
			self.unmet()

		userid = request.identity['repoze.who.userid']
		u = User.by_user_name(userid)
		r = DBHelper().find_by_name(Role, self.role)
		if not u.has_role(r):
			self.unmet()




class authenticate(Predicate):
	message = 'SessionExpired.'
	def __init__(self, **kwargs):
		super(authenticate, self).__init__(**kwargs)

	def evaluate(self, environ, credentials):
		if session.get('userid') is None:
			self.unmet()
		return None




