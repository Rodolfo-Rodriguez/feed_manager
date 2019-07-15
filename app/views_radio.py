
from flask import render_template, redirect, request, Blueprint, session, url_for
import sys, os, time

from sqlalchemy import desc

reload(sys)
sys.setdefaultencoding('utf8')

radio = Blueprint('radio', __name__, template_folder='templates/radio')

from . import db, CONFIG, bookmark_manager
from .models import Radios, Program, Podcast, Radio_Link, Bookmark
from .forms import RadioForm, ImageForm, ProgramForm, LinkForm, RadioSearchForm, PresetForm

from program_info import ProgramsInfo
from podcast import PodcastInfo


###########################################################################################
## List, Grid
###########################################################################################

# ---> Radios List
@radio.route('/radio/list', methods=['GET'])
def radio_list():

    radio_list = Radios.query.all()

    session['last_url'] = url_for('radio.radio_list')

    template_page = 'radio_list.html'

    return render_template(template_page, bookmark_manager=bookmark_manager)

# ---> All Radios
@radio.route('/radio/all', methods=['GET'])
def radio_all():
    radio_list = Radios.query.order_by(desc(Radios.stars)).order_by(desc(Radios.num_plays)).all()

    session['last_url'] = url_for('radio.radio_all')

    template_page = 'radio_grid.html'

    return render_template(template_page, radio_list=radio_list, title='All Radios', bookmark_manager=bookmark_manager)

# ---> Favorite Radios
@radio.route('/radio/favorite', methods=['GET'])
def radio_favorite():
    radio_list = Radios.query.filter(Radios.fav==True).order_by(desc(Radios.stars)).order_by(desc(Radios.num_plays)).all()

    session['last_url'] = url_for('radio.radio_all')

    template_page = 'radio_grid.html'

    return render_template(template_page,radio_list=radio_list,title='Favorite Radios', bookmark_manager=bookmark_manager)

# ---> Radio Styles
@radio.route('/radio/styles', methods=['GET'])
def radio_styles():

    radio_list = db.session.query(Radios.style).distinct()
    radio_styles = [ radio.style for radio in radio_list if radio.style != '']
    radio_styles.sort()

    session['last_url'] = url_for('radio.radio_styles')

    template_page = 'radio_styles.html'

    return render_template(template_page, radio_styles=radio_styles, bookmark_manager=bookmark_manager)

# ---> Radio Style
@radio.route('/radio/style/<style>', methods=['GET'])
def radio_style(style):

    radio_list = Radios.query.filter(Radios.style==style).order_by(desc(Radios.stars)).order_by(desc(Radios.num_plays)).all()

    session['last_url'] = url_for('radio.radio_style', style=style)

    template_page = 'radio_grid.html'

    return render_template(template_page, radio_list=radio_list, title=style, bookmark_manager=bookmark_manager)

# ---> Radio Countries
@radio.route('/radio/countries', methods=['GET'])
def radio_countries():

    radio_list = db.session.query(Radios.country).distinct()
    radio_countries = [ radio.country for radio in radio_list if radio.country != '' ]
    radio_countries.sort()

    session['last_url'] = url_for('radio.radio_countries')

    template_page = 'radio_countries.html'

    return render_template(template_page, radio_countries=radio_countries, bookmark_manager=bookmark_manager)

# ---> Radio Country
@radio.route('/radio/country/<country>', methods=['GET'])
def radio_country(country):

    radio_list = Radios.query.filter(Radios.country==country).order_by(desc(Radios.stars)).order_by(desc(Radios.num_plays)).all()

    session['last_url'] = url_for('radio.radio_country', country=country)

    template_page = 'radio_grid.html'

    return render_template(template_page, radio_list=radio_list, title=country, bookmark_manager=bookmark_manager)


# ---> Radio Grid
@radio.route('/radio/grid', methods=['GET'])
def radio_grid():
    
    radio_list = Radios.query.filter(Radios.preset > 0).order_by(Radios.preset).all()

    session['last_url'] = url_for('radio.radio_grid')

    template_page = 'radio_grid_flat.html'

    return render_template(template_page, radio_list=radio_list, title='Presets', bookmark_manager=bookmark_manager)


# ---> Radio Presets Grid
@radio.route('/radio/grid/presets', methods=['GET'])
def radio_grid_presets():

    preset_list = Preset.query.all()

    session['last_url'] = url_for('radio.radio_grid_presets')

    template_page = 'radio_grid_presets.html'

    return render_template(template_page, preset_list=preset_list, bookmark_manager=bookmark_manager)

###########################################################################################
## Show, Play
###########################################################################################

# ----> Set Week Day
@radio.route('/radio/set_wday/<id>/<wday>', methods=['GET'])
def radio_set_wday(id,wday):
    
    session['list_week_day'] = int(wday)

    redirect_page = url_for('radio.radio_show',id=id)

    session['last_url'] = redirect_page

    return redirect(redirect_page)


# ----> Radio Show
@radio.route('/radio_show/<id>', methods=['GET'])
def radio_show(id):

    radio = Radios.query.filter_by(id=id).first()

    programs_info = ProgramsInfo(radio)

    if 'list_week_day' in session:
        programs_info.set_list_week_day(session['list_week_day'])

    session['last_url'] = url_for('radio.radio_show',id=id)

    template_page = 'radio_show.html'

    return render_template(template_page,radio=radio, programs_info=programs_info, social_sites=CONFIG.SOCIAL_SITES, bookmark_manager=bookmark_manager) 

###########################################################################################
## Radio Add, Edit, Delete
###########################################################################################

# ---> Radio Add
@radio.route('/radio/add', methods=['GET', 'POST'])
def radio_add():

    form = RadioForm()

    if form.validate_on_submit():

        name = form.name.data
        image_file = form.image_file.data
        url = form.url.data
        country = form.country.data
        style = form.style.data

        num_plays = 0
        stars = 1
        fav = False
        description = ''

        image = name + '.png'

        image_file.save(os.path.join(CONFIG.PROJECT_ROOT_DIR, CONFIG.PROJECT_RADIOS_IMG_DIR, image))

        radio = Radios(name=name,
                    url=url,
                    image=image,
                    country=country,
                    style=style,
                    num_plays=num_plays,
                    stars=stars,
                    description=description,
                    fav=fav)

        db.session.add(radio)
        db.session.commit()

        redirect_page = url_for('radio.radio_show',id=radio.id)

        session['last_url'] = redirect_page

        return redirect(redirect_page)

    session['last_url'] = url_for('radio.radio_add')

    template_page = 'radio_add.html'

    return render_template(template_page, form=form, bookmark_manager=bookmark_manager)


# ---> Radio Edit
@radio.route('/radio/edit/<id>', methods=['GET', 'POST'])
def radio_edit(id):
    
    radio = Radios.query.filter_by(id=id).first()

    form = RadioForm()

    if form.validate_on_submit():

        radio.name = form.name.data
        radio.url = form.url.data
        radio.image = form.image.data
        radio.description = form.description.data
        radio.country = form.country.data
        radio.style = form.style.data

        db.session.commit()

        redirect_page = url_for('radio.radio_show',client='web',id=id)

        session['last_url'] = redirect_page

        return redirect(redirect_page)

    form.name.data = radio.name
    form.url.data = radio.url
    form.image.data = radio.image 
    form.description.data = radio.description
    form.country.data = radio.country
    form.style.data = radio.style

    session['last_url'] = url_for('radio.radio_edit', id=id)

    template_page = 'radio_edit.html'

    return render_template(template_page, form=form, bookmark_manager=bookmark_manager)


# ---> Radio Delete
@radio.route('/radio/delete/<id>', methods=['GET'])
def radio_delete(id):
    radio = Radios.query.filter_by(id=id).first()
    
    radio_links = Radio_Link.query.filter_by(radio_id=id).all()

    for link in radio_links:
        db.session.delete(link)

    db.session.delete(radio)

    db.session.commit()

    redirect_page = url_for('radio.radio_all',client='web')

    session['last_url'] = redirect_page

    return redirect(redirect_page)


# ---> Edit Image
@radio.route('/radio/edit_image/<id>', methods=['GET', 'POST'])
def radio_edit_image(id):

    radio = Radios.query.filter_by(id=id).first()

    form = ImageForm()

    if form.validate_on_submit():

        image_file = form.image_file.data

        image = radio.name + '.png'

        image_file.save(os.path.join(CONFIG.PROJECT_ROOT_DIR, CONFIG.PROJECT_RADIOS_IMG_DIR, image))

        redirect_page = url_for('radio.radio_show',id=id)

        session['last_url'] = redirect_page

        return redirect(redirect_page)


    session['last_url'] = url_for('radio.radio_edit_image',id=id)

    template_page = 'radio_edit_image.html'

    return render_template(template_page, form=form, bookmark_manager=bookmark_manager)

###########################################################################################
## Radio Link Add, Edit, Delete
###########################################################################################

# ---> Radio Link Add
@radio.route('/radio/add_link/<id>', methods=['GET', 'POST'])
def radio_add_link(id):

    form = LinkForm()

    if form.validate_on_submit():

        name = form.name.data
        social_name = form.social_name.data
        url = form.url.data

        if social_name != 'none':
            name = social_name

        radio = Radios.query.filter_by(id=id).first()

        radio_link = Radio_Link(name=name,
                                url=url,
                                radios=radio)

        db.session.add(radio_link)
        db.session.commit()

        redirect_page = url_for('radio.radio_show',id=id)
        session['last_url'] = redirect_page

        return redirect(redirect_page)

    
    session['last_url'] = url_for('radio.radio_add_link',id=id)

    template_page = 'radio_add_link.html'

    return render_template(template_page, form=form, bookmark_manager=bookmark_manager)


# ---> Radio Link Edit
@radio.route('/radio/edit_link/<id>', methods=['GET', 'POST'])
def radio_edit_link(id):

    radio_link = Radio_Link.query.filter_by(id=id).first()

    form = LinkForm()

    if form.validate_on_submit():

        radio_link.name = form.name.data
        radio_link.url = form.url.data

        db.session.commit()

        redirect_page = url_for('radio.radio_show',id=radio_link.radio_id)

        session['last_url'] = redirect_page

        return redirect(redirect_page)

    form.name.data = radio_link.name
    form.url.data = radio_link.url

    session['last_url'] = url_for('radio.radio_edit_link',id=id)

    template_page = 'radio_edit_link.html'

    return render_template(template_page, form=form, bookmark_manager=bookmark_manager)


# ---> Radio Link Delete
@radio.route('/radio/delete_link/<id>', methods=['GET'])
def radio_link_delete(id):
    radio_link = Radio_Link.query.filter_by(id=id).first()
    id = radio_link.radio_id

    db.session.delete(radio_link)
    db.session.commit()

    redirect_page = url_for('radio.radio_show',id=id)

    session['last_url'] = redirect_page

    return redirect(redirect_page)

###########################################################################################
## Fav, Unfav, Bookmark, Stars
###########################################################################################

# ---> Radio Fav
@radio.route('/radio_fav/<id>', methods=['GET'])
def radio_fav(id):
    radio = Radios.query.filter_by(id=id).first()

    radio.fav = True

    db.session.commit()

    redirect_page = url_for('radio.radio_show', id=id)

    session['last_url'] = redirect_page

    return redirect(redirect_page)

# ---> Radio UnFav
@radio.route('/radio_unfav/<id>', methods=['GET'])
def radio_unfav(id):
    radio = Radios.query.filter_by(id=id).first()

    radio.fav = False

    db.session.commit()

    redirect_page = url_for('radio.radio_show', id=id)

    session['last_url'] = redirect_page

    return redirect(redirect_page)

# ---> Radio Set Stars
@radio.route('/radio/stars/<id>/<stars>', methods=['GET'])
def radio_stars(id,stars):
    radio = Radios.query.filter_by(id=id).first()

    radio.stars = int(stars)

    db.session.commit()

    redirect_page = url_for('radio.radio_show',id=id)

    session['last_url'] = redirect_page

    return redirect(redirect_page)

###########################################################################################
## Program
###########################################################################################

# ---> Program List
@radio.route('/radio/list_program', methods=['GET'])
def radio_list_program():

    program_list = Program.query.all()

    session['last_url'] = url_for('radio.radio_list_program')

    template_page = 'radio_program_list.html'

    return render_template(template_page, program_list=program_list, bookmark_manager=bookmark_manager)

# ---> Program Add
@radio.route('/radio/add_program/<id>', methods=['GET', 'POST'])
def radio_add_program(id):

    form = ProgramForm()

    if form.validate_on_submit():

        name = form.name.data
        times = form.times.data
        week_days = form.week_days.data

        description = ''
        style = ''
        stars = 0
        fav = False

        radio = Radios.query.filter_by(id=id).first()

        program = Program(name=name,
                        times=times,
                        week_days=week_days,
                        description=description,
                        style=style,
                        stars=stars,
                        fav=fav,
                        radios=radio)

        db.session.add(program)
        db.session.commit()

        redirect_page = url_for('radio.radio_show',id=id)
        session['last_url'] = redirect_page

        return redirect(redirect_page)

    
    form.times.data = 'XX:00-XX:00'
    form.week_days.data = '0,1,2,3,4'

    session['last_url'] = url_for('radio.radio_add_program',id=id)

    template_page = 'radio_add_program.html'

    return render_template(template_page, form=form, bookmark_manager=bookmark_manager)


# ---> Program Edit
@radio.route('/radio/edit_program/<id>', methods=['GET', 'POST'])
def radio_edit_program(id):

    program = Program.query.filter_by(id=id).first()
 
    form = ProgramForm()

    if form.validate_on_submit():

        program.name = form.name.data
        program.times = form.times.data
        program.week_days = form.week_days.data
        program.description = form.description.data
        program.style = form.style.data
        program.twitter = form.twitter.data

        db.session.commit()

        redirect_page = url_for('radio.radio_show',id=program.radio_id)
        session['last_url'] = redirect_page

        return redirect(redirect_page)

    form.name.data = program.name
    form.times.data = program.times
    form.week_days.data = program.week_days
    form.description.data = program.description
    form.style.data = program.style
    form.twitter.data = program.twitter
    
    session['last_url'] = url_for('radio.radio_edit_program',id=id)

    template_page = 'radio_edit_program.html'

    return render_template(template_page, form=form, bookmark_manager=bookmark_manager)


# ---> Program Delete
@radio.route('/radio/delete_program/<id>', methods=['GET'])
def radio_program_delete(id):
    program = Program.query.filter_by(id=id).first()
    radio_id = program.radio_id

    db.session.delete(program)
    db.session.commit()

    redirect_page = url_for('radio.radio_show',id=radio_id)

    session['last_url'] = redirect_page

    return redirect(redirect_page)
