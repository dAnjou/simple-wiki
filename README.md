# simple-wiki

Okay, this is so damn simple. Everything depends on the title of a post (or
page or whatever you want to call it). I use `urlsafe_b64(en|de)code` and
Werkzeug's `url_(un)quote_plus` to convert a title into a valid filename and
URL ... and back! That means, I totally don't care what crap the title contains
because I always get a URL and a file name, no matter what. And that's the
whole trick. Unbelievable, isn't it?

## Usage

It's a Flask project. Look at the code and figure it out by yourself. Here are the required packages:

    Flask==0.8
    Markdown==2.1.1
