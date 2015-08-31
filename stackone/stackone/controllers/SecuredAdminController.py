from tgext.admin import AdminController
from stackone.model.CustomPredicates import has_role
class SecuredAdminController(AdminController):
	allow_only = has_role(u'admin')


