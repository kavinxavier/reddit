# The contents of this file are subject to the Common Public Attribution
# License Version 1.0. (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# http://code.reddit.com/LICENSE. The License is based on the Mozilla Public
# License Version 1.1, but Sections 14 and 15 have been added to cover use of
# software over a computer network and provide for limited attribution for the
# Original Developer. In addition, Exhibit A has been modified to be consistent
# with Exhibit B.
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for
# the specific language governing rights and limitations under the License.
#
# The Original Code is reddit.
#
# The Original Developer is the Initial Developer.  The Initial Developer of
# the Original Code is reddit Inc.
#
# All portions of the code written by reddit are Copyright (c) 2006-2013 reddit
# Inc. All Rights Reserved.
###############################################################################
"""Utilities for interfacing with the WebSocket server Sutro."""

import hashlib
import hmac
import json
import time
import urllib
import urlparse

from pylons import g

from r2.lib import amqp


_WEBSOCKET_EXCHANGE = "sutro"


def send_broadcast(namespace, message):
    """Broadcast an object to all WebSocket listeners in a namespace.

    The message will be encoded as a JSON object before being sent to the
    client.

    """
    amqp.add_item(routing_key=namespace, body=json.dumps(message),
                  exchange=_WEBSOCKET_EXCHANGE)


def make_url(namespace, max_age):
    """Return a signed URL for the client to use for websockets.

    The namespace determines which messages the client receives and max_age is
    the number of seconds the URL is valid for.

    """

    expires = str(int(time.time() + max_age))
    mac = hmac.new(g.secrets["websocket"], expires + namespace,
                   hashlib.sha1).hexdigest()

    query_string = urllib.urlencode({
        "h": mac,
        "e": expires,
    })

    return urlparse.urlunparse(("wss", g.websocket_host, namespace,
                               None, query_string, None))
