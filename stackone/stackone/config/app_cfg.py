from tg.configuration import AppConfig
import stackone
from stackone import model
from stackone.lib import app_globals, helpers
from repoze.who.plugins.basicauth import BasicAuthPlugin
base_config = AppConfig()
base_config.renderers = []
base_config.package = stackone
base_config.default_renderer = 'genshi'
base_config.renderers.append('genshi')
base_config.variable_provider = helpers.add_global_tmpl_vars
base_config.use_sqlalchemy = True
base_config.model = stackone.model
base_config.DBSession = stackone.model.DBSession
base_config.auth_backend = 'sqlalchemy'
base_config.sa_auth.dbsession = model.DBSession
base_config.sa_auth.user_class = model.User
base_config.sa_auth.group_class = model.Group
base_config.sa_auth.permission_class = model.Permission
base_config.sa_auth.form_plugin = BasicAuthPlugin('stackone')
base_config.sa_auth.post_login_url = '/post_login'
base_config.sa_auth.post_logout_url = '/post_logout'
base_config.sa_auth.cookie_secret = 'damm1t'
