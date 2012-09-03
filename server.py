from flask import Flask, render_template, abort, Markup, request, redirect, url_for, flash, Response, stream_with_context
from flaskext.wtf import Form, TextField, TextAreaField, Required

from werkzeug import secure_filename
from markdown import markdown
from yaml import load, safe_dump
from jinja2 import Template

import os
from time import sleep
from datetime import datetime

app = Flask(__name__)

class PostForm(Form):
    title = TextField(validators=[Required()])
    body = TextAreaField(validators=[Required()])


def get_post_metadata_generator():
    for filename in os.listdir('posts'):
        sleep(0.5) # add a little more lag
        with open('posts/' + filename) as f:
            tmp = ''
            for line in f:
                if not line.strip():
                    break
                tmp += line
            metadata = load(tmp)
            #TODO: add creation and modification date
            #if not metadata.has_key('created'):
            #    metadata['created'] = datetime.fromtimestamp(os.path.getmtime(f.name)).strftime('%Y-%m-%d %H:%M:%S')
            metadata['filename'] = filename
            yield metadata

def get_post_metadata_list():
    metadates = []
    for filename in os.listdir('posts'):
        with open('posts/' + filename) as f:
            tmp = ''
            for line in f:
                if not line.strip():
                    break
                tmp += line
            metadata = load(tmp)
            #TODO: add creation and modification date
            #if not metadata.has_key('created'):
            #    metadata['created'] = datetime.fromtimestamp(os.path.getmtime(f.name)).strftime('%Y-%m-%d %H:%M:%S')
            metadata['filename'] = filename
            metadates.append(metadata)
    return metadates

def get_post_from_file(f):
    tmp = ''
    # read yaml stuff until blank line
    for line in f:
        if not line.strip():
            break
        tmp += line
    post = {
        "filename": os.path.basename(f.name),
        "body": "".join(list(f))
    }
    # load yaml stuff into dict
    post.update(load(tmp))
    return post

def save_post_to_file(f, post):
    body = post.pop('body')
    f.write(safe_dump(post, default_flow_style=False))
    f.write("\n")
    f.write(body)

@app.template_filter('markdown')
def md2html(s):
    return Markup(markdown(s))

#TODO: creation and modification date should be formatted for humans, e.g. "2 minutes ago"
#@app.template_filter()
#def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
#    return datetime.fromtimestamp(value).strftime(format)

def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    return t.generate(posts=get_post_metadata_generator())

@app.route('/')
def index():
    return Response(stream_with_context(stream_template('index.html', posts=get_post_metadata_generator())))

@app.route('/p/<filename>')
def post(filename):
    try:
        f = open('posts/' + filename)
    except:
        abort(404)
    else:
        post = get_post_from_file(f)
        f.close()
        return render_template('post.html', post=post)

@app.route('/admin/<filename>', methods=['GET', 'POST'])
def admin(filename):
    form = PostForm(csrf_enabled=False)
    if request.method == "GET":
        # if there is a file already, pre-fill the form
        try:
            f = open('posts/' + filename)
        except:
            form.title.data = ""
            form.body.data = ""
        else:
            post = get_post_from_file(f)
            form.title.data = post['title']
            form.body.data = post['body']
    if request.method == "POST" and form.validate_on_submit():
        filename = secure_filename(filename)
        # if there is a file already, load existing data;
        #  otherwise, create an empty dict
        try:
            f = open('posts/' + filename)
            post = get_post_from_file(f)
            post.pop('filename')
            f.close()
        except:
            post = {}
        post.update({
            "title": form.title.data,
            "body": form.body.data
        })
        with open('posts/' + filename, 'w') as f:
            save_post_to_file(f, post)
        return redirect(url_for('post', filename=filename))
    return render_template('admin_posts.html', form=form, filename=filename)

if __name__ == '__main__':
    app.run(debug=True)