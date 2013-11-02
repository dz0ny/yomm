from urlparse import urlparse
from urlparse import parse_qs

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from yodl.tasks import transcode
from yodl.models import SongItem
from yodl.models import DBSession
from yodl.celery_utils import celery


def url_validate(url):
    """docstring for url_validate"""
    o = urlparse(url)
    try:
        query = parse_qs(o.query)
        if o.netloc.endswith("youtube.com")\
                and query.keys() == [u'v']:
            return url
    except:
        pass


@view_config(route_name='home', renderer='templates/index.jinja2')
def main_view(request):
    if request.POST:
        url = request.params["url"].strip()
        # check if id and file all ready exists
        if url_validate(url):
            r = transcode.delay(url)
            request.session["error"] = False
        else:
            request.session["error"] = True
        return HTTPFound(request.route_url('home'))

    i = celery.control.inspect()
    queue = i.active()

    songs = DBSession.query(SongItem).all()
    return {'songs': songs, 'queue': queue}
