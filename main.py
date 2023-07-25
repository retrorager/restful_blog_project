import os
from datetime import date

from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)


file_path = os.path.abspath(os.getcwd())+'/posts.db'

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+file_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = StringField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


@app.route('/')
def get_all_posts():
    posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:index>")
def show_post(index):
    requested_post = None
    posts = db.session.query(BlogPost).all()
    for post in posts:
        if post.id == index:
            requested_post = post
    return render_template("post.html", post=requested_post)

@app.route("/new-post", methods=["GET", "POST"])
def new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            author=form.author.data,
            img_url=form.img_url.data,
            body=form.body.data,
            date=date.today().strftime("%B-%d-%Y")
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template("make-post.html", form=form, is_edit=False)

@app.route("/edit-post/<post_id>")
def edit_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=requested_post.title,
        subtitle=requested_post.subtitle,
        author=requested_post.author,
        img_url=requested_post.img_url,
        body=requested_post.body,
    )
    if edit_form.validate_on_submit():
        updated_post = BlogPost.query.get(post_id)
        updated_post.title = edit_form.title.data
        updated_post.subtitle = edit_form.subtitle.data
        updated_post.author = edit_form.author.data
        updated_post.img_url = edit_form.img_url.data
        updated_post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for('show_post', index=post_id))
    return render_template("make-post.html", form=edit_form, is_edit=True)

@app.route("/delete-post/<post_id>")
def delete_post(post_id):
    query_id = post_id
    requested_post = BlogPost.query.get(query_id)
    db.session.delete(requested_post)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)