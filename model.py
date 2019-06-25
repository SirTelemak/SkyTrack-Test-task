from peewee import *

db = SqliteDatabase('SkyTrack-test-task.db')


class Pages(Model):
    class Meta:
        database = db
        db_table = 'pages'
    url_id = IntegerField(primary_key=True)
    url = CharField()
    request_depth = IntegerField()

    @classmethod
    def add_pages(cls, urls, depth):
        data_source = [{'url': url, 'request_depth': depth} for url in urls
                       if not cls.select().where(cls.url == url).exists()]
        with db.atomic():
            for idx in range(0, len(data_source), 100):
                cls.insert_many(data_source[idx:idx + 100]).execute()


class Links(Model):
    class Meta:
        database = db
        db_table = 'links'
    from_page_id = ForeignKeyField(Pages, backref='from_page')
    link_id = ForeignKeyField(Pages, backref='link')

    @classmethod
    def add_link(cls, parent_url, urls):
        parent_id = Pages.get(Pages.url == parent_url)
        child_ids = [Pages.get(Pages.url == url) for url in urls]
        data_source = [{'from_page_id': parent_id, 'link_id': child_id} for child_id in child_ids]
        with db.atomic():
            for idx in range(0, len(data_source), 100):
                cls.insert_many(data_source[idx:idx + 100]).execute()


def create_tables():
    with db:
        db.create_tables([Pages, Links])
