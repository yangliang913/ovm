from stackone.model.LDAPManager import LDAPManager
class stackoneLDAPAuthenticator():
	def validate_password(self, user_name, password):
		return LDAPManager().validate_password(user_name, password)



