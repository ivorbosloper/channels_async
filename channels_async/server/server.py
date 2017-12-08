#!/usr/bin/env python3
from __future__ import unicode_literals

import os
import sys
from wsgiref.util import is_hop_by_hop

import six
import traceback

import asyncio
import logging
from channels.channel import Channel
from channels.handler import AsgiHandler
from django.http import HttpResponse

from channels_async import ASYNC_CHANNEL, OPERATION_TYPES
from aiohttp import ClientSession


logger = logging.getLogger(__name__)
DISABLE_HEADERS = ('set-cookie', )


class ChannelsConsumer(object):
    def __init__(self):
        self.session = None
        self.loop = None

    async def request(self, url, **kwargs):
        async with self.session.get(url, **kwargs) as resp:
            content = await resp.read()
            response = HttpResponse(content, status=resp.status, content_type=resp.content_type)
            for k, v in six.iteritems(resp.headers):
                if not (k.lower() in DISABLE_HEADERS or is_hop_by_hop(k)):
                    response[k] = v
            return response

    async def start(self, channel_layer, channel_names):
        with ClientSession(auto_decompress=False) as session:
            self.session = session
            if isinstance(channel_names, str):
                channel_names = [channel_names]

            while True:
                channel, raw_message = channel_layer.receive_many(channel_names, block=False)
                if channel:
                    operation = raw_message.pop('operation')
                    if operation not in OPERATION_TYPES:
                        logger.error("Operation {} not supported".format(operation))
                        continue
                    reply_channel = raw_message.pop('reply_channel')
                    args = raw_message.pop('args', [])
                    logger.debug("Handle {} {} {}".format(operation, args, raw_message))
                    response = await getattr(self, operation.lower())(*args, **raw_message)
                    c = Channel(reply_channel, channel_layer=channel_layer)
                    for chunk in AsgiHandler.encode_response(response):
                        c.send(chunk)
                else:
                    await asyncio.sleep(0.1)

    def run(self, channel_layer, channel_names):
        self.loop = asyncio.get_event_loop()
        asyncio.ensure_future(self.start(channel_layer, channel_names))
        try:
            self.loop.run_forever()
        except Exception as e:
            traceback.print_exc()
        finally:
            self.loop.close()


def runserver(settings_module=None):
    if settings_module:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
    from channels.asgi import get_channel_layer
    channel_layer = get_channel_layer()
    ChannelsConsumer().run(channel_layer, ASYNC_CHANNEL)


if __name__ == '__main__':
    runserver(*sys.argv[1:])
