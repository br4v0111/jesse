import os
import pickle
from time import time


class Cache:
    """

    """
    def __init__(self, path):
        self.path = path

        # make sure path exists
        os.makedirs(path, exist_ok=True)

        # if cache_database exists, load the dictionary
        if os.path.isfile(self.path + "cache_database.pickle"):
            with open(self.path + "cache_database.pickle", 'rb') as f:
                self.db = pickle.load(f)
        # if not, create a dict object. We'll create the file when using set_value()
        else:
            self.db = {}

    def set_value(self, key: str, data, expire_seconds=60 * 60):
        """

        :param key:
        :param data:
        :param expire_seconds:
        """
        # add record into the database
        expire_at = None if expire_seconds is None else time() + expire_seconds
        data_path = self.path + "{}.pickle".format(key)
        self.db[key] = {
            'expire_seconds': expire_seconds,
            'expire_at': expire_at,
            'path': data_path,
        }
        self._update_db()

        # store file
        with open(data_path, 'wb') as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

    def get_value(self, key: str):
        """

        :param key:
        :return:
        """
        try:
            item = self.db[key]
        except KeyError:
            return False

        # if expired, remove file, and database record
        if item['expire_at'] is not None and time() > item['expire_at']:
            os.remove(item['path'])
            del self.db[key]
            self._update_db()
            return False

        # renew cache expiration time
        if item['expire_at'] is not None:
            item['expire_at'] = time() + item['expire_seconds']
            self._update_db()

        with open(item['path'], 'rb') as f:
            return pickle.load(f)

    def _update_db(self):
        # store/update database
        with open(self.path + "cache_database.pickle", 'wb') as f:
            pickle.dump(self.db, f, protocol=pickle.HIGHEST_PROTOCOL)

    def flush(self):
        for key, item in self.db.items():
            os.remove(item['path'])
        self.db = {}


cache = Cache("storage/temp/")
