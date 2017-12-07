#!/usr/bin/env bash

PYTHONPATH=.:$PYTHONPATH python -m channels_async.server.server myproject.settings.async_settings
