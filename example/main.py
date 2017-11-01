from sockjs_flask.server import Server
import flask
import sockjs_flask


app = flask.Flask(__name__,template_folder='./')
sockjs_flask.add_endpoint(app, lambda msg, session: print(msg, session))


@app.route('/')
def sockjs_test():
    response = flask.make_response(flask.render_template('test.html'))
    return response


if __name__ == '__main__':
    server_host = '127.0.0.1'
    server_port = 5001
    print('Serving at host {}:{}...\n'.format(server_host, server_port))
    server = Server((server_host, server_port), app.wsgi_app)
    server.serve_forever()