import select
import eventlet

eventlet.monkey_patch(all=True)

from eventlet import wsgi
import os
import bot

app = bot.create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    server = eventlet.listen(('0.0.0.0', port))
    wsgi.server(server, app)
