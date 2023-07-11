import os
import eventlet
from eventlet import wsgi
import bot

app = bot.create_app()

if __name__ == '__main__':
    eventlet.monkey_patch(all=True)
    port = int(os.environ.get('PORT', 3000))
    server = eventlet.listen(('0.0.0.0', port))
    wsgi.server(server, app)
