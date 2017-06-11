class MongoManager(object):
    def __init__(self, db_name, uri=None):
        self.uri = uri
        self.__db = None
        self.db_name = db_name

    def db(self, **kwargs):
        try:
            self.__db = self.__db or self._conn()[self.db_name]
            return 1, self.__db
        except Exception as e:
            self.__db = None
            return 0, str(e)

    def col(self, name, **kwargs):
        try:
            st, db = self.db()
            if not st:
                print(db)
                return 0, db
            return st, db[name]
        except Exception as e:
            return 0, str(e)

    def _conn(self):
        from motor import motor_asyncio
        return motor_asyncio.AsyncIOMotorClient(self.uri)


def init_mongodb():
    from utils.app import Application
    app = Application.current()
    app.mongo = MongoManager(app.config.get("MONGODB_DB"), uri=app.config.get("MONGODB_URI"))


async def _main():
    m = MongoManager("stocks", uri="mongodb://localhost:27017")
    st, c = m.col("hi_low")
    if not st:
        print(c)
    else:
        d = await c.find_one()
        print(d)


if __name__ == '__main__':
    import asyncio

    asyncio.get_event_loop().run_until_complete(_main())
