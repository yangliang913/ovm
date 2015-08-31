import transaction
from sqlalchemy import *
from tg import expose, flash, require, url, request
from stackone.model import DBSession
class DBHelper():
    def get_session(self):
        return DBSession

    def add(self, obj):
        DBSession.add(obj)

    def update(self, obj):
        DBSession.add(obj)

    def add_all(self, obj_list):
        DBSession.add_all(obj_list)

    def delete(self, obj):
        DBSession.delete(obj)

    def delete_all(self, clazz, joins=None, filters=None):
        query = DBSession.query(clazz)
        if joins is not None:
            for j in joins:
                query = query.join(j)
        if filters is not None:
            for f in filters:
                query = query.filter(f)

        query.delete()


    def truncate(self, clazz):
        DBSession.query(clazz).delete()

    def refresh(self, obj):
        DBSession.refresh(obj)
        return obj

    def get_all(self, clazz):
        return DBSession.query(clazz).all()

    def find_by_id(self, clazz, value):
        return DBSession.query(clazz).filter_by(id=value).first()

    def find_by_name(self, clazz, value):
        return DBSession.query(clazz).filter_by(name=value).first()

    def filterby(self, clazz, joins=None, filters=None, orderby=None):
        query = DBSession.query(clazz)
        if joins is not None:
            for j in joins:
                query = query.join(j)
        if filters is not None:
            for f in filters:
                query = query.filter(f)
        if orderby is not None:
            for o in orderby:
                query = query.order_by(o)
        return query.all()


    def test(self):
        print 'DBHELPERRRRRRRRRRRRRRRRRRRR'



