import Basic
from stackone.core.utils.utils import to_unicode, to_str, convert_to_CMS_TZ
import stackone.core.utils.constants
constants = stackone.core.utils.constants
import traceback
from stackone.model.Metrics import MetricsService, MetricVMRaw, MetricVMCurr, MetricServerRaw, MetricServerCurr, DataCenterRaw, DataCenterCurr
from stackone.model import DBSession
from stackone.model.TopCache import TopCache
from datetime import datetime, timedelta
import calendar
from tg import session
import tg
#from stackone.cloud.DbModel.VM import CloudVM
#from stackone.cloud.DbModel.VDC import VDC
#from stackone.cloud.DbModel.Account import Account
import logging
LOGGER = logging.getLogger('stackone.viewModel')
class ChartService():
    metrics_service = MetricsService()
    def __init__(self):
        self.service = MetricsService()
        self.manager = Basic.getGridManager()
        self.utcoffset = None

    def metrics(self, auth):
        node_id = '53c7a8bb-fc80-947d-f6c5-ab8f33d1be15'
        node_id = '04e059c6-264d-b1af-77dd-f0a62ae00c34'
        day1 = datetime.now()
        day2 = datetime.now() + timedelta(hours=-8)
        print day1,
        print '--------',
        print day2
        result = self.service.getRawData(node_id, SERVER_RAW, day2, day1)
        data_list = []
        for ls in result:
            print ls[0],
            print '--',
            print ls[1],
            print '--',
            print ls[len(ls) - 1]
            dt = ls[len(ls) - 1]
            millis = convert_to_CMS_TZ(dt)
            print millis
            data_list.append(dict(cpu=ls[0], mem=ls[1], millis=millis))
        return data_list

    def get_chart_data(self, auth, node_id, node_type, metric, period, offset, frm, to, chart_type=None, avg_fdate=None, avg_tdate=None):
        self.utcoffset = timedelta(milliseconds=long(offset))
        print self.utcoffset,
        print datetime.now()
        per_type = 'ROLLUP'
        rollup_type = constants.HOURLY
        time_format = '%H:%M'
        (xlabel, ylabel, label) = ('', '', '')
        minTick = 'day'
        date2 = datetime.now()
        date1 = datetime.now() + timedelta(days=-1)
        if period == constants.CUSTOM:
            per_type = 'ROLLUP'
            date2 = constants.defaultDate + timedelta(milliseconds=long(to))
            date1 = constants.defaultDate + timedelta(milliseconds=long(frm))
            td = date2 - date1
            if td.days > 3:
                rollup_type = constants.DAILY
                minTick = [1, 'day']
                xlabel = 'Time(days)'
                time_format = '%b/%d'
            else:
                if self.timedelta_seconds(td) < 43200:
                    per_type = 'RAW'
                    rollup_type = constants.HOURLY
                    minTick = [30, 'minute']
                    xlabel = 'Time(minutes)'
                    time_format = '%H:%M'
                else:
                    rollup_type = constants.HOURLY
                    minTick = [2, 'hour']
                    xlabel = 'Time(hours)'
                    time_format = '%H:%M'
        else:
            per_type = 'ROLLUP'
            if period == constants.HRS24:
                rollup_type = constants.HOURLY
                minTick = [2, 'hour']
                xlabel = 'Time(hours)'
                time_format = '%H:%M'
                date1 = date2 + timedelta(days=-1)
            else:
                if period == constants.HRS12:
                    per_type = 'RAW'
                    rollup_type = constants.HOURLY
                    minTick = [30, 'minute']
                    xlabel = 'Time(minutes)'
                    time_format = '%H:%M'
                    date1 = date2 + timedelta(seconds=-43200)
                else:
                    if period == constants.DAYS7:
                        rollup_type = constants.DAILY
                        minTick = [1, 'day']
                        xlabel = 'Time(days)'
                        time_format = '%b/%d'
                        date1 = date2 + timedelta(weeks=-1)
                    else:
                        if period == constants.DAYS30:
                            rollup_type = constants.DAILY
                            minTick = [2, 'day']
                            xlabel = 'Time(days)'
                            time_format = '%b/%d'
                            date1 = date2 + timedelta(days=-31)
                        else:
                            if period == constants.DTD:
                                date2 = constants.defaultDate + timedelta(milliseconds=long(to))
                                date2 = date2 + self.utcoffset
                                date1 = datetime(date2.year, date2.month, date2.day) - self.utcoffset
                                date2 = date2 - self.utcoffset
                                rollup_type = constants.HOURLY
                                minTick = [2, 'hour']
                                xlabel = 'Time(hours)'
                                time_format = '%H:%M'
                            else:
                                if period == constants.WTD:
                                    rollup_type = constants.DAILY
                                    minTick = [1, 'day']
                                    xlabel = 'Time(days)'
                                    time_format = '%b/%d'
                                    weekdays = date2.date().weekday()
                                    date1 = datetime(date2.year, date2.month, date2.day) + timedelta(days=-weekdays) - self.utcoffset
                                    diff = (date2 - date1).days
                                    if diff < 3:
                                        minTick = [4, 'hour']
                                        time_format = '%b/%d:%H'
                                        xlabel = 'Time(hours)'
                                    if diff < 1:
                                        minTick = [1, 'hour']
                                        time_format = '%b/%d:%H'
                                        xlabel = 'Time(hours)'
                                else:
                                    if period == constants.MTD:
                                        rollup_type = constants.DAILY
                                        minTick = [1, 'day']
                                        xlabel = 'Time(days)'
                                        time_format = '%b/%d'
                                        date1 = datetime(date2.year, date2.month, date2.day) + timedelta(days=-(date2.day - 1)) - self.utcoffset
                                        diff = (date2 - date1).days
                                        if diff > 8:
                                            minTick = [2, 'day']
                                            xlabel = 'Time(days)'
        hr1 = to_str(date1.hour)
        hr2 = to_str(date2.hour)
        minute1 = to_str(date1.minute)
        minute2 = to_str(date2.minute)
        if date1.hour < 10:
            hr1 = '0' + hr1
        if date2.hour < 10:
            hr2 = '0' + hr2
        dt_str = to_str(date1.year) + '/' + to_str(date1.month) + '/' + to_str(date1.day) + ' ' + hr1 + ':' + minute1 + ' - ' + to_str(date2.year) + '/' + to_str(date2.month) + '/' + to_str(date2.day) + ' ' + hr2 + ':' + minute2
        if metric == constants.METRIC_CPU:
            ylabel = 'cpu(%)'
        else:
            if metric == constants.METRIC_MEM:
                ylabel = 'memory(%)'
            else:
                if metric == constants.METRIC_VMCPU:
                    ylabel = 'vm cpu(%)'
                else:
                    if metric == constants.METRIC_NETWORKIN:
                        ylabel = 'NetworkIn(max)'
                    else:
                        if metric == constants.METRIC_NETWORKOUT:
                            ylabel = 'NetworkOut(max)'
                        else:
                            if metric == constants.METRIC_DISKREAD:
                                ylabel = 'DiskReadBytes(max)'
                            else:
                                if metric == constants.METRIC_DISKWRITE:
                                    ylabel = 'DiskWriteBytes(max)'
        label = dt_str
        series = []
        ymax = 1
        avg = 0.0
        show_avg = False
        if chart_type == constants.TOP5SERVERS:
            metric_type = self.get_metric_type(node_type, per_type)
            series,ymax = self.topNServers(auth, node_id, node_type, metric, metric_type, rollup_type, per_type, date1, date2, period)
        else:
            if chart_type == constants.TOP5VMS:
                metric_type = self.get_metric_type(node_type, per_type)
                series,ymax = self.topNVMS(auth, node_id, node_type, metric, metric_type, rollup_type, per_type, date1, date2, period)
            else:
                if chart_type == constants.COMPARISONCHART:
                    series,ymax = self.comparison_chart(auth, node_id, node_type, metric, -1, rollup_type, per_type, date1, date2, period)
                else:
                    metric_type = self.get_metric_type(node_type, per_type)
                    series,ymax,avg,show_avg = self.chart_series_data(node_id, node_type, metric, metric_type, rollup_type, per_type, date1, date2, avg_fdate, avg_tdate, period)
        if len(series) == 0:
            series.append(dict(data=[], label=''))
        min = convert_to_CMS_TZ(date1)
        max = convert_to_CMS_TZ(date2)
        return dict(time_format=time_format, label=label, xlabel=xlabel, ylabel=ylabel, show_avg=show_avg, avg=avg, min=min, max=max, ymax=ymax, minTick=minTick, series=series)

    def get_metric_detail(self, node_id, node_type, metric, rolluptype, fromdate, todate):
        period = constants.CUSTOM
        per_type = 'ROLLUP'
        if fromdate and todate:
            datetime_format = '%Y-%m-%d %H:%M'
            date2 = datetime.strptime(todate, datetime_format)
            date1 = datetime.strptime(fromdate, datetime_format)
        else:
            date2 = datetime.now()
            date1 = datetime.now() + timedelta(days=-1)
        rollup_type = None
        if rolluptype == 'DAILY':
            rollup_type = constants.DAILY
        elif rolluptype == 'HOURLY':
            rollup_type = constants.HOURLY
        elif rolluptype == 'MONTHLY':
            rollup_type = constants.MONTHLY
        elif rolluptype == 'WEEKLY':
            rollup_type = constants.WEEKLY
        elif rolluptype == 'RAW':
            rollup_type = constants.RAW
            per_type = 'RAW'
        else:
            raise Exception('The given rollup_type is wrong')
        if metric != 'Memory' and metric != 'CPU':
            raise Exception('The given metric is wrong')
        result = []
        series = []
        metric_type = self.get_metric_type(node_type, per_type)
        series,ymax,avg,show_avg = self.chart_series_data(node_id, node_type, metric, metric_type, rollup_type, per_type, date1, date2)
        list = series[0]['data']
        for elem in list:
            use = elem['metric']
            date = elem['millis']
            date = datetime.utcfromtimestamp(date / 1000)
            use = to_str('%6.2f' % float(use))
            result.append(dict(Usage=to_str(use), date=to_str(date)))
        return result

    def chart_series_data(self, node_id, node_type, metric, metric_type, rollup_type, per_type, date1, date2, avg_fdate=None, avg_tdate=None, period=None):
        series = []
        node_ids = []
        node_ids.append(node_id)
        avg = False
        cloud = False
        if node_type in constants.CLOUD_ENT_TYPES:
            cloud = True
        if avg_fdate is not None and avg_tdate is not None:
            avg = True
        result = self.get_metrics_data(node_ids, metric, metric_type, rollup_type, per_type, date1, date2, period, avg, cloud=cloud)
        show_avg = False
        if avg_fdate is not None and avg_tdate is not None:
            avg_tdate = constants.defaultDate + timedelta(milliseconds=long(avg_tdate))
            avg_fdate = constants.defaultDate + timedelta(milliseconds=long(avg_fdate))
            show_avg = True
            if per_type == 'ROLLUP':
                avg = self.service.getRollupAvg(node_id, metric, metric_type, rollup_type, avg_fdate, avg_tdate, cloud=cloud)
            else:
                avg = self.service.getRawAvg(node_id, node_type, metric, metric_type, avg_fdate, avg_tdate, cloud=cloud)
        data_list,ymax = self.get_series_data(result)
        series.append(dict(data=data_list, label=''))
        return (series, ymax, avg, show_avg)

    def topNServers(self, auth, node_id, node_type, metric, metric_type, rollup_type, per_type, date1, date2, period):
        series = []
        series.append(dict(data=[], label=''))
        ymx = 2
        srvrs = []
        if node_type == constants.DATA_CENTER:
            site = auth.get_entity(node_id)
            if site is not None:
                grps = auth.get_child_entities_by_type(site, constants.SERVER_POOL)
                for grp in grps:
                    srvrs.extend(auth.get_child_entities(grp))
        else:
            if node_type == constants.SERVER_POOL:
                grp = auth.get_entity(node_id)
                if grp is None:
                    return (series, ymx)
                srvrs = auth.get_child_entities(grp)
        srvr_ids = []
        srvr_dict = {}
        for srvr in srvrs:
            srvr_ids.append(srvr.entity_id)
            srvr_dict[srvr.entity_id] = srvr.name
        dt2 = datetime.now()
        dt1 = dt2 + timedelta(seconds=-3601)
        data_list = []
        tc = TopCache()
        data_list = tc.get_top_entities(node_id, node_type, metric, 'topNservers', auth, constants.SERVER_RAW, srvr_ids, dt1, dt2)
        if per_type == 'ROLLUP':
            metric_type = constants.SERVER_ROLLUP
        else:
            metric_type = constants.SERVER_RAW
        for data in data_list:
            srvr_ids = []
            srvr_ids.append(data[1])
            result = self.get_metrics_data(srvr_ids, metric, metric_type, rollup_type, per_type, date1, date2, period)
            data_list,ymax = self.get_series_data(result)
            if ymax > ymx:
                ymx = ymax
            series.append(dict(data=data_list, label=srvr_dict[data[1]]))
        return (series, ymx)

    def topNVMS(self, auth, node_id, node_type, metric, metric_type, rollup_type, per_type, date1, date2, period):
        series = []
        ymx = 2
        data_list = []
        vms = []
        cloud = False
        if node_type == constants.VDC:
            cloud = True
            vdc_node = auth.get_entity(node_id)
            if vdc_node is None:
                return (series, ymx)
            for child in vdc_node.children:
                if child.type.name == constants.VDC_VM_FOLDER:
                    vms.extend(child.children)
        vm_ids = []
        vm_dict = {}
        for vm in vms:
            vm_ids.append(vm.entity_id)
            vm_dict[vm.entity_id] = vm.name
        data_list = self.metrics_service.getRawTopMetric(vm_ids, metric, metric_type, date1, date2, 'DESC', 5, cloud=cloud)
        if per_type == 'ROLLUP':
            metric_type = constants.VM_ROLLUP
        else:
            metric_type = constants.VM_RAW
        for data in data_list:
            vm_ids = []
            vm_ids.append(data[1])
            result = self.get_metrics_data(vm_ids, metric, metric_type, rollup_type, per_type, date1, date2, period, cloud=cloud)
            data_list,ymax = self.get_series_data(result)
            if ymax > ymx:
                ymx = ymax
            series.append(dict(data=data_list, label=vm_dict[data[1]]))
        return (series, ymx)

    def comparison_chart(self, auth, node_id, node_type, metric, metric_type, rollup_type, per_type, date1, date2, period):
        series = []
        series.append(dict(data=[], label=''))
        ymx = 2
        node_ids = node_id.split('*')
        node_types = node_type.split('*')
        i = -1
        for node_id in node_ids:
            i += 1
            ent = auth.get_entity(node_id)
#            if ent is None:
#                continue
            node_ids = []
            node_ids.append(node_id)
            cloud = False
            if node_types[i] in constants.CLOUD_ENT_TYPES:
                cloud = True
            metric_type = self.get_metric_type(node_types[i], per_type)
            result = self.get_metrics_data(node_ids, metric, metric_type, rollup_type, per_type, date1, date2, period, cloud=cloud)
            data_list,ymax = self.get_series_data(result)
            if ymax > ymx:
                ymx = ymax
            series.append(dict(data=data_list, label=ent.name))
        return (series, ymx)

    def get_metrics_data(self, node_id, metric, metric_type, rollup_type, per_type, date1, date2, period, avg=False, cloud=False):
        result = []
        if period == constants.CUSTOM or avg == True:
            result = self.get_metrics_specific_value(node_id, metric, metric_type, rollup_type, per_type, date1, date2, cloud=cloud)
        else:
            from stackone.model.MetricCache import MetricCache
            mc = MetricCache()
            result = mc.metric_cache(node_id[0], metric, metric_type, rollup_type, per_type, date1, date2, period, cloud=cloud)
        return result

    def get_metrics_specific_value(self, node_id, metric, metric_type, rollup_type, per_type, date1, date2, cloud=False):
        result = []
        if per_type == 'ROLLUP':
            result = self.service.getRollupMetricData(node_id, metric, metric_type, rollup_type, date1, date2, cloud=cloud)
        else:
            result = self.service.getRawMetricData(node_id, metric, metric_type, date1, date2, cloud=cloud)
        return result

    def get_series_data(self, listdata):
        ymax = 0
        data_list = []
        for ls in listdata:
            dt = ls[1]
            millis = convert_to_CMS_TZ(dt)
            if ls[0] > ymax:
                ymax = ls[0]
            data_list.append(dict(metric=ls[0], millis=millis))
        if ymax > 100:
            ymax = ymax + 10
        else:
            if 100 - ymax <= 10:
                ymax = 100
            else:
                ymax = ymax + 2
        return (data_list, ymax)

    def get_metric_type(self, node_type, per_type):
        nod_type = ''
        if node_type == constants.DATA_CENTER:
            nod_type = 'DATACENTER'
        elif node_type == constants.SERVER_POOL:
            nod_type = 'SERVERPOOL'
        elif node_type == constants.MANAGED_NODE:
            nod_type = 'SERVER'
        elif node_type in [constants.DOMAIN,constants.CLOUD_VM,constants.VDC]:
            nod_type = 'VM'
        metric_type = eval('constants.' + nod_type + '_' + per_type)
        return metric_type

    def timedelta_seconds(self, td):
        return (td.days * 86400000 + td.seconds * 1000 + td.microseconds / 1000) / 1000



