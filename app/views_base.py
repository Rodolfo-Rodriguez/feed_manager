
from flask import render_template, redirect, request, Blueprint, session, url_for
import sys, os

from sqlalchemy import desc

reload(sys)
sys.setdefaultencoding('utf8')

base = Blueprint('base', __name__, template_folder='templates/base')

from .models import Bookmark
from . import db, CONFIG, db_manager, bookmark_manager
from .forms import BookmarkForm, ConfigForm


###########################################################################################
# Home
###########################################################################################

# ---> Home
@base.route('/', methods=['GET'])
def home():
    
    session['last_url'] = '/podcast/all'

    return redirect("/podcast/all")

###########################################################################################
# Admin
###########################################################################################

# ---> Admin
@base.route('/admin', methods=['GET'])
def admin():
    
    session['last_url'] = '/admin'

    return render_template('admin.html')

###########################################################################################
##  Server
###########################################################################################

# ---> DB Status
@base.route('/db/status', methods=['GET'])
def db_status():
    session['last_url'] = url_for('player.db_status')
    template_page = 'db_status.html'
    return render_template(template_page, db_manager=db_manager)

###########################################################################################
##  Playing
###########################################################################################

# ---> Bookmarks List
@base.route('/bookmark/list', methods=['GET'])
def list_bookmark():

    session['last_url'] = url_for('base.list_bookmark')

    template_page = 'bookmark_list.html'

    return render_template(template_page, bookmark_manager=bookmark_manager)


# ---> Bookmark Edit
@base.route('/bookmark/edit/<id>', methods=['GET', 'POST'])
def bookmark_edit(id):

    bookmark = Bookmark.query.filter_by(id=id).first()

    form = BookmarkForm()

    if form.validate_on_submit():

        bookmark.url = form.url.data
        bookmark.image_url = form.image_url.data
        bookmark.priority = form.priority.data

        db.session.commit()

        bookmark_manager.update_bookmark_list()

        redirect_page = url_for('base.list_bookmark')

        session['last_url'] = redirect_page

        return redirect(redirect_page)

    form.url.data = bookmark.url
    form.image_url.data = bookmark.image_url
    form.priority.data = bookmark.priority

    session['last_url'] = url_for('base.bookmark_edit',id=id)

    template_page = 'bookmark_edit.html'

    return render_template(template_page, form=form, bookmark_manager=bookmark_manager)

# ---> Bookmark Delete
@base.route('/bookmark/delete/<id>', methods=['GET'])
def bookmark_delete(id):
    bookmark = Bookmark.query.filter_by(id=id).first()

    db.session.delete(bookmark)
    db.session.commit()

    bookmark_list = Bookmark.query.order_by(Bookmark.priority).all()

    prio = 1
    for bookmark in bookmark_list:
        bookmark.priority = prio
        db.session.commit()
        prio = prio + 1

    bookmark_manager.update_bookmark_list()

    redirect_page = session['last_url']

    return redirect(redirect_page)

# ---> Bookmark Move Up
@base.route('/bookmark/move_up/<id>', methods=['GET'])
def bookmark_move_up(id):

    bookmark_list = Bookmark.query.order_by(Bookmark.priority).all()

    prio = 2

    for idx in range(1,len(bookmark_list)):

        if bookmark_list[idx].id == int(id):
            bookmark_list[idx].priority = prio - 1
            bookmark_list[idx-1].priority = prio            
        else:
            bookmark_list[idx].priority = prio
        
        prio = prio + 1
        db.session.commit()

    bookmark_manager.update_bookmark_list()

    redirect_page = session['last_url']

    return redirect(redirect_page)


###########################################################################################
# Config
###########################################################################################

# ---> Home
@base.route('/config', methods=['GET', 'POST'])
def config():

    form = ConfigForm()

    if form.validate_on_submit():

        redirect_page = url_for('base.home')

        session['last_url'] = redirect_page

        return redirect(redirect_page)

    session['last_url'] = url_for('base.config')

    template_page = 'config.html'

    return render_template(template_page, form=form, bookmark_manager=bookmark_manager)


