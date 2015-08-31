from stackone.model import DBSession
from stackone.model import Entity
def get_external_id(entity_id, auth=None):
    if auth:
        ent = auth.get_entity(entity_id)
    else:
        ent = DBSession.query(Entity).filter(Entity.entity_id == entity_id).first()
    if not ent:
        raise Exception('Could not find entity with entity_id:%s' % entity_id)
    else:
        ent_attr = ent.get_external_id()
        if not ent_attr:
            raise Exception('Could not find entity attribute with entity_id:%s' % entity_id)
        else:
            return ent_attr.value

def get_moid(instance):
    return instance._mo_ref.value

def convert_config_dict_to_str(config_options):
    import suds
    content = ''
    for name,value in config_options.iteritems():
        if isinstance(value, suds.sax.text.Text):
            content = content + "%s='%s'\n" % (name, repr(value))
            continue
        content = content + '%s=%s\n' % (name, repr(value))
    return content

def parse_datastore_name_from_vmw_diskpath(path):
    import re
    pattn = re.compile('^\\[[^]]+] ')
    m = pattn.match(path)
    if m:
        msg = 'Got vmware path %s' % path
        print msg
        res = m.group()
        return res.split('[')[1].split(']')[0]

def parse_datastore_name_from_stackone_diskpath(path):
    parts = path.split('/')
    if not len(parts) > 1:
        msg = 'ERROR: Invalid path:%s. path should be like /datastore1/test/test1.vmdk' % path
        raise Exception(msg)
    return parts[1]

def parse_datastore_name_from_diskpath(path):
    ds_name = parse_datastore_name_from_vmw_diskpath(path)
    if ds_name:
        return ds_name
    return parse_datastore_name_from_stackone_diskpath(path)

