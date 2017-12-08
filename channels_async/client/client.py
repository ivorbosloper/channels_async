from __future__ import unicode_literals

from django.http import HttpResponse
from django.conf import settings
from channels.handler import AsgiRequest, HttpResponseLater
from channels.message import Message
from channels import Channel
import requests
import six

from channels_async import ASYNC_CHANNEL


class SyncClient(object):
    def request(self, request, url, **kwargs):
        assert isinstance(request, (AsgiRequest, Message)), "Use AsgiRequest or Message"
        resp = requests.get(url, **kwargs)
        return HttpResponse(resp.content, content_type=resp.headers['content-type'])


class AsyncClient(object):
    def do_operation(self, operation, reply_channel, **kwargs):
        op = {'operation': operation, 'reply_channel': reply_channel}
        op.update({six.text_type(k): six.text_type(v) for k, v in six.iteritems(kwargs)})
        Channel(ASYNC_CHANNEL).send(op)
        return HttpResponseLater()

    def request(self, request, url, **kwargs):
        message = request.message if isinstance(request, AsgiRequest) else request
        return self.do_operation('REQUEST', message['reply_channel'], url=url, **kwargs)


_sync_client = SyncClient()
_async_client = AsyncClient()
client = _async_client if getattr(settings, 'CHANNELS_ASYNC', True) else _sync_client
