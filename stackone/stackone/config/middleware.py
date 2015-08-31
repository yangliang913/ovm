from stackone.config.app_cfg import base_config
from stackone.config.environment import load_environment
from stackone.core.utils.utils import update_vm_status, populate_custom_fence_resources, reset_transient_state, storage_stats_data_upgrade, unreserve_disks_on_cms_start, init_firewall_for_all_csep, add_deployment_stats_task
from stackone.core.services.core import ServiceCentral
from stackone.model.Metrics import MetricsService
from stackone.model import zopelessmaker
from stackone.viewModel import Basic
from stackone.core.utils.NodeProxy import Node
import stackone.core.utils.constants
import tg
import os
import atexit
import sys
__all__ = ['make_app']
make_base_app = base_config.setup_tg_wsgi_app(load_environment)
def make_app(global_conf, full_stack=True, **app):
	app = make_base_app(global_conf, full_stack=True, **app)
	license_file = tg.config.get(stackone.core.utils.constants.license_file)
	try:
		init_firewall_for_all_csep()
	except Exception as e:
		print 'Error while ensuring firewall ',
		print e
	try:
		update_vm_status()
	except Exception as e:
		print 'Error while updating the vm status to None ',
		print e
	try:
		Basic.getImageStore().init_scan_dirs()
	except Exception as e:
		print 'Error while scanning the image store ',
		print e
	try:
		populate_custom_fence_resources(Basic.getManagedNode(), True)
	except Exception as e:
		print 'Error while populating custom fence resources ',
		print e
	try:
		reset_transient_state()
	except Exception as e:
		print 'Error while resetting the state ',
		print e
	try:
		storage_stats_data_upgrade()
	except Exception as e:
		print 'Error while recomputing storage stats ',
		print e
	try:
		unreserve_disks_on_cms_start()
	except Exception as e:
		print 'Error while unreserving storage disks ',
		print e
	sc = ServiceCentral(zopelessmaker)
	sc.start()
	atexit.register(sc.quit)
	base_config.stackone_service_central = sc
	MetricsService().init_mappers()
	#Node.use_bash_timeout = eval(tg.config.get('use_bash_timeout'))
	Node.default_bash_timeout = tg.config.get('bash_default_timeout')
	Node.bash_dir = os.path.join(tg.config.get('stackone_cache_dir'), 'common/scripts')
	Node.local_bash_dir = tg.config.get('common_script')
	try:
		add_deployment_stats_task()
	except Exception,ex:
		print 'Error while adding deployment stats task'
		print ex	
	return app

