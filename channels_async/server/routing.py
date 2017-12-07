# Create custom DJANGO_SETTINGS for this worker, and override default channel routing to here
#
# CHANNEL_LAYERS['default']["ROUTING"] = "channels_async.server.routing.channel_routing"

# from channels.routing import route
# route("async.request", "channels_async.handle_request"),

channel_routing = []
