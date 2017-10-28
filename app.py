# -*- coding: utf-8 -*-
import flask
from flask import request
import mwoauth
import os
import yaml
import img2pdf
import mwclient


app = flask.Flask(__name__)


# Load configuration from YAML file
__dir__ = os.path.dirname(__file__)
app.config.update(
    yaml.safe_load(open(os.path.join(__dir__, 'config.yaml'))))


@app.route('/', methods=['GET', 'POST'])
def index():
    username = flask.session.get('username', None)
    pdf_title = None
    commons_file = None
    if request.method == 'POST':
        if username:
            site = mwclient.Site(
                'commons.wikimedia.org',
                consumer_token=app.config['CONSUMER_KEY'],
                consumer_secret=app.config['CONSUMER_SECRET'],
                access_token=flask.session['access_token']['key'],
                access_secret=flask.session['access_token']['secret'])
        else:
            site = mwclient.Site('commons.wikimedia.org')
        cat = mwclient.listing.Category(site, request.form['category'])
        os.chdir(os.environ['HOME'] + '/category')
        if not os.path.isdir(cat.page_title):
            os.mkdir(cat.page_title)
        os.chdir(cat.page_title)
        for page in cat:
            with open(page.page_title, 'wb') as f:
                page.download(f)
        pages_list = [page for page in os.listdir() if page[-4:] in ['.jpg',
                                                                     '.tif']]
        pages_list.sort()
        pdf_title = cat.page_title + '.pdf'
        static_path = os.environ['HOME'] + '/www/python/static/'
        with open(static_path + pdf_title, 'wb') as pdf_file:
            pdf_file.write(img2pdf.convert(pages_list))
        if username:
            with open(static_path + pdf_title, 'rb') as pdf_file:
                try:
                    result = site.upload(
                        file=pdf_file, filename=request.form.get('filename'),
                        description=request.form.get('description'))
                    if result['result'] == 'Success':
                        commons_file = result['imageinfo']['descriptionurl']
                except Exception as e:
                    print(e)
    return flask.render_template('index.html', username=username,
                                 pdf=pdf_title, commons=commons_file)


@app.route('/login')
def login():
    """Initiate an OAuth login.

    Call the MediaWiki server to get request secrets and then redirect the
    user to the MediaWiki server to sign the request.
    """
    consumer_token = mwoauth.ConsumerToken(
        app.config['CONSUMER_KEY'], app.config['CONSUMER_SECRET'])
    try:
        redirect, request_token = mwoauth.initiate(
            app.config['OAUTH_MWURI'], consumer_token)
    except Exception:
        app.logger.exception('mwoauth.initiate failed')
        return flask.redirect(flask.url_for('index'))
    else:
        flask.session['request_token'] = dict(zip(
            request_token._fields, request_token))
        return flask.redirect(redirect)


@app.route('/oauth-callback')
def oauth_callback():
    """OAuth handshake callback."""
    if 'request_token' not in flask.session:
        flask.flash(u'OAuth callback failed. Are cookies disabled?')
        return flask.redirect(flask.url_for('index'))

    consumer_token = mwoauth.ConsumerToken(
        app.config['CONSUMER_KEY'], app.config['CONSUMER_SECRET'])

    try:
        access_token = mwoauth.complete(
            app.config['OAUTH_MWURI'],
            consumer_token,
            mwoauth.RequestToken(**flask.session['request_token']),
            flask.request.query_string)

        identity = mwoauth.identify(
            app.config['OAUTH_MWURI'], consumer_token, access_token)
    except Exception:
        app.logger.exception('OAuth authentication failed')

    else:
        flask.session['access_token'] = dict(zip(
            access_token._fields, access_token))
        flask.session['username'] = identity['username']

    return flask.redirect(flask.url_for('index'))


@app.route('/logout')
def logout():
    """Log the user out by clearing their session."""
    flask.session.clear()
    return flask.redirect(flask.url_for('index'))
