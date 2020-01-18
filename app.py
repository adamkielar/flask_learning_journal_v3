from flask import (Flask, g, render_template, flash, redirect, url_for,
                   abort, Response, request)
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)
from flask_wtf.csrf import CSRFProtect
from slugify import slugify

import forms
import models

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'


app = Flask(__name__)
# csrf need to submit two forms on one page
csrf = CSRFProtect(app)
app.secret_key = 'jgeworguperougp394up93t8ygoi3u4qhcf384yt3pqfc4p3o9ut[w'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    try:
        g.user = models.User.get(models.User.id == user_id)
        return g.user
    except models.DoesNotExist:
        g.user = None
        return g.user


@app.before_request
def _db_connect():
    models.database.connect()


@app.teardown_request
def _db_close(response):
    if not models.database.is_closed():
        models.database.close()
    return response


@app.route('/register', methods=('GET', 'POST'))
def register():
    """View for user to register"""
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("You registered successfully", "success")
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    """View for user to log in"""
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email and password doesn't match", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You've been logged in", "success")
                return redirect(url_for('index'))
            else:
                flash("Your email and password doesn't match", "error")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    """View for user to logout"""
    logout_user()
    flash("You've been logged out.", "success")
    return redirect(url_for('index'))


@app.route('/')
@app.route('/entries')
def index():
    """View of journal homepage"""
    entries = models.Entry.select()
    entries_tags = models.Entry.select().join(models.Tag)
    return render_template('index.html', entries=entries, entries_tags=entries_tags)


@app.route('/entries/new', methods=('GET', 'POST'))
@login_required
def new_entry():
    """View for user to add entry with or without tag"""
    form = forms.TagEntryForm()
    if "save-entry" in request.form and form.entry_form.validate(form):
        models.Entry.create_entry(
            user=g.user.id,
            title=form.entry_form.title.data,
            slug=slugify(form.entry_form.title.data),
            entry_date=form.entry_form.entry_date.data,
            time_spent=form.entry_form.time_spent.data,
            what_you_learned=form.entry_form.what_you_learned.data,
            to_remember=form.entry_form.to_remember.data
        )
        models.database.close()
        flash('Entry saved !', 'success')
        return redirect(url_for('index'))
    elif "save-entry-tag" in request.form and form.validate():
        models.Entry.create_entry(
            user=g.user.id,
            title=form.entry_form.title.data,
            slug=slugify(form.entry_form.title.data),
            entry_date=form.entry_form.entry_date.data,
            time_spent=form.entry_form.time_spent.data,
            what_you_learned=form.entry_form.what_you_learned.data,
            to_remember=form.entry_form.to_remember.data
        )
        entry_id = models.Entry.select(models.Entry.id).order_by(models.Entry.id.desc()).limit(1).get()
        models.Tag.create_tag(entry_tag=entry_id, tag=form.tag_form.data)
        flash('Entry and Tag saved !', 'success')
        return redirect(url_for('index'))
    return render_template('new.html', form=form)


@app.route('/entries/<slug>/edit', methods=('GET', 'POST'))
@login_required
def edit_entry(slug):
    """View for user to edit entry"""
    if slug:
        entry = models.Entry.select().where(models.Entry.slug == slug).get()
        form = forms.EntryForm(obj=entry)

    if form.validate_on_submit():
        models.Entry.update(
            user=g.user.id,
            title=form.title.data,
            entry_date=form.entry_date.data,
            time_spent=form.time_spent.data,
            what_you_learned=form.what_you_learned.data,
            to_remember=form.to_remember.data,
        ).where(models.Entry.slug == slug).execute()
        flash('Entry updated !', 'success')
        return redirect(url_for('index'))
    return render_template('edit.html', form=form, entry=entry)


@app.route('/entries/<slug>/delete', methods=('GET', 'POST'))
@login_required
def delete_entry(slug):
    """View for user to delete entry"""
    if slug:
        entry = models.Entry.select().where(models.Entry.slug == slug).get()
        form = forms.EntryForm(obj=entry)

    if form.validate_on_submit():
        models.Entry.delete().where(models.Entry.slug == slug).execute()
        flash('Entry deleted !', 'success')
        return redirect(url_for('index'))
    return render_template('delete.html', form=form)


@app.route('/entries/<slug>')
def details(slug):
    """Detail view fo entry"""
    entries = models.Entry.select().filter(slug=slug)
    entry_id = models.Entry.select(models.Entry.id).where(models.Entry.slug == slug).get()
    tags = models.Tag.select().join(models.Entry).where(models.Tag.entry_tag == entry_id).order_by(models.Tag.tag)
    if not entries:
        abort(404)
    else:
        return render_template('detail.html', entries=entries, tags=tags)


@app.route('/tag/<tag>')
def tag(tag):
    """View of all entries with specific tag"""
    tags = models.Tag.select().filter(tag=tag).limit(1)
    entries = models.Entry.select().join(models.Tag, on=(models.Entry.id == models.Tag.entry_tag)).where(
        models.Tag.tag == tag)
    if not entries:
        abort(404)
    else:
        return render_template('tag.html', tags=tags, entries=entries)


@app.errorhandler(404)
def not_found(error):
    return Response('<h3>Not found</h3>'), 404


if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username='adamkielar',
            email='adam@test.pl',
            password='adam'
        )
    except ValueError:
        pass
    app.run(debug=DEBUG, host=HOST, port=PORT)