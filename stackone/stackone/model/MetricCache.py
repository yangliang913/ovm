from stackone.viewModel.ChartService import ChartService
from datetime import datetime, timedelta
import stackone.core.utils.constants
constants = stackone.core.utils.constants
from stackone.model.GenericCache import GenericCache
from stackone.model.Entity import Entity
from stackone.model import DBSession
import tg
class MetricCache(GenericCache):
    chart_service = ChartService()
    def metric_cache(self, node_id, metric, metric_type, rollup_type, per_type, date1, date2, period, cloud=False):
        now = datetime.now()
        status = False
        ent = DBSession.query(Entity).filter(Entity.entity_id == node_id).one()
        cache_key = (node_id, ent.type.name, metric, period)
        if self.cache.has_key(cache_key):
            cached_time=self.cache[cache_key].get('cached_time')
            if now > cached_time:
                status = True
        else:
            self.check_cache_limit(self.cache)
            status = True

        if status:
            result = self.chart_service.get_metrics_specific_value([node_id], metric, metric_type, rollup_type, per_type, date1, date2, cloud=cloud)
            cache_time = now + timedelta(minutes=int(tg.config.get(constants.CACHE_TIME)))
            self.cache[cache_key]={"cached_time":cache_time,"value":result}
        self.cache[cache_key]['last_accessed'] = now
        return self.cache[cache_key].get('value')




