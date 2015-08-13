#coding=utf-8

import datetime
from .. import db
from ..models import Record


def record_sql(user, status, table, table_id, item, value):
    '''记录cmdb操作记录'''
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    record = Record(
        username=user,
        status=status,
        table=table,
        table_id=table_id,
        item=item,
        value=value,
        date=date,
    )
    db.session.add(record)
