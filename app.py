import datetime
import flask
import redis


app = flask.Flask(__name__)
app.secret_key = 'ChangeThisAfter'
red = redis.StrictRedis()


def event_stream(channel):
    pubsub = red.pubsub()
    pubsub.subscribe(channel)
    # TODO: handle client disconnection.
    for message in pubsub.listen():
        print(message)
        yield 'data: %s\n\n' % message['data']


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        flask.session['user'] = flask.request.form['user']
        flask.session['channel'] = flask.request.form['channel']
        return flask.redirect('/')
    return """<form action="" method="post">user: <input name="user"> <br>
    channel: <input name="channel"> <br>
<input type="submit" value="Submit"> </form> """


@app.route('/post', methods=['POST'])
def post():
    message = flask.request.form['message']
    channel = flask.session['channel']
    user = flask.session.get('user', 'anonymous')
    now = datetime.datetime.now().replace(microsecond=0).time()
    red.publish(channel, u'[%s] %s: %s' % (now.isoformat(), user, message))
    return flask.Response(status=204)


@app.route('/stream')
def stream():
    return flask.Response(event_stream(flask.session['channel']),
                          mimetype="text/event-stream")


@app.route('/')
def home():
    if 'user' not in flask.session:
        return flask.redirect('/login')
    return flask.render_template('index.html', username=flask.session['user'])

if __name__ == '__main__':
    app.debug = False
    app.run(host='192.168.0.105', threaded=True, port="5000")
