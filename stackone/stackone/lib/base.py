__doc__ = 'The base Controller API.'
from tg import TGController, tmpl_context
from tg.render import render
from tg import request
from pylons.i18n import _, ungettext, N_
from tw.api import WidgetBunch
import stackone.model as model
__all__ = ['Controller', 'BaseController']
class BaseController(TGController):
    __doc__ = '\n    Base class for the controllers in the application.\n\n    Your web application should have one of these. The root of\n    your application is used to compute URLs used by your app.\n\n    '
    def __call__(self, environ, start_response):
        request.identity = request.environ.get('repoze.who.identity')
        tmpl_context.identity = request.identity
        return TGController.__call__(self, environ, start_response)



