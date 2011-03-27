from pymongo import DESCENDING
from pymongo.objectid import ObjectId


def _assign(obj, name, parent):
    obj.__name__ = name
    obj.__parent__ = parent
    return obj

class Root(object):
    __name__ = None
    __parent__ = None

    def __init__(self, request):
        self.collection = request.db.post

    def __getitem__(self, name):
        post = Post(self.collection.find_one(dict(_id=ObjectId(name))))
        return _assign(post, name, self)

    def __len__(self):
        return self.collection.count()

    def __iter__(self):
        return ( _assign(Post(x), str(x['_id']), self) for x in self.collection.find().sort('updated', DESCENDING) )


class Post(dict):
    def __init__(self, a_dict):
        super(Post, self).__init__(self)
        self.update(a_dict)
        self.__name__ = None
        self.__parent__ = None
        
