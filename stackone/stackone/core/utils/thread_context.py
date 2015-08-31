import threading
import _threading_local
thread_ctx = _threading_local.local()
def get_thread_name():
    return threading.currentThread().getName()

def with_thread_context(_key, _value):
    def fn_with_context(fn):
        def wrapped_fn_with_context(*args, **kwargs):
            thread_name = get_thread_name() + ' '
            try:
                print thread_name,
                print thread_ctx.__dict__
                if _key:
                    if thread_ctx.__dict__.has_key(_key):
                        print thread_name + 'WARNING : Context already has key ',
                        print _key,
                        print 'Current ' + _value,
                        print 'Requested ' + thread_ctx.__dict__.get(_key)
                    else:
                        print thread_name + 'Adding ' + _key + ' to Context. Value ' + _value
                        thread_ctx.__dict__[_key] = _value
                else:
                    print thread_name + 'Nothing to add to Context'
                fn(*args, **kwargs)
            finally:
                if _key and thread_ctx.__dict__.has_key(_key):
                    del thread_ctx.__dict__[_key]
                    print thread_name + 'Cleaning %s from Context' % _key
                else:
                    print thread_name + 'Nothing to clean from Context'
        return wrapped_fn_with_context
    return fn_with_context

def get_thread_context(key):
    return thread_ctx.__dict__.get(key)

def get_subsystem_context():
    return get_thread_context('subsystem')

