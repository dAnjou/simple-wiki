from flask import Flask, render_template, abort, Markup, request, redirect, url_for

from markdown import markdown
from jinja2 import Template
from werkzeug.urls import url_quote_plus, url_unquote_plus

import os
from base64 import urlsafe_b64encode, urlsafe_b64decode

app = Flask(__name__)

@app.template_filter('markdown')
def md2html(s):
    return Markup(markdown(s))

@app.route('/')
def index():
    posts = []
    for filename in os.listdir('posts'):
        title = urlsafe_b64decode(filename)
        posts.append({'title': title, 'url': url_quote_plus(title)})
    return render_template('index.html', posts=posts)

@app.route('/<url>')
def post(url):
    try:
        title = url_unquote_plus(url)
        f = open('posts/' + urlsafe_b64encode(title))
    except:
        return redirect(url_for('admin_edit', url=url))
    else:
        body = f.read()
        f.close()
        return render_template('post.html', title=title, body=body, url=url)

@app.route('/new', defaults={'url': None})
@app.route('/<url>/edit')
def admin_edit(url):
    title = None
    body = ""
    if url:
        try:
            title = url_unquote_plus(url)
            f = open('posts/' + urlsafe_b64encode(title))
        except:
            pass
        else:
            title = url_unquote_plus(url)
            body = f.read()
            f.close()
    return render_template('admin_posts.html', title=title, body=body)

@app.route('/save', methods=['POST'])
def admin_save():
    title = request.form.get('title', None)
    if not title:
        return redirect(url_for('admin_edit'))
    f = open('posts/' + urlsafe_b64encode(title), 'w')
    f.write(request.form.get('body', ''))
    f.close()
    return redirect(url_for('post', url=url_quote_plus(title)))

if __name__ == '__main__':
    app.run(debug=True)