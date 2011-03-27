from pyramid.config import Configurator

import pymongo

from pyramid.events import subscriber
from pyramid.events import NewRequest

from troll.resources import Root


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=Root,
                          settings=settings)

    config.add_renderer(".html", "pyramid.mako_templating.renderer_factory")
    config.add_static_view('static', 'troll:static')
    config.registry.mongo_con = pymongo.Connection(settings['db_uri'])
    config.scan()
    
    return config.make_wsgi_app()


@subscriber(NewRequest)
def add_mongo(event):
    settings = event.request.registry.settings
    event.request.db = event.request.registry.mongo_con[settings['db_name']]
    
