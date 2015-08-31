import tg
import time
import datetime
import calendar
from math import sqrt
from sqlalchemy import func
from stackone.core.utils.utils import to_unicode, to_str, getHexID, get_dbtype, p_task_timing_start, p_task_timing_end
from stackone.core.utils.constants import DOMAIN
from datetime import datetime, date, timedelta
from stackone.model.ManagedNode import ManagedNode
from stackone.model import DBSession, metadata, DeclarativeBase
from sqlalchemy.types import Integer, Unicode, String, DateTime
from sqlalchemy.orm import mapper, relation, sessionmaker, column_property
from sqlalchemy.schema import Index
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Float
from stackone.core.utils.constants import *
import stackone.core.utils.utils
import transaction
constants = stackone.core.utils.constants
from stackone.model.VM import VM
import logging
from sqlalchemy.schema import Index, Sequence
from stackone.model.LockManager import LockManager
LOGGER = logging.getLogger('stackone.model')
MTR_LOGGER = logging.getLogger('METRICS_TIMING')
PURGE_TYPE = 0L
PURGE_DATE = 1L
class Metrics(DeclarativeBase):
    __tablename__ = 'metrics'
    id = Column(Unicode(50), primary_key=True)
    metric_type = Column(Integer)
    state = Column(Unicode(50))
    entity_id = Column(Unicode(50))
    cloud_entity_id = Column(Unicode(50))
    icol1 = Column(Integer)
    icol2 = Column(Integer)
    icol3 = Column(Integer)
    icol4 = Column(Integer)
    icol5 = Column(Integer)
    icol6 = Column(Integer)
    icol7 = Column(Integer)
    icol8 = Column(Integer)
    icol9 = Column(Integer)
    icol10 = Column(Integer)
    icol11 = Column(Integer)
    icol12 = Column(Integer)
    icol13 = Column(Integer)
    fcol1 = Column(Float)
    fcol2 = Column(Float)
    fcol3 = Column(Float)
    fcol4 = Column(Float)
    fcol5 = Column(Float)
    fcol6 = Column(Float)
    fcol7 = Column(Float)
    fcol8 = Column(Float)
    fcol9 = Column(Float)
    fcol10 = Column(Float)
    fcol11 = Column(Float)
    fcol12 = Column(Float)
    fcol13 = Column(Float)
    fcol14 = Column(Float)
    fcol15 = Column(Float)
    fcol16 = Column(Float)
    fcol17 = Column(Float)
    fcol18 = Column(Float)
    fcol19 = Column(Float)
    fcol20 = Column(Float)
    fcol21 = Column(Float)
    fcol22 = Column(Float)
    fcol23 = Column(Float)
    fcol24 = Column(Float)
    fcol25 = Column(Float)
    cdate = Column(DateTime(timezone=True))
    def __init__(self):
        pass



Index('m_eid_rype_cdate', Metrics.entity_id, Metrics.metric_type, Metrics.cdate)
Index('m_rype_cdate', Metrics.metric_type, Metrics.cdate)
class MetricsCurr(DeclarativeBase):
    __tablename__ = 'metrics_curr'
    id = Column(Unicode(50), primary_key=True)
    metric_type = Column(Integer)
    state = Column(Unicode(50))
    entity_id = Column(Unicode(50))
    cloud_entity_id = Column(Unicode(50))
    icol1 = Column(Integer)
    icol2 = Column(Integer)
    icol3 = Column(Integer)
    icol4 = Column(Integer)
    icol5 = Column(Integer)
    icol6 = Column(Integer)
    icol7 = Column(Integer)
    icol8 = Column(Integer)
    icol9 = Column(Integer)
    icol10 = Column(Integer)
    icol11 = Column(Integer)
    icol12 = Column(Integer)
    icol13 = Column(Integer)
    fcol1 = Column(Float)
    fcol2 = Column(Float)
    fcol3 = Column(Float)
    fcol4 = Column(Float)
    fcol5 = Column(Float)
    fcol6 = Column(Float)
    fcol7 = Column(Float)
    fcol8 = Column(Float)
    fcol9 = Column(Float)
    fcol10 = Column(Float)
    fcol11 = Column(Float)
    fcol12 = Column(Float)
    fcol13 = Column(Float)
    fcol14 = Column(Float)
    fcol15 = Column(Float)
    fcol16 = Column(Float)
    fcol17 = Column(Float)
    fcol18 = Column(Float)
    fcol19 = Column(Float)
    fcol20 = Column(Float)
    fcol21 = Column(Float)
    fcol22 = Column(Float)
    fcol23 = Column(Float)
    fcol24 = Column(Float)
    fcol25 = Column(Float)
    cdate = Column(DateTime(timezone=True))
    def __init__(self):
        pass



Index('m_ct_eid_rype_cdate', MetricsCurr.entity_id, MetricsCurr.metric_type, MetricsCurr.cdate)
class MetricsArch(DeclarativeBase):
    __tablename__ = 'metrics_arch'
    id = Column(Unicode(50), primary_key=True)
    metric_type = Column(Integer)
    rollup_type = Column(Integer)
    state = Column(Unicode(50))
    entity_id = Column(Unicode(50))
    cloud_entity_id = Column(Unicode(50))
    icol1 = Column(Integer)
    icol2 = Column(Integer)
    icol3 = Column(Integer)
    icol4 = Column(Integer)
    icol5 = Column(Integer)
    icol6 = Column(Integer)
    icol7 = Column(Integer)
    icol8 = Column(Integer)
    icol9 = Column(Integer)
    icol10 = Column(Integer)
    icol11 = Column(Integer)
    icol12 = Column(Integer)
    icol13 = Column(Integer)
    icol14 = Column(Integer)
    icol15 = Column(Integer)
    icol16 = Column(Integer)
    icol17 = Column(Integer)
    icol18 = Column(Integer)
    icol19 = Column(Integer)
    icol20 = Column(Integer)
    fcol1 = Column(Float)
    fcol2 = Column(Float)
    fcol3 = Column(Float)
    fcol4 = Column(Float)
    fcol5 = Column(Float)
    fcol6 = Column(Float)
    fcol7 = Column(Float)
    fcol8 = Column(Float)
    fcol9 = Column(Float)
    fcol10 = Column(Float)
    fcol11 = Column(Float)
    fcol12 = Column(Float)
    fcol13 = Column(Float)
    fcol14 = Column(Float)
    fcol15 = Column(Float)
    fcol16 = Column(Float)
    fcol17 = Column(Float)
    fcol18 = Column(Float)
    fcol19 = Column(Float)
    fcol20 = Column(Float)
    fcol21 = Column(Float)
    fcol22 = Column(Float)
    fcol23 = Column(Float)
    fcol24 = Column(Float)
    fcol25 = Column(Float)
    fcol26 = Column(Float)
    fcol27 = Column(Float)
    fcol28 = Column(Float)
    fcol29 = Column(Float)
    fcol30 = Column(Float)
    fcol31 = Column(Float)
    fcol32 = Column(Float)
    fcol33 = Column(Float)
    fcol34 = Column(Float)
    fcol35 = Column(Float)
    fcol36 = Column(Float)
    fcol37 = Column(Float)
    fcol38 = Column(Float)
    fcol39 = Column(Float)
    fcol40 = Column(Float)
    fcol41 = Column(Float)
    fcol42 = Column(Float)
    fcol43 = Column(Float)
    fcol44 = Column(Float)
    fcol45 = Column(Float)
    fcol46 = Column(Float)
    fcol47 = Column(Float)
    fcol48 = Column(Float)
    fcol49 = Column(Float)
    fcol50 = Column(Float)
    fcol51 = Column(Float)
    fcol52 = Column(Float)
    fcol53 = Column(Float)
    fcol54 = Column(Float)
    fcol55 = Column(Float)
    fcol56 = Column(Float)
    fcol57 = Column(Float)
    fcol58 = Column(Float)
    fcol59 = Column(Float)
    fcol60 = Column(Float)
    fcol61 = Column(Float)
    fcol62 = Column(Float)
    fcol63 = Column(Float)
    fcol64 = Column(Float)
    fcol65 = Column(Float)
    fcol66 = Column(Float)
    fcol67 = Column(Float)
    fcol68 = Column(Float)
    fcol69 = Column(Float)
    fcol70 = Column(Float)
    fcol71 = Column(Float)
    fcol72 = Column(Float)
    fcol73 = Column(Float)
    fcol74 = Column(Float)
    fcol75 = Column(Float)
    fcol76 = Column(Float)
    fcol77 = Column(Float)
    fcol78 = Column(Float)
    fcol79 = Column(Float)
    fcol80 = Column(Float)
    fcol81 = Column(Float)
    fcol82 = Column(Float)
    fcol83 = Column(Float)
    fcol84 = Column(Float)
    fcol85 = Column(Float)
    fcol86 = Column(Float)
    fcol87 = Column(Float)
    fcol88 = Column(Float)
    fcol89 = Column(Float)
    fcol90 = Column(Float)
    fcol91 = Column(Float)
    fcol92 = Column(Float)
    fcol93 = Column(Float)
    fcol94 = Column(Float)
    fcol95 = Column(Float)
    fcol96 = Column(Float)
    fcol97 = Column(Float)
    fcol98 = Column(Float)
    fcol99 = Column(Float)
    fcol100 = Column(Float)
    fcol101 = Column(Float)
    cdate = Column(DateTime(timezone=True))
    def __init__(self):
        pass



Index('m_ar_eid_rype_cdate', MetricsArch.entity_id, MetricsArch.metric_type, MetricsArch.rollup_type, MetricsArch.cdate)
class rollupStatus(DeclarativeBase):
    __tablename__ = 'rollup_status'
    id = Column(Integer, Sequence('rollupstid_seq'), primary_key=True)
    last_rollup_time = Column('last_rollup_time', DateTime(timezone=True))
    rollup_type = Column('rollup_type', Integer)
    entity_id = Column('entity_id', Unicode(50))
    def __init__(self):
        pass



Index('rlupstat_eid_rtype', rollupStatus.entity_id, rollupStatus.rollup_type)
class PurgeConfiguration(DeclarativeBase):
    __tablename__ = 'purge_config'
    id = Column(Integer, Sequence('prgcnfid_seq'), primary_key=True)
    entity_id = Column('entity_id', Unicode(50))
    data_type = Column('data_type', Integer)
    retention_days = Column('retention_days', Integer)
    def __init__(self):
        pass



Index('prgeconfig_eid', PurgeConfiguration.entity_id)
class DataCenterRaw(object):
    def __init__(self):
        self.id = getHexID()
        self.entity_id = None
        self.state = None
        self.metric_type = constants.DATACENTER_RAW
        self.cdate = None
        self.cpu_util = None
        self.mem_util = None
        self.vbds = None
        self.vbd_oo = None
        self.vbd_rd = None
        self.vbd_wr = None
        self.net = None
        self.net_tx = None
        self.net_rx = None
        self.gb_local = None
        self.gb_poolused = None
        self.gb_pooltotal = None

    def __repr__(self):
        return '( DATA CENTER ' + self.entity_id + ',' + to_str(self.state) + ',' + to_str(self.metric_type) + ',' + to_str(self.cdate) + ',' + to_str(self.cpu_util) + ',' + to_str(self.mem_util) + ',' + to_str(self.vbds) + ',' + to_str(self.vbd_oo) + ',' + to_str(self.vbd_rd) + ',' + to_str(self.vbd_wr) + ',' + to_str(self.net) + ',' + to_str(self.net_tx) + ',' + to_str(self.net_rx) + ',' + to_str(self.gb_local) + ',' + to_str(self.gb_poolused) + ',' + to_str(self.gb_pooltotal) + ')'



class DataCenterRollup(object):
    def __init__(self):
        self.id = getHexID()
        self.entity_id = None
        self.state = None
        self.metric_type = constants.DATACENTER_ROLLUP
        self.rollup_type = constants.HOURLY
        self.cdate = None
        self.cpu_util_avg = None
        self.cpu_util_min = None
        self.cpu_util_max = None
        self.cpu_util_stddev = None
        self.mem_util_avg = None
        self.mem_util_min = None
        self.mem_util_max = None
        self.mem_util_stddev = None
        self.vbds_avg = None
        self.vbds_min = None
        self.vbds_max = None
        self.vbds_stddev = None
        self.vbd_oo_avg = None
        self.vbd_oo_min = None
        self.vbd_oo_max = None
        self.vbd_oo_stddev = None
        self.vbd_rd_avg = None
        self.vbd_rd_min = None
        self.vbd_rd_max = None
        self.vbd_rd_stddev = None
        self.vbd_wr_avg = None
        self.vbd_wr_min = None
        self.vbd_wr_max = None
        self.vbd_wr_stddev = None
        self.net_avg = None
        self.net_min = None
        self.net_max = None
        self.net_stddev = None
        self.net_tx_avg = None
        self.net_tx_min = None
        self.net_tx_max = None
        self.net_tx_stddev = None
        self.net_rx_avg = None
        self.net_rx_min = None
        self.net_rx_max = None
        self.net_rx_stddev = None
        self.gb_local_avg = None
        self.gb_local_min = None
        self.gb_local_max = None
        self.gb_local_stddev = None
        self.gb_poolused_avg = None
        self.gb_poolused_min = None
        self.gb_poolused_max = None
        self.gb_poolused_stddev = None
        self.gb_pooltotal_avg = None
        self.gb_pooltotal_min = None
        self.gb_pooltotal_max = None
        self.gb_pooltotal_stddev = None

    def __repr__(self):
        return '( DATACENTER_ROLLUP ' + to_str(self.type) + ',' + to_str(self.cpu_util_avg) + ')'



class DataCenterCurr(object):
    def __init__(self):
        self.id = getHexID()
        self.entity_id = None
        self.state = None
        self.metric_type = constants.DATACENTER_CURR
        self.cdate = None
        self.cpu_util = None
        self.mem_util = None
        self.vbds = None
        self.vbd_oo = None
        self.vbd_rd = None
        self.vbd_wr = None
        self.net = None
        self.net_tx = None
        self.net_rx = None
        self.gb_local = None
        self.gb_poolused = None
        self.gb_pooltotal = None

    def __repr__(self):
        return '( DATACENTER_CURR ' + self.entity_id + ',' + to_str(self.state) + ',' + to_str(self.metric_type) + ',' + to_str(self.cdate) + ',' + to_str(self.cpu_util) + ',' + to_str(self.mem_util) + ',' + to_str(self.vbds) + ',' + to_str(self.vbd_oo) + ',' + to_str(self.vbd_rd) + ',' + to_str(self.vbd_wr) + ',' + to_str(self.net) + ',' + to_str(self.net_tx) + ',' + to_str(self.net_rx) + ',' + to_str(self.gb_local) + ',' + to_str(self.gb_poolused) + ',' + to_str(self.gb_pooltotal) + ')'



class ServerPoolRaw(object):
    def __init__(self):
        self.id = getHexID()
        self.entity_id = None
        self.state = None
        self.metric_type = constants.SERVERPOOL_RAW
        self.cdate = None
        self.cpu_util = None
        self.mem_util = None
        self.vbds = None
        self.vbd_oo = None
        self.vbd_rd = None
        self.vbd_wr = None
        self.net = None
        self.net_tx = None
        self.net_rx = None
        self.gb_local = None
        self.gb_poolused = None
        self.gb_pooltotal = None

    def __repr__(self):
        return '( SERVERPOOL_RAW ' + self.entity_id + ',' + to_str(self.state) + ',' + to_str(self.metric_type) + ',' + to_str(self.cdate) + ',' + to_str(self.cpu_util) + ',' + to_str(self.mem_util) + ',' + to_str(self.vbds) + ',' + to_str(self.vbd_oo) + ',' + to_str(self.vbd_rd) + ',' + to_str(self.vbd_wr) + ',' + to_str(self.net) + ',' + to_str(self.net_tx) + ',' + to_str(self.net_rx) + ',' + to_str(self.gb_local) + ',' + to_str(self.gb_poolused) + ',' + to_str(self.gb_pooltotal) + ')'



class ServerPoolRollup(object):
    def __init__(self):
        self.id = getHexID()
        self.entity_id = None
        self.state = None
        self.metric_type = constants.SERVERPOOL_ROLLUP
        self.rollup_type = constants.HOURLY
        self.cdate = None
        self.cpu_util_avg = None
        self.cpu_util_min = None
        self.cpu_util_max = None
        self.cpu_util_stddev = None
        self.mem_util_avg = None
        self.mem_util_min = None
        self.mem_util_max = None
        self.mem_util_stddev = None
        self.vbds_avg = None
        self.vbds_min = None
        self.vbds_max = None
        self.vbds_stddev = None
        self.vbd_oo_avg = None
        self.vbd_oo_min = None
        self.vbd_oo_max = None
        self.vbd_oo_stddev = None
        self.vbd_rd_avg = None
        self.vbd_rd_min = None
        self.vbd_rd_max = None
        self.vbd_rd_stddev = None
        self.vbd_wr_avg = None
        self.vbd_wr_min = None
        self.vbd_wr_max = None
        self.vbd_wr_stddev = None
        self.net_avg = None
        self.net_min = None
        self.net_max = None
        self.net_stddev = None
        self.net_tx_avg = None
        self.net_tx_min = None
        self.net_tx_max = None
        self.net_tx_stddev = None
        self.net_rx_avg = None
        self.net_rx_min = None
        self.net_rx_max = None
        self.net_rx_stddev = None
        self.gb_local_avg = None
        self.gb_local_min = None
        self.gb_local_max = None
        self.gb_local_stddev = None
        self.gb_poolused_avg = None
        self.gb_poolused_min = None
        self.gb_poolused_max = None
        self.gb_poolused_stddev = None
        self.gb_pooltotal_avg = None
        self.gb_pooltotal_min = None
        self.gb_pooltotal_max = None
        self.gb_pooltotal_stddev = None

    def __repr__(self):
        return '( SERVERPOOL_ROLLUP' + to_str(self.type) + ',' + to_str(self.cpu_util_avg) + ')'



class ServerPoolCurr(object):
    def __init__(self):
        self.id = getHexID()
        self.entity_id = None
        self.state = None
        self.metric_type = constants.SERVERPOOL_CURR
        self.cdate = None
        self.cpu_util = None
        self.mem_util = None
        self.vbds = None
        self.vbd_oo = None
        self.vbd_rd = None
        self.vbd_wr = None
        self.net = None
        self.net_tx = None
        self.net_rx = None
        self.gb_local = None
        self.gb_poolused = None
        self.gb_pooltotal = None
        return None

    def __repr__(self):
        return '( SERVERPOOL CURR ' + self.entity_id + ',' + to_str(self.state) + ',' + to_str(self.metric_type) + ',' + to_str(self.cdate) + ',' + to_str(self.cpu_util) + ',' + to_str(self.mem_util) + ',' + to_str(self.vbds) + ',' + to_str(self.vbd_oo) + ',' + to_str(self.vbd_rd) + ',' + to_str(self.vbd_wr) + ',' + to_str(self.net) + ',' + to_str(self.net_tx) + ',' + to_str(self.net_rx) + ',' + to_str(self.gb_local) + ',' + to_str(self.gb_poolused) + ',' + to_str(self.gb_pooltotal) + ')'



class MetricVMRaw(object):
    def __init__(self):
        self.id = getHexID()
        self.entity_id = None
        self.cloud_entity_id = None
        self.state = None
        self.metric_type = constants.VM_RAW
        self.cdate = None
        self.cpu_util = None
        self.vm_cpu_util = None
        self.mem_util = None
        self.vbds = None
        self.vbd_oo = None
        self.vbd_rd = None
        self.vbd_wr = None
        self.net = None
        self.net_tx = None
        self.net_rx = None
        self.gb_local = None
        self.gb_poolused = None
        self.gb_pooltotal = None

    def __repr__(self):
        return '(' + to_str(self.cpu_util) + ',' + to_str(self.mem_util) + ',' + to_str(self.vbds) + ',' + to_str(self.vbd_oo) + ',' + to_str(self.vbd_rd) + ',' + to_str(self.vbd_wr) + ',' + to_str(self.net) + ',' + to_str(self.net_tx) + ',' + to_str(self.net_rx) + ',' + to_str(self.gb_local) + ',' + to_str(self.gb_poolused) + ',' + to_str(self.gb_pooltotal) + ',' + to_str(self.state) + ',' + to_str(self.metric_type) + ')'



class MetricServerRaw(object):
    def __init__(self):
        self.id = getHexID()
        self.entity_id = None
        self.state = None
        self.metric_type = constants.SERVER_RAW
        self.cdate = None
        self.cpu_util = None
        self.mem_util = None
        self.vbds = None
        self.vbd_oo = None
        self.vbd_rd = None
        self.vbd_wr = None
        self.net = None
        self.net_tx = None
        self.net_rx = None
        self.gb_local = None
        self.gb_poolused = None
        self.gb_pooltotal = None
        self.host_mem = None
        self.host_cpu = None

    def __repr__(self):
        return '( SERVER_RAW ' + self.entity_id + ',' + to_str(self.state) + ',' + to_str(self.metric_type) + ',' + to_str(self.cdate) + ',' + to_str(self.cpu_util) + ',' + to_str(self.mem_util) + ',' + to_str(self.vbds) + ',' + to_str(self.vbd_oo) + ',' + to_str(self.vbd_rd) + ',' + to_str(self.vbd_wr) + ',' + to_str(self.net) + ',' + to_str(self.net_tx) + ',' + to_str(self.net_rx) + ',' + to_str(self.gb_local) + ',' + to_str(self.gb_poolused) + ',' + to_str(self.gb_pooltotal) + ')'

class MetricVMCurr(object):
    def __init__(self):
        self.id = getHexID()
        self.entity_id = None
        self.cloud_entity_id = None
        self.state = None
        self.metric_type = constants.VM_CURR
        self.cdate = None
        self.cpu_util = None
        self.vm_cpu_util = None
        self.mem_util = None
        self.vbds = None
        self.vbd_oo = None
        self.vbd_rd = None
        self.vbd_wr = None
        self.net = None
        self.net_tx = None
        self.net_rx = None
        self.gb_local = None
        self.gb_poolused = None
        self.gb_pooltotal = None

    def __repr__(self):
        return '( VM_CURR ' + self.entity_id + ',' + to_str(self.state) + ',' + to_str(self.metric_type) + ',' + to_str(self.cdate) + ',' + to_str(self.cpu_util) + ',' + to_str(self.mem_util) + ',' + to_str(self.vbds) + ',' + to_str(self.vbd_oo) + ',' + to_str(self.vbd_rd) + ',' + to_str(self.vbd_wr) + ',' + to_str(self.net) + ',' + to_str(self.net_tx) + ',' + to_str(self.net_rx) + ',' + to_str(self.gb_local) + ',' + to_str(self.gb_poolused) + ',' + to_str(self.gb_pooltotal) + ')'



class MetricServerCurr(object):
    def __init__(self):
        self.id = getHexID()
        self.entity_id = None
        self.state = None
        self.metric_type = constants.SERVER_CURR
        self.cdate = None
        self.cpu_util = None
        self.mem_util = None
        self.vbds = None
        self.vbd_oo = None
        self.vbd_rd = None
        self.vbd_wr = None
        self.net = None
        self.net_tx = None
        self.net_rx = None
        self.gb_local = None
        self.gb_poolused = None
        self.gb_pooltotal = None
        self.host_mem = None
        self.host_cpu = None

    def __repr__(self):
        return '( SERVER_CURR ' + self.entity_id + ',' + to_str(self.state) + ',' + to_str(self.metric_type) + ',' + to_str(self.cdate) + ',' + to_str(self.cpu_util) + ',' + to_str(self.mem_util) + ',' + to_str(self.vbds) + ',' + to_str(self.vbd_oo) + ',' + to_str(self.vbd_rd) + ',' + to_str(self.vbd_wr) + ',' + to_str(self.net) + ',' + to_str(self.net_tx) + ',' + to_str(self.net_rx) + ',' + to_str(self.gb_local) + ',' + to_str(self.gb_poolused) + ',' + to_str(self.gb_pooltotal) + ')'



class MetricVMRollup(object):
    def __init__(self):
        self.id = getHexID()
        self.entity_id = None
        self.cloud_entity_id = None
        self.state = None
        self.metric_type = constants.VM_ROLLUP
        self.rollup_type = constants.HOURLY
        self.cdate = None
        self.cpu_util_avg = None
        self.cpu_util_min = None
        self.cpu_util_max = None
        self.cpu_util_stddev = None
        self.vm_cpu_util_avg = None
        self.vm_cpu_util_min = None
        self.vm_cpu_util_max = None
        self.vm_cpu_util_stddev = None
        self.mem_util_avg = None
        self.mem_util_min = None
        self.mem_util_max = None
        self.mem_util_stddev = None
        self.vbds_avg = None
        self.vbds_min = None
        self.vbds_max = None
        self.vbds_stddev = None
        self.vbd_oo_avg = None
        self.vbd_oo_min = None
        self.vbd_oo_max = None
        self.vbd_oo_stddev = None
        self.vbd_rd_avg = None
        self.vbd_rd_min = None
        self.vbd_rd_max = None
        self.vbd_rd_stddev = None
        self.vbd_wr_avg = None
        self.vbd_wr_min = None
        self.vbd_wr_max = None
        self.vbd_wr_stddev = None
        self.net_avg = None
        self.net_min = None
        self.net_max = None
        self.net_stddev = None
        self.net_tx_avg = None
        self.net_tx_min = None
        self.net_tx_max = None
        self.net_tx_stddev = None
        self.net_rx_avg = None
        self.net_rx_min = None
        self.net_rx_max = None
        self.net_rx_stddev = None
        self.gb_local_avg = None
        self.gb_local_min = None
        self.gb_local_max = None
        self.gb_local_stddev = None
        self.gb_poolused_avg = None
        self.gb_poolused_min = None
        self.gb_poolused_max = None
        self.gb_poolused_stddev = None
        self.gb_pooltotal_avg = None
        self.gb_pooltotal_min = None
        self.gb_pooltotal_max = None
        self.gb_pooltotal_stddev = None

    def __repr__(self):
        return '( VM_ROLLUP' + to_str(self.type) + ',' + to_str(self.cpu_util_avg) + ')'



class MetricServerRollup(object):
    def __init__(self):
        self.id = getHexID()
        self.entity_id = None
        self.state = None
        self.metric_type = constants.SERVER_ROLLUP
        self.rollup_type = constants.HOURLY
        self.cdate = None
        self.cpu_util_avg = None
        self.cpu_util_min = None
        self.cpu_util_max = None
        self.cpu_util_stddev = None
        self.mem_util_avg = None
        self.mem_util_min = None
        self.mem_util_max = None
        self.mem_util_stddev = None
        self.vbds_avg = None
        self.vbds_min = None
        self.vbds_max = None
        self.vbds_stddev = None
        self.vbd_oo_avg = None
        self.vbd_oo_min = None
        self.vbd_oo_max = None
        self.vbd_oo_stddev = None
        self.vbd_rd_avg = None
        self.vbd_rd_min = None
        self.vbd_rd_max = None
        self.vbd_rd_stddev = None
        self.vbd_wr_avg = None
        self.vbd_wr_min = None
        self.vbd_wr_max = None
        self.vbd_wr_stddev = None
        self.net_avg = None
        self.net_min = None
        self.net_max = None
        self.net_stddev = None
        self.net_tx_avg = None
        self.net_tx_min = None
        self.net_tx_max = None
        self.net_tx_stddev = None
        self.net_rx_avg = None
        self.net_rx_min = None
        self.net_rx_max = None
        self.net_rx_stddev = None
        self.gb_local_avg = None
        self.gb_local_min = None
        self.gb_local_max = None
        self.gb_local_stddev = None
        self.gb_poolused_avg = None
        self.gb_poolused_min = None
        self.gb_poolused_max = None
        self.gb_poolused_stddev = None
        self.gb_pooltotal_avg = None
        self.gb_pooltotal_min = None
        self.gb_pooltotal_max = None
        self.gb_pooltotal_stddev = None
        self.host_mem_avg = None
        self.host_mem_min = None
        self.host_mem_max = None
        self.host_mem_stddev = None
        self.host_cpu_avg = None
        self.host_cpu_min = None
        self.host_cpu_max = None
        self.host_cpu_stddev = None

    def __repr__(self):
        return '( SERVER_ROLLUP' + to_str(self.type) + ',' + to_str(self.cpu_util_avg) + ')'



class MetricsService():
    def __init__(self):
        self.mapper_class_dict = self.mapper_class_lookup()
        self.metricType_class_dict = self.metricType_class_lookup()

    def mapper_class_lookup(self):
        mapper_class_dict  = {
                              'DataCenterRawMapper':DataCenterRaw,
                              'DataCenterCurrMapper':DataCenterCurr,
                              'DatCenterRollupMapper':DataCenterRollup,
                              'ServerPoolRawMapper':ServerPoolRaw,
                              'ServerPoolCurrMapper':ServerPoolCurr,
                              'ServerPoolRollupMapper':ServerPoolRollup,
                              'MetricVMRawMapper':MetricVMRaw,
                              'MetricServerRawMapper':MetricServerRaw,
                              'MetricVMCurrMapper':MetricVMCurr,
                              'MetricServerCurrMapper':MetricServerCurr,
                              'MetricVMRollupMapper':MetricVMRollup,
                              'MetricServerRollupMapper':MetricServerRollup
                             }
        return mapper_class_dict

    def metricType_class_lookup(self):
        metricType_class_dict = {
                                 constants.DATACENTER_RAW:DataCenterRaw,
                                 constants.DATACENTER_CURR:DataCenterCurr,
                                 constants.SERVERPOOL_RAW:ServerPoolRaw,
                                 constants.SERVERPOOL_CURR:ServerPoolCurr,
                                 constants.VM_RAW:MetricVMRaw,
                                 constants.SERVER_RAW:MetricServerRaw,
                                 constants.VM_CURR:MetricVMCurr,
                                 constants.SERVER_CURR:MetricServerCurr
                                 ,constants.DATACENTER_ROLLUP:DataCenterRollup,
                                 constants.SERVERPOOL_ROLLUP:ServerPoolRollup,
                                 constants.VM_ROLLUP:MetricVMRollup,
                                 constants.SERVER_ROLLUP:MetricServerRollup,
                                }
        return metricType_class_dict

    def init_mappers(self):
        # currently this mapper is not in use
        self.DataCenterRawMapper = mapper(DataCenterRaw,Metrics.__table__,properties={
        'entity_id':Metrics.__table__.c.entity_id,
        'state':Metrics.__table__.c.state,
        'metric_type':Metrics.__table__.c.metric_type,
        'cdate':Metrics.__table__.c.cdate,
        'cpu_util':Metrics.__table__.c.fcol1,
        'mem_util':Metrics.__table__.c.fcol2,
        'vbds':Metrics.__table__.c.icol1,
        'vbd_oo':Metrics.__table__.c.icol2,
        'vbd_rd':Metrics.__table__.c.icol3,
        'vbd_wr':Metrics.__table__.c.icol4,
        'net':Metrics.__table__.c.icol5,
        'net_tx':Metrics.__table__.c.icol6,
        'net_rx':Metrics.__table__.c.icol7,
        'gb_local':Metrics.__table__.c.fcol3,
        'gb_poolused':Metrics.__table__.c.fcol4,
        'gb_pooltotal':Metrics.__table__.c.fcol5
        }
        )

        # currently this mapper is not in use
        self.DataCenterCurrMapper = mapper(DataCenterCurr,MetricsCurr.__table__,properties={
        'entity_id':column_property(MetricsCurr.__table__.c.entity_id),
        'state':column_property(MetricsCurr.__table__.c.state),
        'metric_type':column_property(MetricsCurr.__table__.c.metric_type),
        'cdate':column_property(MetricsCurr.__table__.c.cdate),
        'cpu_util':column_property(MetricsCurr.__table__.c.fcol1),
        'mem_util':column_property(MetricsCurr.__table__.c.fcol2),
        'vbds':column_property(MetricsCurr.__table__.c.icol1),
        'vbd_oo':column_property(MetricsCurr.__table__.c.icol2),
        'vbd_rd':column_property(MetricsCurr.__table__.c.icol3),
        'vbd_wr':column_property(MetricsCurr.__table__.c.icol4),
        'net':column_property(MetricsCurr.__table__.c.icol5),
        'net_tx':column_property(MetricsCurr.__table__.c.icol6),
        'net_rx':column_property(MetricsCurr.__table__.c.icol7),
        'gb_local':column_property(MetricsCurr.__table__.c.fcol3),
        'gb_poolused':column_property(MetricsCurr.__table__.c.fcol4),
        'gb_pooltotal':column_property(MetricsCurr.__table__.c.fcol5)
        }
        )

        # currently this mapper is not in use 
        self.DatCenterRollupMapper = mapper(DataCenterRollup,MetricsArch.__table__,properties={
        'entity_id':MetricsArch.__table__.c.entity_id,
        'state':MetricsArch.__table__.c.state,
        'metric_type':MetricsArch.__table__.c.metric_type,
        'rollup_type':MetricsArch.__table__.c.rollup_type,
        'cdate':MetricsArch.__table__.c.cdate, 
        'cpu_util_avg':MetricsArch.__table__.c.fcol1,
        'cpu_util_min':MetricsArch.__table__.c.fcol2,
        'cpu_util_max':MetricsArch.__table__.c.fcol3,
        'cpu_util_stddev':MetricsArch.__table__.c.fcol4,
        'mem_util_avg':MetricsArch.__table__.c.fcol5,
        'mem_util_min':MetricsArch.__table__.c.fcol6,
        'mem_util_max':MetricsArch.__table__.c.fcol7,
        'mem_util_stddev':MetricsArch.__table__.c.fcol8,
        'vbds_avg':MetricsArch.__table__.c.fcol9,
        'vbds_min':MetricsArch.__table__.c.icol1,
        'vbds_max':MetricsArch.__table__.c.icol2,
        'vbds_stddev':MetricsArch.__table__.c.fcol9,
        'vbd_oo_avg':MetricsArch.__table__.c.icol3,
        'vbd_oo_min':MetricsArch.__table__.c.icol4,
        'vbd_oo_max':MetricsArch.__table__.c.icol5,
        'vbd_oo_stddev':MetricsArch.__table__.c.fcol10,
        'vbd_rd_avg':MetricsArch.__table__.c.fcol11,
        'vbd_rd_min':MetricsArch.__table__.c.icol6,
        'vbd_rd_max':MetricsArch.__table__.c.icol7,
        'vbd_rd_stddev':MetricsArch.__table__.c.icol8,
        'vbd_wr_avg':MetricsArch.__table__.c.fcol12,
        'vbd_wr_min':MetricsArch.__table__.c.icol9,
        'vbd_wr_max':MetricsArch.__table__.c.icol10,
        'vbd_wr_stddev':MetricsArch.__table__.c.fcol13,
        'net_avg':MetricsArch.__table__.c.fcol14,
        'net_min':MetricsArch.__table__.c.icol11,
        'net_max':MetricsArch.__table__.c.icol12,
        'net_stddev':MetricsArch.__table__.c.fcol15,
        'net_tx_avg':MetricsArch.__table__.c.fcol16,
        'net_tx_min':MetricsArch.__table__.c.icol13,
        'net_tx_max':MetricsArch.__table__.c.icol14,
        'net_tx_stddev':MetricsArch.__table__.c.fcol17,
        'net_rx_avg':MetricsArch.__table__.c.fcol18,
        'net_rx_min':MetricsArch.__table__.c.icol15,
        'net_rx_max':MetricsArch.__table__.c.icol16,
        'net_rx_stddev':MetricsArch.__table__.c.fcol19,
        'gb_local_avg':MetricsArch.__table__.c.fcol20,
        'gb_local_min':MetricsArch.__table__.c.fcol21,
        'gb_local_max':MetricsArch.__table__.c.fcol22,
        'gb_local_stddev':MetricsArch.__table__.c.fcol23,
        'gb_poolused_avg':MetricsArch.__table__.c.fcol24,
        'gb_poolused_min':MetricsArch.__table__.c.fcol25,
        'gb_poolused_max':MetricsArch.__table__.c.fcol26,
        'gb_poolused_stddev':MetricsArch.__table__.c.fcol27,
        'gb_pooltotal_avg':MetricsArch.__table__.c.fcol28,
        'gb_pooltotal_min':MetricsArch.__table__.c.fcol29,
        'gb_pooltotal_max':MetricsArch.__table__.c.fcol30,
        'gb_pooltotal_stddev':MetricsArch.__table__.c.fcol31,
        'cpu_util_stddev':MetricsArch.__table__.c.cdate
        }
        )

        self.ServerPoolRawMapper = mapper(ServerPoolRaw,Metrics.__table__,properties={
        'entity_id':column_property(Metrics.__table__.c.entity_id),
        'state':column_property(Metrics.__table__.c.state),
        'metric_type':column_property(Metrics.__table__.c.metric_type),
        'cdate':column_property(Metrics.__table__.c.cdate),
        'cpu_util':column_property(Metrics.__table__.c.fcol1),
        'mem_util':column_property(Metrics.__table__.c.fcol2),
        'vbds':column_property(Metrics.__table__.c.icol1),
        'vbd_oo':column_property(Metrics.__table__.c.icol2),
        'vbd_rd':column_property(Metrics.__table__.c.icol3),
        'vbd_wr':column_property(Metrics.__table__.c.icol4),
        'net':column_property(Metrics.__table__.c.icol5),
        'net_tx':column_property(Metrics.__table__.c.icol6),
        'net_rx':column_property(Metrics.__table__.c.icol7),
        'gb_local':column_property(Metrics.__table__.c.fcol3),
        'gb_poolused':column_property(Metrics.__table__.c.fcol4),
        'gb_pooltotal':column_property(Metrics.__table__.c.fcol5),
        'total_vms':column_property(Metrics.__table__.c.icol8),
        'paused_vms':column_property(Metrics.__table__.c.icol9),
        'running_vms':column_property(Metrics.__table__.c.icol10),
        'server_cpus':column_property(Metrics.__table__.c.icol11),
        'crashed_vms':column_property(Metrics.__table__.c.icol12),
        'total_mem':column_property(Metrics.__table__.c.fcol6),
        'total_cpu':column_property(Metrics.__table__.c.fcol7),
        'server_mem':column_property(Metrics.__table__.c.fcol8),
        'server_count':column_property(Metrics.__table__.c.fcol9),
        'nodes_connected':column_property(Metrics.__table__.c.icol13)
        }
        )

        # currently this mapper is not in use###########################
        self.ServerPoolCurrMapper = mapper(ServerPoolCurr,MetricsCurr.__table__,properties={
        'entity_id':column_property(MetricsCurr.__table__.c.entity_id),
        'state':column_property(MetricsCurr.__table__.c.state),
        'metric_type':column_property(MetricsCurr.__table__.c.metric_type),
        'cdate':column_property(MetricsCurr.__table__.c.cdate),
        'cpu_util':column_property(MetricsCurr.__table__.c.fcol1),
        'mem_util':column_property(MetricsCurr.__table__.c.fcol2),
        'vbds':column_property(MetricsCurr.__table__.c.icol1),
        'vbd_oo':column_property(MetricsCurr.__table__.c.icol2),
        'vbd_rd':column_property(MetricsCurr.__table__.c.icol3),
        'vbd_wr':column_property(MetricsCurr.__table__.c.icol4),
        'net':column_property(MetricsCurr.__table__.c.icol5),
        'net_tx':column_property(MetricsCurr.__table__.c.icol6),
        'net_rx':column_property(MetricsCurr.__table__.c.icol7),
        'gb_local':column_property(MetricsCurr.__table__.c.fcol3),
        'gb_poolused':column_property(MetricsCurr.__table__.c.fcol4),
        'gb_pooltotal':column_property(MetricsCurr.__table__.c.fcol5),
        'total_vms':column_property(MetricsCurr.__table__.c.icol8),
        'paused_vms':column_property(MetricsCurr.__table__.c.icol9),
        'running_vms':column_property(MetricsCurr.__table__.c.icol10),
        'server_cpus':column_property(MetricsCurr.__table__.c.icol11),
        'crashed_vms':column_property(MetricsCurr.__table__.c.icol12),
        'total_mem':column_property(MetricsCurr.__table__.c.fcol6),
        'total_cpu':column_property(MetricsCurr.__table__.c.fcol7),
        'server_mem':column_property(MetricsCurr.__table__.c.fcol8),
        'server_count':column_property(MetricsCurr.__table__.c.fcol9),
        'nodes_connected':column_property(MetricsCurr.__table__.c.icol13)
        
        }
        )

        self.MetricServerRawMapper = mapper(MetricServerRaw,Metrics.__table__,properties={
        'entity_id':Metrics.__table__.c.entity_id,
        'state':Metrics.__table__.c.state,
        'metric_type':Metrics.__table__.c.metric_type,
        'cdate':Metrics.__table__.c.cdate,
        'cpu_util':Metrics.__table__.c.fcol1,
        'mem_util':Metrics.__table__.c.fcol2,
        'vbds':Metrics.__table__.c.icol1,
        'vbd_oo':Metrics.__table__.c.icol2,
        'vbd_rd':Metrics.__table__.c.icol3,
        'vbd_wr':Metrics.__table__.c.icol4,
        'net':Metrics.__table__.c.icol5,
        'net_tx':Metrics.__table__.c.icol6,
        'net_rx':Metrics.__table__.c.icol7,
        'gb_local':Metrics.__table__.c.fcol3,
        'gb_poolused':Metrics.__table__.c.fcol4,
        'gb_pooltotal':Metrics.__table__.c.fcol5,
        'total_vms':Metrics.__table__.c.icol8,
        'paused_vms':Metrics.__table__.c.icol9,
        'running_vms':Metrics.__table__.c.icol10,
        'server_cpus':Metrics.__table__.c.icol11,
        'crashed_vms':Metrics.__table__.c.icol12,
        'total_mem':Metrics.__table__.c.fcol6,
        'total_cpu':Metrics.__table__.c.fcol7,
        'server_mem':Metrics.__table__.c.fcol8,
        'host_mem':Metrics.__table__.c.fcol9,
        'host_cpu':Metrics.__table__.c.fcol10
        }
        )

        # currently this mapper is not in use
        self.MetricServerCurrMapper = mapper(MetricServerCurr,MetricsCurr.__table__,properties={
        'entity_id':column_property(MetricsCurr.__table__.c.entity_id),
        'state':column_property(MetricsCurr.__table__.c.state),
        'metric_type':column_property(MetricsCurr.__table__.c.metric_type),
        'cdate':column_property(MetricsCurr.__table__.c.cdate),
        'cpu_util':column_property(MetricsCurr.__table__.c.fcol1),
        'mem_util':column_property(MetricsCurr.__table__.c.fcol2),
        'vbds':column_property(MetricsCurr.__table__.c.icol1),
        'vbd_oo':column_property(MetricsCurr.__table__.c.icol2),
        'vbd_rd':column_property(MetricsCurr.__table__.c.icol3),
        'vbd_wr':column_property(MetricsCurr.__table__.c.icol4),
        'net':column_property(MetricsCurr.__table__.c.icol5),
        'net_tx':column_property(MetricsCurr.__table__.c.icol6),
        'net_rx':column_property(MetricsCurr.__table__.c.icol7),
        'gb_local':column_property(MetricsCurr.__table__.c.fcol3),
        'gb_poolused':column_property(MetricsCurr.__table__.c.fcol4),
        'gb_pooltotal':column_property(MetricsCurr.__table__.c.fcol5),
        'total_vms':column_property(MetricsCurr.__table__.c.icol8),
        'paused_vms':column_property(MetricsCurr.__table__.c.icol9),
        'running_vms':column_property(MetricsCurr.__table__.c.icol10),
        'server_cpus':column_property(MetricsCurr.__table__.c.icol11),
        'crashed_vms':column_property(MetricsCurr.__table__.c.icol12),
        'total_mem':column_property(MetricsCurr.__table__.c.fcol6),
        'total_cpu':column_property(MetricsCurr.__table__.c.fcol7),
        'server_mem':column_property(MetricsCurr.__table__.c.fcol8),
        'host_mem':column_property(MetricsCurr.__table__.c.fcol9),
        'host_cpu':column_property(MetricsCurr.__table__.c.fcol10)
        }
        )

        """
        serverrollup metrics is commented since the rollup data is added to server
        raw metrics. not sure if this mapper is required any more
        """
        self.MetricServerRollupMapper=mapper(MetricServerRollup,MetricsArch.__table__,properties={
        'entity_id':MetricsArch.__table__.c.entity_id,
        'state':MetricsArch.__table__.c.state,
        'metric_type':MetricsArch.__table__.c.metric_type,
        'rollup_type':MetricsArch.__table__.c.rollup_type,
        'cdate':MetricsArch.__table__.c.cdate, 
        'cpu_util_avg':MetricsArch.__table__.c.fcol1,
        'cpu_util_min':MetricsArch.__table__.c.fcol2,
        'cpu_util_max':MetricsArch.__table__.c.fcol3,
        'cpu_util_stddev':MetricsArch.__table__.c.fcol4,
        'mem_util_avg':MetricsArch.__table__.c.fcol5,
        'mem_util_min':MetricsArch.__table__.c.fcol6,
        'mem_util_max':MetricsArch.__table__.c.fcol7,
        'mem_util_stddev':MetricsArch.__table__.c.fcol8,
        'vbds_avg':MetricsArch.__table__.c.fcol9,
        'vbds_min':MetricsArch.__table__.c.icol1,
        'vbds_max':MetricsArch.__table__.c.icol2,
        'vbds_stddev':MetricsArch.__table__.c.fcol9,
        'vbd_oo_avg':MetricsArch.__table__.c.icol3,
        'vbd_oo_min':MetricsArch.__table__.c.icol4,
        'vbd_oo_max':MetricsArch.__table__.c.icol5,
        'vbd_oo_stddev':MetricsArch.__table__.c.fcol10,
        'vbd_rd_avg':MetricsArch.__table__.c.fcol11,
        'vbd_rd_min':MetricsArch.__table__.c.icol6,
        'vbd_rd_max':MetricsArch.__table__.c.icol7,
        'vbd_rd_stddev':MetricsArch.__table__.c.icol8,
        'vbd_wr_avg':MetricsArch.__table__.c.fcol12,
        'vbd_wr_min':MetricsArch.__table__.c.icol9,
        'vbd_wr_max':MetricsArch.__table__.c.icol10,
        'vbd_wr_stddev':MetricsArch.__table__.c.fcol13,
        'net_avg':MetricsArch.__table__.c.fcol14,
        'net_min':MetricsArch.__table__.c.icol11,
        'net_max':MetricsArch.__table__.c.icol12,
        'net_stddev':MetricsArch.__table__.c.fcol15,
        'net_tx_avg':MetricsArch.__table__.c.fcol16,
        'net_tx_min':MetricsArch.__table__.c.icol13,
        'net_tx_max':MetricsArch.__table__.c.icol14,
        'net_tx_stddev':MetricsArch.__table__.c.fcol17,
        'net_rx_avg':MetricsArch.__table__.c.fcol18,
        'net_rx_min':MetricsArch.__table__.c.icol15,
        'net_rx_max':MetricsArch.__table__.c.icol16,
        'net_rx_stddev':MetricsArch.__table__.c.fcol19,
        'gb_local_avg':MetricsArch.__table__.c.fcol20,
        'gb_local_min':MetricsArch.__table__.c.fcol21,
        'gb_local_max':MetricsArch.__table__.c.fcol22,
        'gb_local_stddev':MetricsArch.__table__.c.fcol23,
        'gb_poolused_avg':MetricsArch.__table__.c.fcol24,
        'gb_poolused_min':MetricsArch.__table__.c.fcol25,
        'gb_poolused_max':MetricsArch.__table__.c.fcol26,
        'gb_poolused_stddev':MetricsArch.__table__.c.fcol27,
        'gb_pooltotal_avg':MetricsArch.__table__.c.fcol28,
        'gb_pooltotal_min':MetricsArch.__table__.c.fcol29,
        'gb_pooltotal_max':MetricsArch.__table__.c.fcol30,
        'gb_pooltotal_stddev':MetricsArch.__table__.c.fcol31,
        #'cpu_util_stddev':MetricsArch.__table__.c.cdate,
        'host_mem_avg':MetricsArch.__table__.c.fcol32,
        'host_mem_min':MetricsArch.__table__.c.fcol33,
        'host_mem_max':MetricsArch.__table__.c.fcol34,
        'host_mem_stddev':MetricsArch.__table__.c.fcol35,
        'host_cpu_avg':MetricsArch.__table__.c.fcol36,
        'host_cpu_min':MetricsArch.__table__.c.fcol37,
        'host_cpu_max':MetricsArch.__table__.c.fcol38,
        'host_cpu_stddev':MetricsArch.__table__.c.fcol39
        }
        )

        self.ServerPoolRollupMapper=mapper(ServerPoolRollup,MetricsArch.__table__,properties={
        'entity_id':MetricsArch.__table__.c.entity_id,
        'state':MetricsArch.__table__.c.state,
        'metric_type':MetricsArch.__table__.c.metric_type,
        'rollup_type':MetricsArch.__table__.c.rollup_type,
        'cdate':MetricsArch.__table__.c.cdate, 
        'cpu_util_avg':MetricsArch.__table__.c.fcol1,
        'cpu_util_min':MetricsArch.__table__.c.fcol2,
        'cpu_util_max':MetricsArch.__table__.c.fcol3,
        'cpu_util_stddev':MetricsArch.__table__.c.fcol4,
        'mem_util_avg':MetricsArch.__table__.c.fcol5,
        'mem_util_min':MetricsArch.__table__.c.fcol6,
        'mem_util_max':MetricsArch.__table__.c.fcol7,
        'mem_util_stddev':MetricsArch.__table__.c.fcol8,
        'vbds_avg':MetricsArch.__table__.c.fcol9,
        'vbds_min':MetricsArch.__table__.c.icol1,
        'vbds_max':MetricsArch.__table__.c.icol2,
        'vbds_stddev':MetricsArch.__table__.c.fcol9,
        'vbd_oo_avg':MetricsArch.__table__.c.icol3,
        'vbd_oo_min':MetricsArch.__table__.c.icol4,
        'vbd_oo_max':MetricsArch.__table__.c.icol5,
        'vbd_oo_stddev':MetricsArch.__table__.c.fcol10,
        'vbd_rd_avg':MetricsArch.__table__.c.fcol11,
        'vbd_rd_min':MetricsArch.__table__.c.icol6,
        'vbd_rd_max':MetricsArch.__table__.c.icol7,
        'vbd_rd_stddev':MetricsArch.__table__.c.icol8,
        'vbd_wr_avg':MetricsArch.__table__.c.fcol12,
        'vbd_wr_min':MetricsArch.__table__.c.icol9,
        'vbd_wr_max':MetricsArch.__table__.c.icol10,
        'vbd_wr_stddev':MetricsArch.__table__.c.fcol13,
        'net_avg':MetricsArch.__table__.c.fcol14,
        'net_min':MetricsArch.__table__.c.icol11,
        'net_max':MetricsArch.__table__.c.icol12,
        'net_stddev':MetricsArch.__table__.c.fcol15,
        'net_tx_avg':MetricsArch.__table__.c.fcol16,
        'net_tx_min':MetricsArch.__table__.c.icol13,
        'net_tx_max':MetricsArch.__table__.c.icol14,
        'net_tx_stddev':MetricsArch.__table__.c.fcol17,
        'net_rx_avg':MetricsArch.__table__.c.fcol18,
        'net_rx_min':MetricsArch.__table__.c.icol15,
        'net_rx_max':MetricsArch.__table__.c.icol16,
        'net_rx_stddev':MetricsArch.__table__.c.fcol19,
        'gb_local_avg':MetricsArch.__table__.c.fcol20,
        'gb_local_min':MetricsArch.__table__.c.fcol21,
        'gb_local_max':MetricsArch.__table__.c.fcol22,
        'gb_local_stddev':MetricsArch.__table__.c.fcol23,
        'gb_poolused_avg':MetricsArch.__table__.c.fcol24,
        'gb_poolused_min':MetricsArch.__table__.c.fcol25,
        'gb_poolused_max':MetricsArch.__table__.c.fcol26,
        'gb_poolused_stddev':MetricsArch.__table__.c.fcol27,
        'gb_pooltotal_avg':MetricsArch.__table__.c.fcol28,
        'gb_pooltotal_min':MetricsArch.__table__.c.fcol29,
        'gb_pooltotal_max':MetricsArch.__table__.c.fcol30,
        'gb_pooltotal_stddev':MetricsArch.__table__.c.fcol31,
        'cpu_util_stddev':MetricsArch.__table__.c.cdate
        }
        )

        self.MetricVMRawMapper = mapper(MetricVMRaw,Metrics.__table__,properties={
        'entity_id':Metrics.__table__.c.entity_id,
        'cloud_entity_id':Metrics.__table__.c.cloud_entity_id,
        'state':Metrics.__table__.c.state,
        'metric_type':Metrics.__table__.c.metric_type,
        'cdate':Metrics.__table__.c.cdate,
        'cpu_util':Metrics.__table__.c.fcol1,
        'vm_cpu_util':Metrics.__table__.c.fcol6,
        'mem_util':Metrics.__table__.c.fcol2,
        'vbds':Metrics.__table__.c.icol1,
        'vbd_oo':Metrics.__table__.c.icol2,
        'vbd_rd':Metrics.__table__.c.icol3,
        'vbd_wr':Metrics.__table__.c.icol4,
        'net':Metrics.__table__.c.icol5,
        'net_tx':Metrics.__table__.c.icol6,
        'net_rx':Metrics.__table__.c.icol7,
        'gb_local':Metrics.__table__.c.fcol3,
        'gb_poolused':Metrics.__table__.c.fcol4,
        'gb_pooltotal':Metrics.__table__.c.fcol5
        }
        )

        self.MetricVMCurrMapper = mapper(MetricVMCurr,MetricsCurr.__table__,properties={
        'entity_id':MetricsCurr.__table__.c.entity_id,
        'cloud_entity_id':MetricsCurr.__table__.c.cloud_entity_id,
        'state':MetricsCurr.__table__.c.state,
        'metric_type':MetricsCurr.__table__.c.metric_type,
        'cdate':MetricsCurr.__table__.c.cdate,
        'cpu_util':MetricsCurr.__table__.c.fcol1,
        'vm_cpu_util':MetricsCurr.__table__.c.fcol6,
        'mem_util':MetricsCurr.__table__.c.fcol2,
        'vbds':MetricsCurr.__table__.c.icol1,
        'vbd_oo':MetricsCurr.__table__.c.icol2,
        'vbd_rd':MetricsCurr.__table__.c.icol3,
        'vbd_wr':MetricsCurr.__table__.c.icol4,
        'net':MetricsCurr.__table__.c.icol5,
        'net_tx':MetricsCurr.__table__.c.icol6,
        'net_rx':MetricsCurr.__table__.c.icol7,
        'gb_local':MetricsCurr.__table__.c.fcol3,
        'gb_poolused':MetricsCurr.__table__.c.fcol4,
        'gb_pooltotal':MetricsCurr.__table__.c.fcol5
        }
        )

        self.MetricVMRollupMapper = mapper(MetricVMRollup,MetricsArch.__table__,properties={
        'entity_id':MetricsArch.__table__.c.entity_id,
        'cloud_entity_id':MetricsArch.__table__.c.cloud_entity_id,
        'state':MetricsArch.__table__.c.state,
        'metric_type':MetricsArch.__table__.c.metric_type,
        'rollup_type':MetricsArch.__table__.c.rollup_type,
        'cdate':MetricsArch.__table__.c.cdate, 
        'cpu_util_avg':MetricsArch.__table__.c.fcol1,
        'cpu_util_min':MetricsArch.__table__.c.fcol2,
        'cpu_util_max':MetricsArch.__table__.c.fcol3,
        'cpu_util_stddev':MetricsArch.__table__.c.fcol4,
        'vm_cpu_util_avg':MetricsArch.__table__.c.fcol40,
        'vm_cpu_util_min':MetricsArch.__table__.c.fcol41,
        'vm_cpu_util_max':MetricsArch.__table__.c.fcol42,
        'vm_cpu_util_stddev':MetricsArch.__table__.c.fcol43,
        'mem_util_avg':MetricsArch.__table__.c.fcol5,
        'mem_util_min':MetricsArch.__table__.c.fcol6,
        'mem_util_max':MetricsArch.__table__.c.fcol7,
        'mem_util_stddev':MetricsArch.__table__.c.fcol8,
        'vbds_avg':MetricsArch.__table__.c.fcol9,
        'vbds_min':MetricsArch.__table__.c.icol1,
        'vbds_max':MetricsArch.__table__.c.icol2,
        'vbds_stddev':MetricsArch.__table__.c.fcol9,
        'vbd_oo_avg':MetricsArch.__table__.c.icol3,
        'vbd_oo_min':MetricsArch.__table__.c.icol4,
        'vbd_oo_max':MetricsArch.__table__.c.icol5,
        'vbd_oo_stddev':MetricsArch.__table__.c.fcol10,
        'vbd_rd_avg':MetricsArch.__table__.c.fcol11,
        'vbd_rd_min':MetricsArch.__table__.c.icol6,
        'vbd_rd_max':MetricsArch.__table__.c.icol7,
        'vbd_rd_stddev':MetricsArch.__table__.c.icol8,
        'vbd_wr_avg':MetricsArch.__table__.c.fcol12,
        'vbd_wr_min':MetricsArch.__table__.c.icol9,
        'vbd_wr_max':MetricsArch.__table__.c.icol10,
        'vbd_wr_stddev':MetricsArch.__table__.c.fcol13,
        'net_avg':MetricsArch.__table__.c.fcol14,
        'net_min':MetricsArch.__table__.c.icol11,
        'net_max':MetricsArch.__table__.c.icol12,
        'net_stddev':MetricsArch.__table__.c.fcol15,
        'net_tx_avg':MetricsArch.__table__.c.fcol16,
        'net_tx_min':MetricsArch.__table__.c.icol13,
        'net_tx_max':MetricsArch.__table__.c.icol14,
        'net_tx_stddev':MetricsArch.__table__.c.fcol17,
        'net_rx_avg':MetricsArch.__table__.c.fcol18,
        'net_rx_min':MetricsArch.__table__.c.icol15,
        'net_rx_max':MetricsArch.__table__.c.icol16,
        'net_rx_stddev':MetricsArch.__table__.c.fcol19,
        'gb_local_avg':MetricsArch.__table__.c.fcol20,
        'gb_local_min':MetricsArch.__table__.c.fcol21,
        'gb_local_max':MetricsArch.__table__.c.fcol22,
        'gb_local_stddev':MetricsArch.__table__.c.fcol23,
        'gb_poolused_avg':MetricsArch.__table__.c.fcol24,
        'gb_poolused_min':MetricsArch.__table__.c.fcol25,
        'gb_poolused_max':MetricsArch.__table__.c.fcol26,
        'gb_poolused_stddev':MetricsArch.__table__.c.fcol27,
        'gb_pooltotal_avg':MetricsArch.__table__.c.fcol28,
        'gb_pooltotal_min':MetricsArch.__table__.c.fcol29,
        'gb_pooltotal_max':MetricsArch.__table__.c.fcol30,
        'gb_pooltotal_stddev':MetricsArch.__table__.c.fcol31,
        'cpu_util_stddev':MetricsArch.__table__.c.cdate
        }
        )
    def getClass(self, mapper_name):
        class_name = self.mapper_class_dict[mapper_name]
        return class_name

    def getClassfromMetricType(self, metric_type):
        class_name = self.metricType_class_dict[metric_type]
        return class_name
    ##########ppp
    def setClass(self, mapper_name, class_name):
        self.mapper_class_dict.update({mapper_name:class_name})

    def UpdateclassMetricTypeLookup(self, mapper_name, class_name):
        #class_name(mapper_name)
        self.metricType_class_dict.update({mapper_name:class_name})

    def insert_rollupstatus_record(self, entity_id, rollup_type):
        defaultDate = constants.defaultDate
        try:
            # query rollupstatus table to read the last_rollup_time
            rollupStatusResult = DBSession.query(rollupStatus).filter(rollupStatus.entity_id==entity_id).filter(rollupStatus.rollup_type==rollup_type).first()
        except:
            rollupStatusResult = None

        # if table has record
        if  rollupStatusResult:
            # read the last_rollup_time
            defaultDate = rollupStatusResult.last_rollup_time
        else:
            # add new entry for given entity id with default date
            rollup_staus_obj = rollupStatus()
            rollup_staus_obj.last_rollup_time = defaultDate
            rollup_staus_obj.rollup_type = rollup_type
            rollup_staus_obj.entity_id = entity_id
            DBSession.add(rollup_staus_obj) 
        
        return defaultDate


    def update_rollupstatus_record(self, entity_id, formatted_uptoDate, rollup_type):
        try:
            rollupStatusResult = DBSession.query(rollupStatus).filter(rollupStatus.entity_id == entity_id).filter(rollupStatus.rollup_type == rollup_type).first()
            if rollupStatusResult:
                rollupStatusResult.last_rollup_time = formatted_uptoDate
        except Exception as ex:
            LOGGER.error(to_str(ex))
            LOGGER.debug('Failed: update_rollupstatus_record')
            raise


    def find_date_for_week_rollup(self):
        weekNo = int(datetime.now().strftime('%U'))
        first_date_of_year = date(datetime.now().year, 1, 1)
        if first_date_of_year.weekday() > 3:
            last_date_week = first_date_of_year + timedelta(7 - first_date_of_year.weekday())
        else:
            last_date_week = first_date_of_year - timedelta(first_date_of_year.weekday())
        no_of_days = timedelta(days=(weekNo - 1) * 7)
        weekBeforeToDate = last_date_week + no_of_days + timedelta(days=6)
        return weekBeforeToDate


    def last_date_of_previous_month(self, year, month):
        last_days = [31, 30, 29, 28, 27]
        for i in last_days:
            try:
                end = datetime(year, month, i)
            except ValueError:
                continue
            else:
                return end.date()
        return None


    def get_previous_hour(self):
        todays_date = datetime.now()
        hr = todays_date.strftime('%H')
        if int(hr) == 0:
            difference = timedelta(days=-1)
            uptoDate = (todays_date + difference).strftime('%Y-%m-%d %H')
        else:
            uptoDate = datetime(todays_date.year, todays_date.month, todays_date.day, todays_date.hour - 1, 59, 59).strftime('%Y-%m-%d %H')
        return uptoDate

#####################not
    def insert_timebased_rollup_record(self, row, uptoDate, metricTypeRollup, rollup_type, entity_id):
        row = list(row)
        for values in row:
            if values == None:
                row.__setitem__(row.index(values), 0)
        id = getHexID()
        db_type = get_dbtype()
        try:
            LockManager().get_lock(constants.METRICS, entity_id, constants.ROLLUP_METRICS, constants.Table_metrics_arch)
            if db_type == constants.ORACLE:
                try:
                    orac = "insert into metrics_arch (id, fcol1, fcol2, fcol3, fcol5, fcol6, fcol7, fcol9,icol1, icol2, icol3, icol4, icol5, fcol11, icol6, icol7, fcol12, icol9, icol10, fcol14, icol11, icol12, fcol16, icol13, icol14, fcol18, icol15, icol16, fcol20, fcol21, fcol22, fcol24, fcol25, fcol26, fcol28, fcol29, fcol30, fcol32, fcol33, fcol34, fcol36, fcol37, fcol38, fcol40, fcol41, fcol42, cdate, metric_type, rollup_type, entity_id, cloud_entity_id) values ('%s', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (id, row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27], row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36], row[37], row[38], row[39], row[40], row[41], row[45], row[46], row[47], "to_date('" + to_str(uptoDate) + "','" + to_str('yyyy-mm-dd hh24:mi:ss') + "')", metricTypeRollup, rollup_type, entity_id, row[44])
                    LOGGER.debug(orac)
                    DBSession.execute(orac)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    raise e
            else:
                DBSession.execute("insert into metrics_arch (id, fcol1, fcol2, fcol3, fcol5, fcol6, fcol7, fcol9,icol1, icol2, icol3, icol4, icol5, fcol11, icol6, icol7, fcol12, icol9, icol10, fcol14, icol11, icol12, fcol16, icol13, icol14, fcol18, icol15, icol16, fcol20, fcol21, fcol22, fcol24, fcol25, fcol26, fcol28, fcol29, fcol30, fcol32, fcol33, fcol34, fcol36, fcol37, fcol38, fcol40, fcol41, fcol42, cdate, metric_type, rollup_type, entity_id, cloud_entity_id) values ('%s', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (id, row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21], row[22], row[23], row[24], row[25], row[26], row[27], row[28], row[29], row[30], row[31], row[32], row[33], row[34], row[35], row[36], row[37], row[38], row[39], row[40], row[41], row[45], row[46], row[47], uptoDate, metricTypeRollup, rollup_type, entity_id, row[44]))
        finally:
            LockManager().release_lock()

###################not
    def fetch_timebased_rollup_records(self, date_format_string, groupby_format_string, defaultDate, uptoDate, entity_id, metricType, condition=''):
        db_type = get_dbtype()

        if db_type == constants.SQLITE:
            if groupby_format_string=='%U' :
                groupby_format_string='%W'
            resultSet = DBSession.execute('select avg(fcol1), min(fcol1), max(fcol1),avg(fcol2), min(fcol2), max(fcol2),avg(icol1), min(icol1), max(icol1),avg(icol2), min(icol2), max(icol2),avg(icol3), min(icol3), max(icol3),avg(icol4), min(icol4), max(icol4),avg(icol5), min(icol5), max(icol5),avg(icol6), min(icol6), max(icol6),avg(icol7), min(icol7), max(icol7),avg(fcol3), min(fcol3), max(fcol3),avg(fcol4), min(fcol4), max(fcol4),avg(fcol5), min(fcol5), max(fcol5),avg(fcol9),min(fcol9),max(fcol9),avg(fcol10),min(fcol10),max(fcol10),strftime("' + to_str(groupby_format_string) + '", ' + 'cdate' + '),strftime("' + to_str(date_format_string) + '", ' + 'cdate' + '), cloud_entity_id, avg(fcol6), min(fcol6), max(fcol6) from metrics where cdate>= "' + to_str(defaultDate) + '" and  cdate< "' + to_str(uptoDate) + '" and entity_id = "' + to_str(entity_id) + '" and metric_type = ' + to_str(metricType) + condition + ' group by strftime("' + to_str(groupby_format_string) + '", ' + 'cdate' + ');')

        elif db_type == constants.MYSQL:
            resultSet = DBSession.execute('select avg(fcol1), min(fcol1), max(fcol1),avg(fcol2), min(fcol2), max(fcol2),avg(icol1), min(icol1), max(icol1),avg(icol2), min(icol2), max(icol2),avg(icol3), min(icol3), max(icol3),avg(icol4), min(icol4), max(icol4),avg(icol5), min(icol5), max(icol5),avg(icol6), min(icol6), max(icol6),avg(icol7), min(icol7), max(icol7),avg(fcol3), min(fcol3), max(fcol3),avg(fcol4), min(fcol4), max(fcol4),avg(fcol5), min(fcol5), max(fcol5),avg(fcol9),min(fcol9),max(fcol9),avg(fcol10),min(fcol10),max(fcol10),date_format(cdate,"' + to_str(groupby_format_string) + '"),date_format(cdate,"' + to_str(date_format_string) + '"), cloud_entity_id, avg(fcol6), min(fcol6), max(fcol6) from metrics where cdate>= "' + to_str(defaultDate) + '" and  cdate< "' + to_str(uptoDate) + '" and entity_id = "' + to_str(entity_id) + '" and metric_type = ' + to_str(metricType) + condition + ' group by date_format(cdate,"' + to_str(groupby_format_string) + '" );')

        elif db_type == constants.ORACLE:
            try:
                orac = "select avg(fcol1), min(fcol1), max(fcol1),avg(fcol2), min(fcol2), max(fcol2),avg(icol1), min(icol1), max(icol1),avg(icol2), min(icol2), max(icol2),avg(icol3), min(icol3), max(icol3),avg(icol4), min(icol4), max(icol4),avg(icol5), min(icol5), max(icol5),avg(icol6), min(icol6), max(icol6),avg(icol7), min(icol7), max(icol7),avg(fcol3), min(fcol3), max(fcol3),avg(fcol4), min(fcol4), max(fcol4),avg(fcol5), min(fcol5), max(fcol5),avg(fcol9),min(fcol9),max(fcol9),avg(fcol10),min(fcol10),max(fcol10),to_char(cdate,'" + to_str(groupby_format_string) + "'),to_char(cdate,'" + to_str(date_format_string) + "'), cloud_entity_id, avg(fcol6), min(fcol6), max(fcol6) from metrics where cdate>= to_date('" + to_str(defaultDate) + "','yyyy-mm-dd hh24:mi:ss') and  cdate< to_date('" + to_str(uptoDate) + "','yyyy-mm-dd hh24:mi:ss') and entity_id = '" + to_str(entity_id) + "' and metric_type = " + to_str(metricType) + condition + " group by to_char(cdate, '" + to_str(groupby_format_string) + "'), to_char(cdate, '" + to_str(date_format_string) + "')  "
                LOGGER.debug(orac)
                resultSet = DBSession.execute(orac)
            except Exception as e:
                import traceback
                traceback.print_exc()
                raise e
        return resultSet


    def get_row_date(self, row, rollup_type):
        tmprow = list(row)
        dateval = tmprow[43]
        year = int(dateval[:4])
        month = int(dateval[5:7])
        if rollup_type == constants.HOURLY:
            day = int(dateval[8:10])
            hour = int(dateval[11:13])
            rowdate = datetime(year, month, day, hour)
        elif rollup_type == constants.DAILY:
            day = int(dateval[8:10])
            rowdate = datetime(year, month, day)
        elif rollup_type == constants.WEEKLY:
            day = int(dateval[8:10])
            rowdate = datetime(year, month, day)
        elif rollup_type == constants.MONTHLY:
            rowdate = datetime(year, month, 1)
        return rowdate

#############not
    def performDayRollUp(self, metricType, rollup_type, metricTypeRollup, entity_id, condition=''):
        today = datetime.now()
        uptoDate = today.strftime('%Y-%m-%d')
        defaultDate = self.insert_rollupstatus_record(entity_id, rollup_type)
        year = int(uptoDate[:4])
        month = int(uptoDate[5:7])
        day = int(uptoDate[8:10])
        formatted_uptoDate = datetime(year, month, day)
        db_type = get_dbtype()
        if db_type == constants.ORACLE:
            date_format_string = 'yyyy-mm-dd'
            groupby_format_string = 'yyyy-mm-dd'
            uptoDate = today.strftime('%Y-%m-%d %H:%M:%S')
        else:
            date_format_string = '%Y-%m-%d'
            groupby_format_string = '%Y-%m-%d'
        resultSet = self.fetch_timebased_rollup_records(date_format_string, groupby_format_string, defaultDate, uptoDate, entity_id, metricType, condition)
        while (1):
            row = resultSet.fetchone()
            if row == None:
                break
            else:
                rowdate=self.get_row_date(row,rollup_type)
                self.insert_timebased_rollup_record(row, rowdate, metricTypeRollup, rollup_type, entity_id)
        self.update_rollupstatus_record(entity_id,formatted_uptoDate,rollup_type)

##########not
    def performMonthRollUp(self, metricType, rollup_type, metricTypeRollup, entity_id, condition=''):
        today = datetime.now()
        uptoDate = date(today.year, today.month, 1)
        formatted_uptoDate = uptoDate
        defaultDate = self.insert_rollupstatus_record(entity_id, rollup_type)
        db_type = get_dbtype()
        if db_type == constants.ORACLE:
            date_format_string = 'yyyy-mm'
            groupby_format_string = 'yyyy-mm'
            uptoDate = today.strftime('%Y-%m-%d %H:%M:%S')
        else:
            date_format_string = '%Y-%m'
            groupby_format_string = '%Y-%m'
        resultSet = self.fetch_timebased_rollup_records(date_format_string, groupby_format_string, defaultDate, uptoDate, entity_id, metricType, condition)

        while (1):
            row = resultSet.fetchone()
            if row == None:
                break
            else:
                rowdate = self.get_row_date(row, rollup_type)
                self.insert_timebased_rollup_record(row, rowdate, metricTypeRollup, rollup_type, entity_id)
        self.update_rollupstatus_record(entity_id, formatted_uptoDate, rollup_type)

##########not
    def performHourRollUp(self, metricType, rollup_type, metricTypeRollup, entity_id, condition=''):
        today = datetime.now()
        uptoDate = today.strftime('%Y-%m-%d %H')
        year = int(uptoDate[:4])
        month = int(uptoDate[5:7])
        day = int(uptoDate[8:10])
        hour = int(uptoDate[11:13])
        formatted_uptoDate = datetime(year, month, day, hour)
        defaultDate = self.insert_rollupstatus_record(entity_id, rollup_type)
        db_type = get_dbtype()
        if db_type == constants.ORACLE:
            date_format_string = 'yyyy-mm-dd hh24'
            groupby_format_string = 'yyyy-mm-dd hh24'
            uptoDate = today.strftime('%Y-%m-%d %H:%M:%S')
        else:
            date_format_string = '%Y-%m-%d %H'
            groupby_format_string = '%Y-%m-%d %H'
        resultSet = self.fetch_timebased_rollup_records(date_format_string, groupby_format_string, defaultDate, uptoDate, entity_id, metricType, condition)
        while (1):
            row = resultSet.fetchone()
            if row == None:
                break
            else:
                rowdate = self.get_row_date(row, rollup_type)
                self.insert_timebased_rollup_record(row, rowdate, metricTypeRollup, rollup_type, entity_id)
        self.update_rollupstatus_record(entity_id, formatted_uptoDate, rollup_type)


    def performWeekRollUp(self, metricType, rollup_type, metricTypeRollup, entity_id, condition=''):
        today = datetime.now()
        weekdays = today.weekday()
        weekStartDate = datetime(today.year, today.month, today.day) + timedelta(days=-weekdays)
        uptoDate = weekStartDate.strftime('%Y-%m-%d')
        year = int(uptoDate[:4])
        month = int(uptoDate[5:7])
        day = int(uptoDate[8:10])
        formatted_uptoDate = datetime(year, month, day)
        defaultDate = self.insert_rollupstatus_record(entity_id, rollup_type)
        db_type = get_dbtype()
        if db_type == constants.ORACLE:
            date_format_string = 'yyyy-mm-dd'
            groupby_format_string = 'ww'
            uptoDate = today.strftime('%Y-%m-%d %H:%M:%S')
        else:
            date_format_string = '%Y-%m-%d'
            groupby_format_string = '%U'
        resultSet = self.fetch_timebased_rollup_records(date_format_string, groupby_format_string, defaultDate, uptoDate, entity_id, metricType, condition)
        while (1):
            row = resultSet.fetchone()
            if row == None:
                break
            else:
                rowdate = self.get_row_date(row, rollup_type)
                self.insert_timebased_rollup_record(row, rowdate, metricTypeRollup, rollup_type, entity_id)
        self.update_rollupstatus_record(entity_id, formatted_uptoDate, rollup_type)


    def insertServerMetricsData(self, dict_data, node_id, metrics_obj):
        strt = p_task_timing_start(MTR_LOGGER, "InsertServerMetrics", node_id, log_level="DEBUG")
        # create a list of metrics_types to be updated
        metric_type_list = [constants.SERVER_RAW, constants.SERVER_CURR]
        # loop to update VM_CURR and VM_RAW metrics
        for metric_type in metric_type_list:
            # delete previous entry for the passed node_id from VM_CURR metrics
            if metric_type == constants.SERVER_CURR:
                metrics_obj = MetricServerCurr()
                try:
                    self.DeleteCurrentMetrics(constants.SERVER_CURR, node_id)
                except Exception, ex:
                    LOGGER.error(to_str(ex))
                    LOGGER.debug('Failed: insertServerMetricsData')
                    raise

            # to retrive the integer from string '1024k'
            server_mem = dict_data.get('SERVER_MEM')
            if server_mem:
                server_mem = float(server_mem[:-1])
            server_cpus=dict_data.get('SERVER_CPUs')
            #to retrive the integer from string '2 @ 1864MHz'
            if server_cpus:
                server_cpus = int(server_cpus.split(' ')[0])
            metrics_obj.entity_id = node_id
            metrics_obj.metric_type = metric_type
            metrics_obj.cpu_util=dict_data.get('VM_TOTAL_CPU(%)',0.00)
            metrics_obj.mem_util=dict_data.get('VM_TOTAL_MEM(%)',0.00)
            metrics_obj.vbds=dict_data.get('VM_TOTAL_VBDS')
            metrics_obj.vbd_oo=dict_data.get('VM_TOTAL_VBD_OO')
            metrics_obj.vbd_rd=dict_data.get('VM_TOTAL_VBD_RD')
            metrics_obj.vbd_wr=dict_data.get('VM_TOTAL_VBD_WR')
            metrics_obj.net=dict_data.get('VM_TOTAL_NETS')
            metrics_obj.net_tx=dict_data.get('VM_TOTAL_NETTX(k)')
            metrics_obj.net_rx=dict_data.get('VM_TOTAL_NETRX(k)')
            metrics_obj.gb_local = dict_data.get('VM_LOCAL_STORAGE',0.00)
            metrics_obj.gb_poolused = dict_data.get('VM_SHARED_STORAGE',0.00)
            metrics_obj.gb_pooltotal = dict_data.get('VM_TOTAL_STORAGE',0.00)
            metrics_obj.cdate=datetime.now()
            metrics_obj.state=to_unicode(dict_data.get('NODE_STATUS'))
            metrics_obj.paused_vms=dict_data.get('PAUSED_VMs',0)
            metrics_obj.running_vms=dict_data.get('RUNNING_VMs',0)
            metrics_obj.crahsed_vms=dict_data.get('CRASHED_VMs',0)
            metrics_obj.total_mem=dict_data.get('VM_TOTAL_MEM',0.000)
            metrics_obj.total_cpu=dict_data.get('VM_TOTAL_CPU',0)
            metrics_obj.total_vms=dict_data.get('TOTAL_VMs',0)
            metrics_obj.server_cpus=server_cpus
            metrics_obj.server_mem=server_mem
            metrics_obj.host_mem=dict_data.get('HOST_MEM(%)',0.00)
            metrics_obj.host_cpu=dict_data.get('HOST_CPU(%)',0.00)
            DBSession.add(metrics_obj)
        p_task_timing_end(MTR_LOGGER, strt)


    def insertServerPoolMetricsData(self, dict_data, node_id, metrics_obj):
        strt = p_task_timing_start(MTR_LOGGER, "InsertServerPoolMetrics", node_id, log_level="DEBUG")
        metric_type_list = [constants.SERVERPOOL_RAW, constants.SERVERPOOL_CURR]
        # loop to update VM_CURR and VM_RAW metrics 
        for metric_type in metric_type_list:
            # delete previous entry for the passed node_id from VM_CURR metrics
            if metric_type == constants.SERVERPOOL_CURR:
                metrics_obj = ServerPoolCurr()
                try:
                    self.DeleteCurrentMetrics(constants.SERVERPOOL_CURR, node_id)
                except Exception, ex:
                    LOGGER.error(to_str(ex))
                    LOGGER.debug('Failed: insertServerPoolMetricsData')
                    raise
            metrics_obj.entity_id = node_id
            metrics_obj.metric_type = metric_type
            metrics_obj.cpu_util=dict_data.get('VM_TOTAL_CPU(%)',0.00)
            metrics_obj.mem_util=dict_data.get('VM_TOTAL_MEM(%)',0.00)
            metrics_obj.vbds=dict_data.get('VM_TOTAL_VBDS')
            metrics_obj.vbd_oo=dict_data.get('VM_TOTAL_VBD_OO')
            metrics_obj.vbd_rd=dict_data.get('VM_TOTAL_VBD_RD')
            metrics_obj.vbd_wr=dict_data.get('VM_TOTAL_VBD_WR')
            metrics_obj.net=dict_data.get('VM_TOTAL_NETS')
            metrics_obj.net_tx=dict_data.get('VM_TOTAL_NETTX(k)')
            metrics_obj.net_rx=dict_data.get('VM_TOTAL_NETRX(k)')
            metrics_obj.gb_local = dict_data.get('VM_LOCAL_STORAGE',0.00)
            metrics_obj.gb_poolused = dict_data.get('VM_SHARED_STORAGE',0.00)
            metrics_obj.gb_pooltotal = dict_data.get('VM_TOTAL_STORAGE',0.00)
            metrics_obj.cdate=datetime.now()
            metrics_obj.paused_vms=dict_data.get('PAUSED_VMs',0)
            metrics_obj.running_vms=dict_data.get('RUNNING_VMs',0)
            metrics_obj.crahsed_vms=dict_data.get('CRASHED_VMs',0)
            metrics_obj.total_mem=dict_data.get('VM_TOTAL_MEM',0.00)
            metrics_obj.total_cpu=dict_data.get('VM_TOTAL_CPU',0)
            metrics_obj.server_mem=dict_data.get('SERVER_MEM',0.00)
            metrics_obj.server_cpus=dict_data.get('SERVER_CPUs',0)
            metrics_obj.total_vms=dict_data.get('TOTAL_VMs',0)
            metrics_obj.server_count=dict_data.get('server_count',0)
            metrics_obj.nodes_connected=dict_data.get('NODES_CONNECTED',0)
            DBSession.add(metrics_obj)
            p_task_timing_end(MTR_LOGGER, strt)


    def insertMetricsData(self, dict_data, node_id, metrics_obj):
        metric_type_list = [constants.VM_RAW, constants.VM_CURR]
        strt = p_task_timing_start(MTR_LOGGER, "InsertVMMetrics", node_id, log_level="DEBUG")
        for metric_type in metric_type_list:
            if metric_type == constants.VM_CURR:
                metrics_obj = MetricVMCurr()
                try:
                    self.DeleteCurrentMetrics(constants.VM_CURR, node_id)
                except Exception, ex:
                    LOGGER.error(to_str(ex))
                    LOGGER.debug('Failed: insertMetricsData')
                    raise
            metrics_obj.state=to_unicode(dict_data.get('STATE'))
            metrics_obj.entity_id = node_id
            metrics_obj.cloud_entity_id = dict_data.get('CLOUD_VM_ID',None)
            metrics_obj.metric_type = metric_type
            metrics_obj.cpu_util=dict_data.get('CPU(%)',0)
            metrics_obj.vm_cpu_util=dict_data.get('VM_CPU(%)',0)
            metrics_obj.mem_util=dict_data.get('MEM(%)',0)
            metrics_obj.vbds=dict_data.get('VBDS',0)
            metrics_obj.vbd_oo=dict_data.get('VBD_OO',0)
            metrics_obj.vbd_rd=dict_data.get('VBD_RD',0)
            metrics_obj.vbd_wr=dict_data.get('VBD_WR',0)
            metrics_obj.net=dict_data.get('NETS',0)
            metrics_obj.net_tx=dict_data.get('NETTX(k)',0)
            metrics_obj.net_rx=dict_data.get('NETRX(k)',0)
            metrics_obj.gb_local = dict_data.get('VM_LOCAL_STORAGE',0)
            metrics_obj.gb_poolused = dict_data.get('VM_SHARED_STORAGE',0)
            metrics_obj.gb_pooltotal = dict_data.get('VM_TOTAL_STORAGE',0)
            metrics_obj.cdate=datetime.now()
            DBSession.add(metrics_obj)
        p_task_timing_end(MTR_LOGGER, strt)

    def timebasis_rollup_for_all_nodes(self, auth):
        serverpool_ents = auth.get_entities(to_unicode(constants.SERVER_POOL))
        for each_serverpool in serverpool_ents:
            metric_type_raw = constants.SERVERPOOL_RAW
            metric_type_rollup = constants.SERVERPOOL_ROLLUP
            self.performHourRollUp(metric_type_raw, constants.HOURLY, metric_type_rollup, each_serverpool.entity_id)
            self.performDayRollUp(metric_type_raw, constants.DAILY, metric_type_rollup, each_serverpool.entity_id)
            self.performWeekRollUp(metric_type_raw, constants.WEEKLY, metric_type_rollup, each_serverpool.entity_id)
            self.performMonthRollUp(metric_type_raw, constants.MONTHLY, metric_type_rollup, each_serverpool.entity_id)

            try:
                serverpool_ent = auth.get_entity(each_serverpool.entity_id)
                server_ents = auth.get_entities(to_unicode(constants.MANAGED_NODE), parent=serverpool_ent)
                for each_server in server_ents:
                    metric_type_raw = constants.SERVER_RAW
                    metric_type_rollup = constants.SERVER_ROLLUP
                    self.performHourRollUp(metric_type_raw, constants.HOURLY, metric_type_rollup, each_server.entity_id)
                    self.performDayRollUp(metric_type_raw, constants.DAILY, metric_type_rollup, each_server.entity_id)
                    self.performWeekRollUp(metric_type_raw, constants.WEEKLY, metric_type_rollup, each_server.entity_id)
                    self.performMonthRollUp(metric_type_raw, constants.MONTHLY, metric_type_rollup, each_server.entity_id)
                    vm_ent = auth.get_entity(each_server.entity_id)
                    vms = auth.get_entities(to_unicode(constants.DOMAIN), parent=vm_ent)
                    for each_vm in vms:
                        metric_type_raw = constants.VM_RAW
                        metric_type_rollup = constants.VM_ROLLUP
                        condition = ' and state != ' + to_str(VM.SHUTDOWN) + ' '
                        self.performHourRollUp(metric_type_raw, constants.HOURLY, metric_type_rollup, each_vm.entity_id, condition)
                        self.performDayRollUp(metric_type_raw, constants.DAILY, metric_type_rollup, each_vm.entity_id, condition)
                        self.performWeekRollUp(metric_type_raw, constants.WEEKLY, metric_type_rollup, each_vm.entity_id, condition)
                        self.performMonthRollUp(metric_type_raw, constants.MONTHLY, metric_type_rollup, each_vm.entity_id, condition)
            except Exception as ex:
                LOGGER.error(to_str(ex))
                LOGGER.debug('Failed: timebasis_rollup_for_all_nodes')
                raise


    def insert_into_purge_config(self, entity_id, data_type, retention_days):
        obj_purge_config = PurgeConfiguration()
        obj_purge_config.entity_id = entity_id
        obj_purge_config.data_type = data_type
        obj_purge_config.retention_days = retention_days
        DBSession.add(obj_purge_config)

    def get_purgeconfig_data(self, purge_day_data, purge_hr_data, purge_week_data, purge_month_data, purge_raw_data):
        purge_config_data = []
        individual_config_data = []
        todays_date = datetime.now()
        time_diff = timedelta(days=-int(purge_day_data))
        purge_before_date = (todays_date + time_diff).strftime('%Y-%m-%d')
        formatted_uptoDate = datetime(int(purge_before_date[:4]), int(purge_before_date[5:7]), int(purge_before_date[8:10]))
        data_type = constants.DAILY
        individual_config_data.append(data_type)
        individual_config_data.append(formatted_uptoDate)
        purge_config_data.append(individual_config_data)
        individual_config_data = []
        time_diff = timedelta(days=-int(purge_hr_data))
        purge_before_date = (todays_date + time_diff).strftime('%Y-%m-%d %H')
        formatted_uptoDate = datetime(int(purge_before_date[:4]), int(purge_before_date[5:7]), int(purge_before_date[8:10]), int(purge_before_date[11:13]))
        data_type = constants.HOURLY
        individual_config_data.append(data_type)
        individual_config_data.append(formatted_uptoDate)
        purge_config_data.append(individual_config_data)
        individual_config_data = []
        time_diff = timedelta(days=-int(purge_week_data))
        purge_before_date = (todays_date + time_diff).strftime('%Y-%m-%d')
        formatted_uptoDate = datetime(int(purge_before_date[:4]), int(purge_before_date[5:7]), int(purge_before_date[8:10]))
        data_type = constants.WEEKLY
        individual_config_data.append(data_type)
        individual_config_data.append(formatted_uptoDate)
        purge_config_data.append(individual_config_data)
        individual_config_data = []
        time_diff = timedelta(days=-int(purge_month_data))
        purge_before_date = (todays_date + time_diff).strftime('%Y-%m')
        formatted_uptoDate = datetime(int(purge_before_date[:4]), int(purge_before_date[5:7]), 1)
        data_type = constants.MONTHLY
        individual_config_data.append(data_type)
        individual_config_data.append(formatted_uptoDate)
        purge_config_data.append(individual_config_data)
        individual_config_data = []
        time_diff = timedelta(days=-int(purge_raw_data))
        purge_before_date = (todays_date + time_diff).strftime('%Y-%m-%d')
        formatted_uptoDate = datetime(int(purge_before_date[:4]), int(purge_before_date[5:7]), int(purge_before_date[8:10]))
        data_type = constants.RAW
        individual_config_data.append(data_type)
        individual_config_data.append(formatted_uptoDate)
        purge_config_data.append(individual_config_data)
        return purge_config_data

    def purging_for_all_nodes(self, auth):
        serverpool_ents = auth.get_entities(to_unicode(constants.SERVER_POOL))
        for serverpool_ids in serverpool_ents:
            self.purging(serverpool_ids.entity_id)
            try:
                serverpool_ent = auth.get_entity(serverpool_ids.entity_id)
                server_ents = auth.get_entities(to_unicode(constants.MANAGED_NODE), parent=serverpool_ent)
                for server_id in server_ents:
                    self.purging(server_id.entity_id)
                    vm_ent = auth.get_entity(server_id.entity_id)
                    vms = auth.get_entities(to_unicode(constants.DOMAIN), parent=vm_ent)
                    for each_vm in vms:
                        vmId = each_vm.entity_id
                        self.purging(vmId)
            except Exception as ex:
                LOGGER.error(to_str(ex))
                LOGGER.debug('Failed: purging_for_all_nodes')
                raise


    def purging(self, entity_id):
        purge_hr_data = tg.config.get('purge_hr_data', 0)
        purge_day_data = tg.config.get('purge_day_data', 0)
        purge_week_data = tg.config.get('purge_week_data', 0)
        purge_month_data = tg.config.get('purge_month_data', 0)
        purge_raw_data = tg.config.get('purge_raw_data', 0)
        resultSet = DBSession.query(PurgeConfiguration.data_type, PurgeConfiguration.retention_days).filter(PurgeConfiguration.entity_id == entity_id).all()
        if not resultSet:
            purge_config_data = self.get_purgeconfig_data(purge_day_data, purge_hr_data, purge_week_data, purge_month_data, purge_raw_data)
            purge_config_dict= {constants.HOURLY:purge_hr_data, constants.DAILY:purge_day_data, constants.WEEKLY:purge_week_data, constants.MONTHLY:purge_month_data, constants.RAW:purge_raw_data}
            for keys in purge_config_dict:
                self.insert_into_purge_config(entity_id, keys, purge_config_dict[keys])
        else:
            for individual_config_data in resultSet:
                individual_config_data = list(individual_config_data)
                purge_type = individual_config_data[PURGE_TYPE]
                purge_date = individual_config_data[PURGE_DATE]
                if purge_type == constants.DAILY:
                    purge_day_data = purge_date
                elif purge_type == constants.HOURLY:
                    purge_hr_data = purge_date
                elif purge_type == constants.WEEKLY:
                    purge_week_data = purge_date
                elif purge_type == constants.MONTHLY:
                    purge_month_data = purge_date
                else:
                    purge_raw_data = purge_date
                purge_config_data = self.get_purgeconfig_data(purge_day_data, purge_hr_data, purge_week_data, purge_month_data, purge_raw_data)
        for individual_config_data in purge_config_data:
            if individual_config_data:
                purge_type = individual_config_data[PURGE_TYPE]
                if purge_type==constants.RAW: 
                    try:
                        try:
                            #DBSession.query(Metrics).filter(Metrics.entity_id==entity_id).filter(Metrics.cdate <= individual_config_data[PURGE_DATE]).delete()
                            LockManager().get_lock(constants.METRICS,entity_id, constants.PURGE_METRICS, constants.Table_metrics)
                            xs=DBSession.query(Metrics).filter(Metrics.entity_id==entity_id).filter(Metrics.cdate <= individual_config_data[PURGE_DATE]).all()
                            for x in xs:
                                DBSession.delete(x)
                        except Exception, ex:
                            LOGGER.error(to_str(ex))
                            LOGGER.debug('Failed: purging')
                            raise
                    finally:
                        LockManager().release_lock()

                else: # purge ROLLUP table entries
                    try:
                        try:
                            #DBSession.query(MetricsArch).filter(MetricsArch.entity_id==entity_id).filter(MetricsArch.rollup_type==individual_config_data[PURGE_TYPE]).filter(MetricsArch.cdate <= individual_config_data[PURGE_DATE]).delete()
                            LockManager().get_lock(constants.METRICS,entity_id, constants.PURGE_METRICS, constants.Table_metrics_arch)
                            xs=DBSession.query(MetricsArch).filter(MetricsArch.entity_id==entity_id).filter(MetricsArch.rollup_type==individual_config_data[PURGE_TYPE]).filter(MetricsArch.cdate <= individual_config_data[PURGE_DATE]).all()
                            for x in xs:
                                DBSession.delete(x)
                        
                        except Exception, ex:
                            LOGGER.error(to_str(ex))
                            LOGGER.debug('Failed: purging')
                            raise
                    finally:
                        LockManager().release_lock()

    def getVMCurrMetricsData(self, metric_type, node_id, auth):
        class_name = self.getClassfromMetricType(metric_type)
        currVMMetricsData = None
        try:
            currVMMetricsData = DBSession.query(class_name).filter(class_name.entity_id == node_id.entity_id).filter(class_name.metric_type == metric_type).first()
        except Exception as ex:
            LOGGER.error(to_str(ex))
            LOGGER.debug('Failed: getVMCurrMetricsData')
            raise
        return currVMMetricsData


    def getServerCurrMetricsData(self, metric_type, node_id):
        class_name = self.getClassfromMetricType(metric_type)
        currMetricsData = None
        try:
            currMetricsData = DBSession.query(class_name).filter(class_name.entity_id == node_id).filter(class_name.metric_type == metric_type).first()
        except Exception as ex:
            LOGGER.error(to_str(ex))
            LOGGER.debug('Failed: getServerCurrMetricsData')
            raise
        return currMetricsData


    def getServerMetrics(self, node_id, hrs):
        metric_type=constants.SERVER_ROLLUP
        to_date=datetime.now()

        if hrs is None or hrs==0 or hrs==1:
            metric_type=constants.SERVER_RAW
            hrs=1
        class_name = self.getClassfromMetricType(metric_type)
        if metric_type == constants.SERVER_ROLLUP:
            col1=class_name.cpu_util_avg
            col2=class_name.mem_util_avg            
        elif  metric_type == constants.SERVER_RAW:
            col1=class_name.cpu_util
            col2=class_name.mem_util
        from_date=to_date+timedelta(seconds=-(hrs*60*60))
        query=DBSession.query(func.sum(col1)/func.count(col1),func.sum(col2)/func.count(col2),class_name.entity_id, class_name.cdate).\
                filter(class_name.entity_id==node_id).\
                filter(class_name.metric_type==metric_type).\
                filter(class_name.cdate>=from_date).\
                filter(class_name.cdate<=to_date)
        query=query.group_by(class_name.entity_id)
        rawList=query.first()        
        metrics={}
        metrics['VM_TOTAL_CPU(%)']=0.0
        metrics['VM_TOTAL_MEM(%)']=0.0
        if rawList is not None:
            rawData = list(rawList)
            metrics['VM_TOTAL_CPU(%)']=rawData[0]
            metrics['VM_TOTAL_MEM(%)']=rawData[1]            
        return metrics

    def getRawData(self, entity_id, metric_type, from_date, to_date):
        class_name = self.getClassfromMetricType(metric_type)
        raw_data_list = []
        for rawData in DBSession.query(class_name.cpu_util, class_name.mem_util, class_name.vbds, class_name.vbd_oo, class_name.vbd_rd, class_name.vbd_wr, class_namenet, class_name.net_tx, class_name.net_rx, class_name.gb_local, class_name.gb_poolused, class_name.gb_pooltotal, class_name.state, class_name.metric_type, class_name.cdate).filter(class_name.entity_id == entity_id).filter(class_name.metric_type == metric_type).filter(class_name.cdate >= from_date).filter(class_name.cdate <= to_date).all():
            rawDataList = list(rawData)
            raw_data_list.append(rawDataList)
        return raw_data_list


    def getRawCpuAndMemData(self, entity_id, metric_type, from_date, to_date, variance_from_date):
        class_name = self.getClassfromMetricType(metric_type)
        data = {}
        data['cpu_util_sum'] = 0
        data['cpu_util_avg'] = 0
        data['cpu_util_var'] = 0
        data['mem_util_sum'] = 0
        data['mem_util_avg'] = 0
        #class_name = MetricServerRaw
        subqry = DBSession.query(func.variance(class_name.cpu_util)).filter(class_name.entity_id == entity_id).filter(class_name.metric_type == metric_type).filter(class_name.cdate >= variance_from_date).filter(class_name.cdate <= to_date).group_by(class_name.entity_id).subquery()
        resultSet = DBSession.query(func.sum(class_name.cpu_util), func.avg(class_name.cpu_util), subqry, func.sum(class_name.mem_util), func.avg(class_name.mem_util)).filter(class_name.entity_id == entity_id).filter(class_name.metric_type == metric_type).filter(class_name.cdate >= from_date).filter(class_name.cdate <= to_date).group_by(class_name.entity_id, subqry).all()
        #print subqry,'###3subqry###',resultSet,'###resultSet###',class_name,'####class_name',metric_type
        if resultSet:
            if resultSet[0][0] is not None:
                data['cpu_util_sum'] = resultSet[0][0]
            if resultSet[0][1] is not None:
                data['cpu_util_avg'] = resultSet[0][1]
            if resultSet[0][2] is not None:
                data['cpu_util_var'] = resultSet[0][2]
            if resultSet[0][3] is not None:
                data['mem_util_sum'] = resultSet[0][3]
            if resultSet[0][4] is not None:
                data['mem_util_avg'] = resultSet[0][4]
        return data


    def get_entity_col(self, class_name, cloud=False):
        entity_column = class_name.entity_id
        if cloud == True:
            entity_column = class_name.cloud_entity_id
        return entity_column


    def getRawMetricData(self, entity_ids, metric, metric_type, from_date, to_date, cloud=False):
        class_name = self.getClassfromMetricType(metric_type)
        raw_data_list = []
        col = self.getMetricCol(metric, metric_type, class_name, cloud)
        entity_column = self.get_entity_col(class_name, cloud)
        for rawData in DBSession.query(col, class_name.cdate).filter(entity_column.in_(entity_ids)).filter(class_name.metric_type == metric_type).filter(class_name.cdate >= from_date).filter(class_name.cdate <= to_date).all():
            rawDataList = list(rawData)
            raw_data_list.append(rawDataList)
        return raw_data_list


    def getRawTopMetric(self, entity_ids, metric, metric_type, from_date, to_date, order='DESC', limit=5, cloud=False):
        class_name = self.getClassfromMetricType(metric_type)
        raw_data_list = []
        col = self.getMetricCol(metric, metric_type, class_name, cloud)
        entity_column = self.get_entity_col(class_name, cloud)
        query = DBSession.query((func.sum(col) / func.count(col)).label('usge'), entity_column).filter(entity_column.in_(entity_ids)).filter(class_name.metric_type == metric_type).filter(class_name.cdate >= from_date).filter(class_name.cdate <= to_date)
        query = query.group_by(entity_column)
        query = query.order_by('usge ' + order)
        query = query.limit(limit)
        rawList = query.all()
        for rawData in rawList:
            rawDataList = list(rawData)
            raw_data_list.append(rawDataList)
        return raw_data_list


    def getRawAvg(self, entity_id, entity_type, metric, metric_type, from_date, to_date, cloud=False):
        class_name = self.getClassfromMetricType(metric_type)
        col = self.getMetricCol(metric, metric_type, class_name, cloud)
        entity_column = self.get_entity_col(class_name, cloud)
        avg = 0.0
        fquery = DBSession.query(func.avg(col)).filter(entity_column == entity_id).filter(class_name.metric_type == metric_type).filter(class_name.cdate >= from_date).filter(class_name.cdate <= to_date)
        if entity_type == constants.DOMAIN:
            fquery = fquery.filter(class_name.state != VM.SHUTDOWN)
        dataList = fquery.group_by(entity_column).all()
        if len(dataList) > 0:
            avg = dataList[0][0]
        return avg


    def getServerPoolCurrMetricsData(self, pool_id, metric_type):
        class_name = self.getClassfromMetricType(metric_type)
        rawDataList = []
        currMetricsData = None
        try:
            currMetricsData = DBSession.query(class_name).filter(class_name.entity_id == pool_id).filter(class_name.metric_type == metric_type).first()
        except Exception as ex:
            LOGGER.error(to_str(ex))
            LOGGER.debug('Failed: getServerPoolCurrMetricsData')
            raise
        return currMetricsData


    def getRollupData(self, entity_id, metric_type, from_date, to_date):
        class_name = self.getClassfromMetricType(metric_type)
        raw_data_list = []
        for rolupData in DBSession.query(class_name.state, class_name.metric_type, class_name.rollup_type, class_name.cdate, class_name.cpu_util_avg, class_name.cpu_util_min, class_name.cpu_util_max, class_name.cpu_util_stddev, class_name.mem_util_avg, class_name.mem_util_min, class_name.mem_util_min, class_name.mem_util_stddev, class_name.vbds_avg, class_name.vbds_min, class_name.vbds_max, class_name.vbds_stddev, class_name.vbd_oo_av, class_name.vbd_oo_min, class_name.vbd_oo_max, class_name.vbd_oo_stddev, class_name.vbd_rd_avg, class_name.vbd_rd_min, class_name.vbd_rd_min, class_name.vbd_rd_stddev, class_name.vbd_wr_avg, class_name.vbd_wr_min, class_name.vbd_wr_max, class_name.vbd_wr_stddev, class_name.net_avg, class_name.net_min, class_name.net_max, class_name.net_stddev, class_name.net_tx_avg, class_name.net_tx_min, class_name.net_tx_max, class_name.net_tx_stddev, class_name.net_rx_avg, class_name.net_rx_min, class_name.net_rx_max, class_name.net_rx_stddev, class_name.gb_local_avg, class_name.gb_local_min, class_name.gb_local_max, class_name.gb_local_stddev, class_name.gb_poolused_avg, class_name.gb_poolused_min, class_name.gb_poolused_max, class_name.gb_poolused_stddev, class_name.gb_pooltotal_avg, class_name.gb_pooltotal_min, class_name.gb_pooltotal_max, class_name.gb_pooltotal_stddev, class_name.entity_id).filter(class_name.entity_id == entity_id).filter(class_name.metric_type == metric_type).filter(class_name.cdate >= from_date).filter(class_name.cdate <= to_date).all():
            rollupDataList = list(rolupData)
            raw_data_list.append(rollupDataList)
        return raw_data_list


    def getRollupMetricData(self, entity_ids, metric, metric_type, rollup_type, from_date, to_date, cloud=False):
        class_name = self.getClassfromMetricType(metric_type)
        data_list = []
        col = self.getMetricCol(metric, metric_type, class_name, cloud)
        entity_column = self.get_entity_col(class_name, cloud)
        for data in DBSession.query(col, class_name.cdate, class_name.metric_type, class_name.rollup_type, entity_column).filter(entity_column.in_(entity_ids)).filter(class_name.metric_type == metric_type).filter(class_name.rollup_type == rollup_type).filter(class_name.cdate >= from_date).filter(class_name.cdate <= to_date).all():
            dataList = list(data)
            data_list.append(dataList)
        return data_list


    def getRollupAvg(self, entity_id, metric, metric_type, rollup_type, from_date, to_date, cloud=False):
        class_name = self.getClassfromMetricType(metric_type)
        col = self.getMetricCol(metric, metric_type, class_name, cloud)
        entity_column = self.get_entity_col(class_name, cloud)
        avg = 0.0
        dataList = DBSession.query(func.avg(col)).filter(entity_column == entity_id).filter(class_name.metric_type == metric_type).filter(class_name.rollup_type == rollup_type).filter(class_name.cdate >= from_date).filter(class_name.cdate <= to_date).group_by(entity_column).all()
        if len(dataList) > 0:
            avg = dataList[0][0]
        return avg


    def getRollupTop(self, entity_ids, metric, metric_type, rollup_type, from_date, to_date, order='DESC', limit=5, cloud=False):
        class_name = self.getClassfromMetricType(metric_type)
        data_list = []
        col = self.getMetricCol(metric, metric_type, class_name, cloud)
        query = DBSession.query((func.sum(col) / func.count(col)).label('usge'), class_name.entity_id).filter(class_name.entity_id.in_(entity_ids)).filter(class_name.metric_type == metric_type).filter(class_name.rollup_type == rollup_type).filter(class_name.cdate >= from_date).filter(class_name.cdate <= to_date)
        query = query.group_by(class_name.entity_id)
        query = query.order_by('usge ' + order)
        query = query.limit(limit)
        for data in query.all():
            dataList = list(data)
            data_list.append(dataList)
        return data_list


    def getCurrentTopMetricData(self, entity_ids, metric, metric_type, order='DESC', limit=5, cloud=False):
        class_name = self.getClassfromMetricType(metric_type)
        data_list = []
        col = self.getMetricCol(metric, metric_type, class_name, cloud)
        query = DBSession.query(col, class_name.entity_id, class_name.metric_type).filter(class_name.metric_type == metric_type)
        query = query.filter(class_name.entity_id.in_(entity_ids))
        if order == 'ASC':
            query = query.order_by(col.asc())
        else:
            query = query.order_by(col.desc())
        query = query.limit(limit)
        for data in query.all():
            dataList = list(data)
            data_list.append(dataList)
        return data_list

    ###############
    def getMetricCol(self, metric, metric_type, class_name, cloud=False):
        if metric == constants.METRIC_CPU:
            if metric_type in [constants.SERVER_RAW, constants.SERVER_CURR]:
                col = class_name.host_cpu
            elif metric_type in [constants.SERVER_ROLLUP]:
                col = class_name.host_cpu_avg
            if metric_type in [constants.VM_RAW,constants.VM_CURR]:
                if cloud == True:
                    col = class_name.vm_cpu_util
                else:
                    col = class_name.cpu_util
            elif metric_type in [constants.VM_ROLLUP]:
                if cloud == True:
                    col = class_name.vm_cpu_util_avg
                else:
                    col = class_name.cpu_util_avg
    
            elif metric_type in [constants.SERVERPOOL_RAW,constants.SERVERPOOL_CURR,\
                            constants.DATACENTER_RAW,constants.DATACENTER_CURR]:
                col = class_name.cpu_util
            elif metric_type in [constants.SERVERPOOL_ROLLUP,constants.DATACENTER_ROLLUP]:
                col = class_name.cpu_util_avg
        elif metric == constants.METRIC_VMCPU:
            if metric_type in [constants.VM_RAW, constants.VM_CURR]:
                col = class_name.vm_cpu_util
            elif metric_type in [constants.VM_ROLLUP]:
                col = class_name.vm_cpu_util_avg
        elif metric == constants.METRIC_MEM:
            if metric_type in [constants.SERVER_RAW, constants.SERVER_CURR]:
                col = class_name.host_mem
            elif metric_type in [constants.SERVER_ROLLUP]:
                col = class_name.host_mem_avg
            elif metric_type in [constants.VM_RAW, constants.VM_CURR, constants.SERVERPOOL_RAW, constants.SERVERPOOL_CURR, constants.DATACENTER_RAW, constants.DATACENTER_CURR]:
                col = class_name.mem_util
            elif metric_type in [constants.VM_ROLLUP, constants.SERVERPOOL_ROLLUP, constants.DATACENTER_ROLLUP]:
                col = class_name.mem_util_avg
        elif metric == constants.METRIC_NETWORKOUT:
            if metric_type in [constants.SERVER_RAW, constants.SERVER_CURR]:
                col = class_name.host_cpu
            elif metric_type in [constants.SERVER_ROLLUP]:
                col = class_name.host_cpu_avg
            elif metric_type in [constants.VM_RAW, constants.VM_CURR, constants.SERVERPOOL_RAW, constants.SERVERPOOL_CURR, constants.DATACENTER_RAW, constants.DATACENTER_CURR]:
                col = class_name.net_tx
            elif metric_type in [constants.VM_ROLLUP, constants.SERVERPOOL_ROLLUP, constants.DATACENTER_ROLLUP]:
                col = class_name.net_tx_avg
        elif metric == constants.METRIC_NETWORKIN:
            if metric_type in [constants.SERVER_RAW, constants.SERVER_CURR]:
                col = class_name.host_cpu
            elif metric_type in [constants.SERVER_ROLLUP]:
                col = class_name.host_cpu_avg
            elif metric_type in [constants.VM_RAW, constants.VM_CURR, constants.SERVERPOOL_RAW, constants.SERVERPOOL_CURR, constants.DATACENTER_RAW, constants.DATACENTER_CURR]:
                col = class_name.net_rx
            elif metric_type in [constants.VM_ROLLUP, constants.SERVERPOOL_ROLLUP, constants.DATACENTER_ROLLUP]:
                col = class_name.net_rx_avg
        elif metric == constants.METRIC_STORAGE:
            if metric_type in [constants.SERVER_RAW, constants.SERVER_CURR]:
                col = class_name.gb_local
            elif metric_type in [constants.SERVER_ROLLUP]:
                col = class_name.gb_local_avg
            elif metric_type in [constants.VM_RAW, constants.VM_CURR, constants.SERVERPOOL_RAW, constants.SERVERPOOL_CURR, constants.DATACENTER_RAW, constants.DATACENTER_CURR]:
                col = class_name.gb_poolused
            elif metric_type in [constants.VM_ROLLUP, constants.SERVERPOOL_ROLLUP, constants.DATACENTER_ROLLUP]:
                col = class_name.gb_poolused_avg
        return col


    def collect_serverpool_metrics(self, serverpool_id, connected, auth):
        strt = p_task_timing_start(MTR_LOGGER, "CollectServerPoolMetrics", serverpool_id)
        server_dict = {}
        # get the server ids list from the serverpool id 
        serverpool_ent =auth.get_entity(serverpool_id)
        managed_nodes=auth.get_entities(to_unicode(constants.MANAGED_NODE),parent=serverpool_ent)
        if managed_nodes:
            # sql to find sum of required colums of server metrics to create server pool metrics. 
            sql = 'select sum(fcol1), sum(fcol2), sum(icol1), sum(icol2), sum(icol3), sum(icol4), sum(icol5), sum(icol6), sum(icol7), sum(fcol3), sum(fcol4), sum(fcol5), sum(icol8), sum(icol9), sum(icol10), sum(icol11), sum(icol12), sum(fcol6), sum(fcol7), sum(fcol8), count(fcol8) from metrics_curr where metric_type = %s and entity_id in (' % constants.SERVER_CURR
            for node in managed_nodes: 
                sql+= ' "%s", ' % (node.entity_id)
            sql = sql[:-2]
            sql+= ')'
            resultSet = DBSession.execute(sql)
            record = resultSet.fetchone()
            server_dict['VM_TOTAL_CPU(%)'] = record[0]
            server_dict['VM_TOTAL_MEM(%)'] = record[1]
            server_dict['VM_TOTAL_VBDS'] = record[2]
            server_dict['VM_TOTAL_VBD_OO'] = record[3]
            server_dict['VM_TOTAL_VBD_RD'] = record[4]
            server_dict['VM_TOTAL_VBD_WR'] = record[5]
            server_dict['VM_TOTAL_NETS'] = record[6]
            server_dict['VM_TOTAL_NETTX(k)'] = record[7]
            server_dict['VM_TOTAL_NETRX(k)'] = record[8]
            server_dict['VM_LOCAL_STORAGE'] = record[9]
            server_dict['VM_SHARED_STORAGE'] = record[10]
            server_dict['VM_TOTAL_STORAGE'] = record[11]
            server_dict['TOTAL_VMs'] = record[12]
            server_dict['PAUSED_VMs']=record[13]
            server_dict['RUNNING_VMs']=record[14]
            server_dict['SERVER_CPUs']=record[15]
            server_dict['CRASHED_VMs']=record[16]
            server_dict['VM_TOTAL_MEM']=record[17]
            server_dict['VM_TOTAL_CPU']=record[18]
            server_dict['SERVER_MEM']=record[19]
            server_dict['entity_id']=serverpool_id
            server_dict['metric_type']=constants.SERVERPOOL_RAW
            server_dict['cdate']=datetime.now()
            server_dict['server_count']=record[20]
            server_dict['NODE_TYPE'] = 'SERVER_POOL'
            server_dict['NODES_CONNECTED'] = connected

            metrics_obj = ServerPoolRaw()
            self.insertServerPoolMetricsData(server_dict, serverpool_id, metrics_obj)
        p_task_timing_end(MTR_LOGGER, strt)

    def DeleteCurrentMetrics(self, metric_type, entity_id):
        class_name = self.getClassfromMetricType(metric_type)
        try:
            DBSession.query(class_name).filter(class_name.entity_id == entity_id).filter(class_name.metric_type == metric_type).delete()
        except Exception as ex:
            LOGGER.error(to_str(ex))
            LOGGER.debug('Failed: DeleteCurrentMetrics')
            raise ex




