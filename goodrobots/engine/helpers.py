from datetime import datetime
import openai
from yake import KeywordExtractor
from functools import wraps
from flask_paginate import Pagination, get_page_parameter
from flask import session, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
from flask import request


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session['logged_in'] == True:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('auth.signin'))
    return wrap


def save_image(file, base="goodrobots/static/assets/cdn/images", slug=None):
    title, ext = file.filename.split(".")
    slug = slug if slug else title.lower().replace(" ", "-")
    filename = f"{slug}.{ext}"
    filename = secure_filename(filename)

    filename = os.path.join(base, filename)
    file.save(filename)
    return filename

class Paginate(object):
    def __init__(self, posts, perpage=6):
        self.posts = posts
        self.posts_lists = self._list_posts()
        self.per_page = perpage
        self.items = self.do_pagination()
        '''posts is a return from [MOngodb][collection].find()'''

    def _list_posts(self):
        return [i for i in self.posts]

    def paginate_posts(self):
        return self.posts_lists[self.offset: self.offset + self.per_page]

    def do_pagination(self):
        self.page = request.args.get(get_page_parameter(), type=int, default=1)
        self.offset = (self.page * self.per_page) - self.per_page
        pagination = Pagination(page=self.page,
                                per_page=self.per_page,
                                total=len(self.posts_lists),
                                css_framework='bootstrap4')

        paginated_posts = self.paginate_posts()
        return {"pagination": pagination, "page": self.page, "paginated_posts": paginated_posts, "per_page": 6}

    def _pagination(self):
        return self.items['pagination']

    def _page(self):
        return self.items['page']

    def _pg_posts(self):
        return self.items['paginated_posts']

    def _perpage(self):
        return self.items['per_page']

class NLTKGPT():
    def __init__(self, content):
        self.content = content[0:4077]

    def _init_(self):
        openai.api_key = "OPEN-API-KEY"

    def _ChatGPT(self, prompt):
        res = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.7,
            max_tokens=350,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        return res['choices'][0]['text']

    def _extract_keywords(self, top=2, n=3):
        kwe = KeywordExtractor(lan='en', n=n, dedupLim=0.9,
                                    top=top, features=None)
        keywords = kwe.extract_keywords(self.content)
        keywords = [i[0].lower() for i in keywords]
        return keywords

    def _extract_tags(self):
        keywords = [i[0].lower() for i in self.content]
        return 0

    def _bullets_article(self):
        prompt = f"Strip all HTML Tags from the following text and Summarise the text into 5 bullet points. End each bullet point with a #: '{self.content}'"
        res = self._ChatGPT(prompt)
        return res

    def _summarize_article(self):
        prompt = f"Strip all HTML Tags from the following text and Summarise the resulting text into 100 words: '{self.content}'"
        res = self._ChatGPT(prompt)
        return res

    def run(self):
        keywords = self._extract_keywords()
        summary = self._summarize_article()
        bullets = self._bullets_article()
        tags = self._extract_tags()
        return {"keywords":keywords, "summary":summary, "bullets":bullets, "tags":tags}
