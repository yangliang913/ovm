from datetime import datetime, timedelta
import stackone.core.utils.constants
constants = stackone.core.utils.constants
from stackone.model.Metrics import MetricsService
from stackone.model.GenericCache import GenericCache
import tg

class TopCache(GenericCache):
    service = MetricsService()
    def get_top_entities(self, node_id, node_type, metric, top_type, auth, metric_type, ids, date1, date2, cloud=False):
        now = datetime.now()
        status = False
        user_id = auth.user_name
        top_cache = self.get_top_value(user_id)
        usage_list = []
        cache_key = (node_id, node_type, metric, top_type)

        if top_cache.has_key(cache_key):
            cache_ids=[]
            for data in top_cache[cache_key].get('value'):
                cache_ids.append(data[1])

            diff_list=[item for item in cache_ids if  item not in ids]
            cached_time=top_cache[cache_key].get("cached_time")
            if (now > cached_time) or len(diff_list) > 0:
                status = True
        else:
            status = True
        if status:
            cache_time=now+timedelta(minutes=int(tg.config.get(constants.CACHE_TIME)))
            data_list = self.service.getRawTopMetric(ids, metric, metric_type, date1, date2, 'DESC', 5, cloud)
            if len(data_list) > 0:
                self.check_cache_limit(top_cache)
            top_cache[cache_key]={"cached_time":cache_time,"value":data_list}
        top_cache[cache_key]['last_accessed'] = now
        self.user_cache[user_id].update({cache_key:top_cache[cache_key]})
        if len(ids) == 0 and self.user_cache.has_key(user_id):
            user=self.user_cache[user_id]
            if user.has_key(cache_key):
                self.user_cache[user_id][cache_key]["value"]=[]

        usage_list=self.user_cache[user_id][cache_key].get("value",[]) 
        if len(usage_list) == 0:
            del self.user_cache[user_id][cache_key]
        return usage_list

        



    def get_top_value(self, user_id):
        if not self.user_cache.has_key(user_id):
            self.user_cache[user_id] = {}

        top_cache = self.user_cache.get(user_id, {})
        return top_cache


    def delete_usercache(self, auth):
        user_id = auth.user_name
        if self.user_cache.has_key(user_id):
            del self.user_cache[user_id]


