from datetime import datetime
from pymongo import DESCENDING
from pymongo.objectid import ObjectId

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from wtforms import Form, TextField, TextAreaField, validators
from wtfrecaptcha.fields import RecaptchaField

from troll import resources

PUBLIC_KEY='YOUR_PUBLIC_KEY'
PRIVATE_KEY='YOUR_PRIVATE_KEY'


class TrollForm(Form):
    name = TextField(u'name', default='anonymous')
    content = TextAreaField(u'content', [validators.required])
    captcha = RecaptchaField(public_key=PUBLIC_KEY, private_key=PRIVATE_KEY)


def _post(collection, author, content):
    p = dict(author=author,
             content=content,
             comments=[],
             updated=datetime.utcnow(),
             time=datetime.utcnow())
    collection.insert(p)
    #remove unpopular post if >  10
    if collection.find().count() > 10:
        collection.remove({'_id': [x for x in collection.find().sort("updated", DESCENDING)][-1]['_id']})


def _comment(collection, post_id, author, comment):
    post = collection.find_one(dict(_id=post_id))
    time = datetime.utcnow()
    post['comments'].append(dict(author=author,
                                 comment=comment,
                                 time=time))
    post.update(dict(updated=time))
    collection.save(post)



def _add(context, author, content):
    if context.__parent__ is None:
        _post(context.collection,
              author,
              content)
    else:
        _comment(context.__parent__.collection,
                 context['_id'],
                 author,
                 content)


@view_config(name='add', request_method='POST', context=resources.Post)
@view_config(name='add', request_method='POST', context=resources.Root)
def add(context, request):
    author = request.params['name']
    content = request.params['content']
    _add(context, author, content)
    return HTTPFound(location=request.resource_url(context))


@view_config(renderer='single.html', context=resources.Post)
@view_config(renderer='index.html', context=resources.Root)
def view(context, request):
    form = TrollForm()
    return {'p': context, 'form': form}

