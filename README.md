# Aysnchronous Task Runner for Django Channels

Django Channels extends Django in a great way, but it doesn't directly support running code 
concurrently / asynchonous.

Channels Async Server is an AsyncIO-based eventloop which consumes Django Channels messages,
does some processing and sends results to a Channels reply-channel. You can easily send 
messages to the server with the Channels Client. The main difference between Channels 
Async Server and normal Channels Worker processes is that this process runs in an asyncio 
loop. Therefore, as long as you use non-blocking asyncio operations (or you spawn threads),
it can handle many tasks concurrently. Not all of your application needs to be asyncio-capable
(Django isn't by default), only the tasks handled by this worker.

The main use case is proxying http-requests, or running external processes and waiting on the 
result. We want to avoid blocking our (memory-expensive) Django http_workers, only waiting 
for an external service to reply and sending this to our client. This worker is not meant 
for CPU or IO-bound tasks, but avoids blocking expensive Django workers on slow IO tasks.

Channels Async Server is run as a seperate worker process. The main Django workers can use the
Channels Async Client to offload tasks to the server and supply a reply-channel for the result. 
The Client puts an operation in the Channels queue for the server to process.

The client code is python2/python3 compatible and the server currently relies on python 3.5+
for asyncio operations (feel free to backport this to python2, possibly with trollius).

# Install

## Client

In your Django project environment do:

```
pip install channels_async
```

## Server

Make sure you run python>=3.5 . The description below assumes you have a python2-based Django
project and you need to setup a python3 virtualenv for the asyncio server. This might not be
neccesary if your Django project runs in python3 by itself.

```
# Setup new virtualenv for the server part

pip3 install virtualenv
python3 `which virtualenv` —python=`which python3` channels_async

pip install Django==1.11.* channels==1.1.5
pip install psycopg2 asgi_redis==1.4.2  # you might need this based on your settings
PYTHONPATH=.:$PYTHONPATH python3 -m channels_async.server.server myproject.settings
```

The server relies on your project's django settings to get the relevant Channels configuration. 
You don't necissarily need the complete django settings of you base project (e.g. if your project
isn't completely python3 compatible, or you don't want to load all the external modules of your
base project). You can make a small derived settings file just for this purpose, see 
the file settings.example.

# Usage

You can use the client to offload work to the server.

In urls.py add:

```
    url("get_some_url$", "myproject.view.get_some_url",),
```

In `myproject.view` add:

```
def get_some_url(request):
    from channels_async.client.client import client
    # do stuff with request, like access request.user etc
    user = request.user.username
    return client.request(request, url='https://github.com/{}'.format(user))
```

## Low level usage with Channels Messages

Tapping into channels routing is a more low-level way to invoke channels async. You can 
route a normal http.request (with a specific path) into a custom consumer, and do all the 
handling yourself. You don't get a request object enriched by your middleware, only the
raw channels message.

In your routes.py add:

```
    route("http.request", "myproject.view.get_some_url", path="^/get_some_url$"),
```

In `myproject.view` add:

```
def get_some_url(messsage):
    from channels_async.client.client import client
    # do stuff with message
    return client.request(message, url='https://github.com/')
```

# TODO

- Port server to python2 with trollius
- Add other type of operations, like running a python method or a unix commandline script
  and sending the response to the client
- Test the client on python3
