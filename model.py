from peewee import *

db = SqliteDatabase('SkyTrack-test-task.db')


class Pages(Model):
    class Meta:
        database = db
        db_table = 'pages'
    url_id = IntegerField(primary_key=True)
    url = CharField()
    request_depth = IntegerField()


class Links(Model):
    class Meta:
        database = db
        db_table = 'links'
    from_page_id = ForeignKeyField(Pages, backref='from_page')
    link_id = ForeignKeyField(Pages, backref='link')
