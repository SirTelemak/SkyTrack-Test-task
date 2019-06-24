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
    def add_page(cls, url, depth):
        q = cls.select().where(cls.url == url)
        if not q.exists():
            cls.create(url=url, request_depth=depth)
            return True


class Links(Model):
    class Meta:
        database = db
        db_table = 'links'
    from_page_id = ForeignKeyField(Pages, backref='from_page')
    link_id = ForeignKeyField(Pages, backref='link')

    @classmethod
    def add_link(cls, parent_url, child_url):
        parent_id = Pages.get(Pages.url == parent_url)
        child_id = Pages.get(Pages.url == child_url)
        cls.create(from_page_id=parent_id, link_id=child_id)


db.create_tables([Pages, Links])
# Pages.add_page('a', 1)
# Pages.add_page('b', 2)
# Pages.add_page('c', 2)
# Pages.add_page('d', 3)
# Pages.add_page('e', 3)
# Pages.add_page('f', 3)
#
# Links.add_link('a', 'b')
# Links.add_link('a', 'c')
# Links.add_link('b', 'd')
# Links.add_link('b', 'f')
# Links.add_link('c', 'e')
