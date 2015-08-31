__doc__ = 'Sample controller with all its actions protected.'
from tg import expose, flash
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what.predicates import has_permission
from stackone.controllers.ControllerBase import ControllerBase
from stackone.model.CustomPredicates import has_role
__all__ = ['SecureController']
class SecureController(ControllerBase):
    @expose('stackone.templates.index')
    def index(self):
        flash(_("Secure Controller here"))
        return dict(page='index')
    
    @expose('stackone.templates.index')
    def some_where(self):
        return dict(page='some_where')

