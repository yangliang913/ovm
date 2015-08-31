__doc__ = 'Fallback controller.'
from stackone.lib.base import BaseController
__all__ = ['TemplateController']
class TemplateController(BaseController):
	__doc__ = "\n    The fallback controller for stackone.\n    \n    By default, the final controller tried to fulfill the request\n    when no other routes match. It may be used to display a template\n    when all else fails, e.g.::\n    \n        def view(self, url):\n            return render('/%s' % url)\n    \n    Or if you're using Mako and want to explicitly send a 404 (Not\n    Found) response code when the requested template doesn't exist::\n    \n        import mako.exceptions\n        \n        def view(self, url):\n            try:\n                return render('/%s' % url)\n            except mako.exceptions.TopLevelLookupException:\n                abort(404)\n    \n    "
	def view(self, url):
		abort(404L)



