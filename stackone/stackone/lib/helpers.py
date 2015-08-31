
"""WebHelpers used in stackone."""

from webhelpers import date, feedgenerator, html, number, misc, text

import tg

supported_languages = ['en','tr']

def decide_js_lang():
    return 'zh_CN'
    languages = tg.i18n.get_lang()
    if languages is not None:
        for l in languages:
            if l in supported_languages:
                return l
    return 'en'

def add_global_tmpl_vars():
    return dict(decide_js_lang=decide_js_lang)

