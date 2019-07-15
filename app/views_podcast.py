
from flask import render_template, redirect, request, Blueprint, session, url_for, g
import sys, os
import urllib2
import datetime

reload(sys)
sys.setdefaultencoding('utf8')

podcast = Blueprint('podcast', __name__, template_folder='templates/podcast')

from .models import Podcast, Podcast_Link, Bookmark, Radios, Episode
from . import db, CONFIG, bookmark_manager
from .forms import ImageForm, LinkForm, PodcastForm, TagForm, BookmarkForm, URLForm, PodcastEpisodeForm
from .feed_manager import FeedManager

from sqlalchemy import desc

from podcast import PodcastInfo
        
###########################################################################################
# Podcast List and Load
###########################################################################################

# ---> Podcast List
@podcast.route('/podcast/list', methods=['GET'])
def podcast_list():

    podcast_list = Podcast.query.all()

    session['last_url'] = url_for('podcast.podcast_list')

    template_page = 'podcast_list.html'

    return render_template(template_page, podcast_list=podcast_list, bookmark_manager=bookmark_manager)

# ---> All Podcasts
@podcast.route('/podcast/all', methods=['GET'])
def podcast_all():

    podcast_list = Podcast.query.order_by(desc(Podcast.stars), Podcast.priority).all()

    session['last_url'] = url_for('podcast.podcast_all')

    template_page = 'podcast_grid.html'

    return render_template(template_page, podcast_list=podcast_list, title='All Podcasts', bookmark_manager=bookmark_manager)

# ---> Favorite Podcasts
@podcast.route('/podcast/favorite', methods=['GET'])
def podcast_favorite():

    podcast_list = Podcast.query.filter(Podcast.fav==True).order_by(Podcast.priority).all()

    session['last_url'] = url_for('podcast.podcast_all')

    template_page = 'podcast_grid.html'

    return render_template(template_page, podcast_list=podcast_list, title='Favorite Podcasts', bookmark_manager=bookmark_manager)

# ---> Styles
@podcast.route('/podcast/styles', methods=['GET'])
def podcast_styles():

    podcast_list = db.session.query(Podcast.style).distinct()
    podcast_styles = [ podcast.style for podcast in podcast_list if podcast.style != '' ]
    podcast_styles.sort()

    session['last_url'] = url_for('podcast.podcast_styles')

    template_page = 'podcast_styles.html'

    return render_template(template_page, podcast_styles=podcast_styles, bookmark_manager=bookmark_manager)

@podcast.route('/podcast/style/<style>', methods=['GET'])
def podcast_style(style):

    podcast_list = Podcast.query.filter(Podcast.style==style)

    session['last_url'] = url_for('podcast.podcast_style', style=style)

    template_page = 'podcast_grid.html'

    return render_template(template_page, podcast_list=podcast_list, title=style, bookmark_manager=bookmark_manager)

# ---> Countries
@podcast.route('/podcast/countries', methods=['GET'])
def podcast_countries():

    podcast_list = db.session.query(Podcast.country).distinct()
    podcast_countries = [ podcast.country for podcast in podcast_list if podcast.country != '' ]
    podcast_countries.sort()

    session['last_url'] = url_for('podcast.podcast_countries')

    template_page = 'podcast_countries.html'

    return render_template(template_page,podcast_countries=podcast_countries, bookmark_manager=bookmark_manager)

@podcast.route('/podcast/country/<country>', methods=['GET'])
def podcast_country(country):

    podcast_list = Podcast.query.filter(Podcast.country==country)

    session['last_url'] = url_for('podcast.podcast_country',country=country)

    template_page = 'podcast_grid.html'

    return render_template(template_page, podcast_list=podcast_list, title=country, bookmark_manager=bookmark_manager)

###########################################################################################
# Feeds, Episodes
###########################################################################################

# ---> Podcast Show
@podcast.route('/podcast/show/<id>', methods=['GET'])
def podcast_show(id):

    podcast = Podcast.query.filter_by(id=id).first()

    podcast.episode_list.sort(key=lambda x: x.pub_date, reverse=True)

    session['last_url'] = url_for('podcast.podcast_show', id=id)

    template_page = 'podcast_show.html'

    return render_template(template_page, podcast=podcast, social_sites=CONFIG.SOCIAL_SITES, bookmark_manager=bookmark_manager)


# ---> Feed Update
@podcast.route('/podcast/feed/update/<id>', methods=['GET'])
def podcast_feed_update(id):

    podcast = Podcast.query.filter_by(id=id).first()
    pod_info = PodcastInfo(podcast)
    pod_info.update_feed()
    
    redirect_page = url_for('podcast.podcast_feed_episodes', id=id)

    session['last_url'] = redirect_page

    return redirect(redirect_page)


# ---> Feed Episodes
@podcast.route('/podcast/feed/episodes/<id>', methods=['GET'])
def podcast_feed_episodes(id):

    podcast = Podcast.query.filter_by(id=id).first()
    pod_info = PodcastInfo(podcast)
    pod_info.update_items_list()
    
    episodes_list = pod_info.episode_list()

    session['last_url'] = url_for('podcast.podcast_feed_episodes', id=id)

    template_page = 'podcast_feed_episodes.html'

    return render_template(template_page,podcast=podcast,episodes_list=episodes_list, social_sites=CONFIG.SOCIAL_SITES, bookmark_manager=bookmark_manager)

# ---> Add Episode
@podcast.route('/podcast/add_episode/<id>', methods=['GET', 'POST'])
def podcast_add_episode(id):

    form = URLForm()
    
    if form.validate_on_submit():

        name = form.name.data
        url = form.url.data

        podcast = Podcast.query.filter_by(id=id).first()
        pod_info = PodcastInfo(podcast)

        if 'temp_file' in session:
            del session['temp_file']

        if 'file_size' in session:
            del session['file_size']

        pod_info.download_episode_from_url(url,name)

        redirect_page = url_for('podcast.podcast_show',id=id)

        session['last_url'] = redirect_page

        return redirect(redirect_page)

    session['last_url'] = url_for('podcast.podcast_add_episode',id=id)

    template_page = 'podcast_add_episode.html'

    return render_template(template_page, form=form, config=CONFIG, bookmark_manager=bookmark_manager)


# ---> Add URL to local feed
@podcast.route('/podcast/add_to_feed/<id>', methods=['GET', 'POST'])
def podcast_add_to_feed(id):

    form = PodcastEpisodeForm()
    
    if form.validate_on_submit():

        title = form.title.data
        url = form.url.data
        date = form.date.data

        podcast = Podcast.query.filter_by(id=id).first()
        pod_info = PodcastInfo(podcast)

        pod_info.add_episode_to_feed(title, url, date)

        redirect_page = url_for('podcast.podcast_feed_episodes',id=id)

        session['last_url'] = redirect_page

        return redirect(redirect_page)

    form.title.data = session['feed_title']
    form.url.data = session['feed_url']
    form.date.data = session['feed_date']

    session['last_url'] = url_for('podcast.podcast_add_to_feed',id=id)

    template_page = 'podcast_add_to_feed.html'

    return render_template(template_page, form=form, config=CONFIG, bookmark_manager=bookmark_manager)


# ---> Import Feed from URL
@podcast.route('/podcast/import_from_url/<id>', methods=['GET','POST'])
def podcast_import_from_url(id):

    form = URLForm()

    if form.validate_on_submit():

        url = form.url.data

        feed_manager = FeedManager(url)

        session['feed_title'] = feed_manager.get_title()
        session['feed_url'] = feed_manager.get_audio_url()
        session['feed_date'] = feed_manager.get_pub_date()

        return redirect( url_for('podcast.podcast_add_to_feed', id=id) )

    else:

        return render_template('podcast_import_from_url.html', form=form, bookmark_manager=bookmark_manager)


# ---> Delete Episode
@podcast.route('/podcast/delete_episode/<id>/<track>', methods=['GET', 'POST'])
def podcast_delete_episode(id,track):
    
    podcast = Podcast.query.filter_by(id=id).first()
    pod_info = PodcastInfo(podcast)

    pod_info.delete_episode(int(track))

    redirect_page = url_for('podcast.podcast_show', id=id)

    session['last_url'] = redirect_page

    return redirect(redirect_page)


# ---> List to Copy Episode
@podcast.route('/podcast/list_to_copy/episode/<src_id>/<track>', methods=['GET'])
def podcast_list_to_copy_episode(src_id,track):

    podcast_list = Podcast.query.all()

    session['last_url'] = url_for('podcast.podcast_list_to_copy_episode', src_id=src_id, track=track)

    template_page = 'podcast_list_to_copy.html'

    return render_template(template_page, podcast_list=podcast_list, src_id=src_id, track=track, bookmark_manager=bookmark_manager)


# ---> Move Episode
@podcast.route('/podcast/episode/copy_to/<ep_id>/<dst_id>', methods=['GET'])
def podcast_episode_copy_to(ep_id, dst_id):

    episode = Episode.query.filter_by(id=ep_id).first()

    new_episode = Episode(
                        title=episode.title,
                        url=episode.url,
                        description=episode.description,
                        pub_date=episode.pub_date,
                        downloaded=episode.downloaded,
                        local_file=episode.local_file,
                        audio_size=episode.audio_size,
                        audio_time=episode.audio_time,
                        podcast_id=dst_id
                   )
                        
    db.session.add(new_episode)
    db.session.commit()

    return redirect(url_for('podcast.podcast_episode_list',id=dst_id))


# ---> List to Move Episode
@podcast.route('/podcast/list_to_move/episode/<src_id>/<track>', methods=['GET'])
def podcast_list_to_move_episode(src_id,track):

    podcast_list = Podcast.query.all()

    session['last_url'] = url_for('podcast.podcast_list_to_move_episode', src_id=src_id, track=track)

    template_page = 'podcast_list_to_move.html'

    return render_template(template_page, podcast_list=podcast_list,src_id=src_id, track=track, bookmark_manager=bookmark_manager)


###########################################################################################
# Podcast Add, Edit, Del
###########################################################################################

# ---> Podcast Add
@podcast.route('/podcast/add', methods=['GET', 'POST'])
def podcast_add():

    form = PodcastForm()
    
    if form.validate_on_submit():

        name = form.name.data
        image = form.image.data
        pod_dir = form.pod_dir.data

        stars = 1
        fav = False

        podcast = Podcast(name=name,
                        image=image,
                        pod_dir=pod_dir,
                        stars=stars,
                        fav=fav
                       )

        db.session.add(podcast)
        db.session.commit()

        pod_info = PodcastInfo(podcast)
        pod_info.create_init_files()

        redirect_page = url_for('podcast.podcast_episode_list',id=podcast.id)

        session['last_url'] = redirect_page

        return redirect(redirect_page)

    session['last_url'] = url_for('podcast.podcast_add')

    template_page = 'podcast_add.html'

    return render_template(template_page, form=form, bookmark_manager=bookmark_manager)


# ---> Podcast Edit
@podcast.route('/podcast/edit/<id>', methods=['GET', 'POST'])
def podcast_edit(id):

    podcast = Podcast.query.filter_by(id=id).first()

    form = PodcastForm()
    
    if form.validate_on_submit():

        podcast.name = form.name.data
        podcast.image = form.image.data
        podcast.country = form.country.data
        podcast.description = form.description.data
        podcast.style = form.style.data
        podcast.feed_url = form.feed_url.data
        podcast.internal_feed_url = form.internal_feed_url.data
        podcast.web_url = form.web_url.data
        podcast.pod_dir = form.pod_dir.data
        podcast.publisher = form.publisher.data
        podcast.priority = form.priority.data

        db.session.commit()

        redirect_page = url_for('podcast.podcast_episode_list',id=id)

        session['last_url'] = redirect_page

        return redirect(redirect_page)


    form.name.data = podcast.name
    form.image.data = podcast.image 
    form.country.data = podcast.country
    form.description.data = podcast.description 
    form.style.data = podcast.style 
    form.feed_url.data = podcast.feed_url 
    form.internal_feed_url.data = podcast.internal_feed_url 
    form.web_url.data = podcast.web_url 
    form.pod_dir.data = podcast.pod_dir 
    form.publisher.data = podcast.publisher 
    form.priority.data = podcast.priority 

    session['last_url'] = url_for('podcast.podcast_edit',id=id)

    template_page = 'podcast_edit.html'

    return render_template(template_page,form=form, bookmark_manager=bookmark_manager)


# ---> Podcast Delete
@podcast.route('/podcast/delete/<id>', methods=['GET'])
def podcast_delete(id):
    podcast = Podcast.query.filter_by(id=id).first()
    db.session.delete(podcast)
    db.session.commit()

    redirect_page = url_for('podcast.podcast_all')

    session['last_url'] = redirect_page

    return redirect(redirect_page)

###########################################################################################
# Episode
###########################################################################################

# ---> Episode List
@podcast.route('/podcast/episode/list/<id>', methods=['GET'])
def podcast_episode_list(id):

    podcast = Podcast.query.filter_by(id=id).first()

    episode_list = Episode.query.filter_by(podcast_id=id).order_by(desc(Episode.pub_date)).all()

    session['last_url'] = url_for('podcast.podcast_feed_episodes', id=id)

    return render_template('podcast_episode_list.html', podcast=podcast, episode_list=episode_list, social_sites=CONFIG.SOCIAL_SITES, bookmark_manager=bookmark_manager)


# ---> Import Episode from URL
@podcast.route('/podcast/episode/import_from_url/<id>', methods=['GET','POST'])
def podcast_episode_import_from_url(id):

    form = URLForm()

    if form.validate_on_submit():

        url = form.url.data

        feed_manager = FeedManager(url)

        session['feed_title'] = feed_manager.get_title()
        session['feed_url'] = feed_manager.get_audio_url()
        session['feed_date'] = feed_manager.get_pub_date()
        session['feed_description'] = feed_manager.get_description()
        session['feed_audio_size'] = 0

        return redirect( url_for('podcast.podcast_episode_add', id=id) )

    else:

        return render_template('podcast_import_from_url.html', form=form, bookmark_manager=bookmark_manager)


# ---> Add Episode to Podcast
@podcast.route('/podcast/episode/add/<id>', methods=['GET', 'POST'])
def podcast_episode_add(id):

    form = PodcastEpisodeForm()
    
    if form.validate_on_submit():

        title = form.title.data
        url = form.url.data
        date = form.date.data
        description = form.description.data
        audio_size = form.audio_size.data
        audio_time = form.audio_time.data

        podcast = Podcast.query.filter_by(id=id).first()

        episode = Episode(title=title,
                        url=url,
                        description=description,
                        pub_date=date,
                        downloaded=False,
                        local_file='',
                        audio_size=audio_size,
                        audio_time=audio_time,
                        podcast=podcast)

        db.session.add(episode)
        db.session.commit()

        redirect_page = url_for('podcast.podcast_episode_list',id=id)

        session['last_url'] = redirect_page

        return redirect(redirect_page)

    form.title.data = session['feed_title']
    form.url.data = session['feed_url']
    form.date.data = session['feed_date']
    form.description.data = session['feed_description']
    form.audio_size.data = session['feed_audio_size']

    session['last_url'] = url_for('podcast.podcast_episode_add',id=id)

    template_page = 'podcast_episode_add.html'

    return render_template(template_page, form=form, config=CONFIG, bookmark_manager=bookmark_manager)



# ---> Edit Episode
@podcast.route('/podcast/episode/edit/<id>', methods=['GET', 'POST'])
def podcast_episode_edit(id):

    form = PodcastEpisodeForm()
    
    episode = Episode.query.filter_by(id=id).first()

    if form.validate_on_submit():

        episode.title = form.title.data
        episode.url = form.url.data
        episode.pub_date = form.date.data
        episode.description = form.description.data
        episode.audio_size = form.audio_size.data
        episode.audio_time = form.audio_time.data

        db.session.commit()

        redirect_page = url_for('podcast.podcast_episode_list',id=episode.podcast_id)

        session['last_url'] = redirect_page

        return redirect(redirect_page)

    form.title.data = episode.title
    form.url.data = episode.url
    form.date.data = episode.pub_date
    form.description.data = episode.description
    form.audio_size.data = episode.audio_size
    form.audio_time.data = episode.audio_time

    session['last_url'] = url_for('podcast.podcast_episode_add',id=id)

    template_page = 'podcast_episode_edit.html'

    return render_template(template_page, form=form, config=CONFIG, bookmark_manager=bookmark_manager)


# ---> Episode Delete
@podcast.route('/podcast/episode/delete/<id>', methods=['GET'])
def podcast_episode_delete(id):
    episode = Episode.query.filter_by(id=id).first()
    pod_id = episode.podcast_id
    db.session.delete(episode)
    db.session.commit()

    redirect_page = url_for('podcast.podcast_episode_list',id=pod_id)

    session['last_url'] = redirect_page

    return redirect(redirect_page)


# ---> Copy Episode
@podcast.route('/podcast/episode/copy/<src_id>/<track>/<dst_id>', methods=['GET'])
def podcast_episode_copy(src_id,track,dst_id):

    src_podcast = Podcast.query.filter_by(id=src_id).first()
    src_pod_info = PodcastInfo(src_podcast)

    src_pod_info.update_items_list()
    episode_info = src_pod_info.episode_list()[int(track) - 1]

    title = episode_info['title']
    url = episode_info['url']
    pub_date = episode_info['pubdate'].split(' +')[0]
    pub_date = datetime.datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S")
    pub_date = pub_date.strftime('%Y.%m.%d-%H:%M:%S')
    description = episode_info['description']
    length = episode_info['length']


    episode = Episode(title=title,
        url=url,
        description=description,
        pub_date=pub_date,
        downloaded=False,
        local_file='',
        audio_size=length,
        audio_time='0',
        podcast_id=dst_id
    )

    db.session.add(episode)
    db.session.commit()

    return redirect(url_for('podcast.podcast_episode_list',id=dst_id))


# ---> Add Episode to DB
@podcast.route('/podcast/episode/add_to_db/<pod_id>/<track>', methods=['GET'])
def podcast_episode_add_to_db(pod_id,track):

    podcast = Podcast.query.filter_by(id=pod_id).first()
    pod_info = PodcastInfo(podcast)

    pod_info.update_items_list()
    episode_info = pod_info.episode_list()[int(track) - 1]

    title = episode_info['title']
    url = episode_info['url']
    pub_date = episode_info['pubdate'].split(' +')[0]
    pub_date = datetime.datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S")
    pub_date = pub_date.strftime('%Y.%m.%d-%H:%M:%S')
    description = episode_info['description']
    length = episode_info['length']

    urls_in_db = [ ep.url for ep in podcast.episode_list ]
    if not (url in urls_in_db):
        episode = Episode(title=title,
            url=url,
            description=description,
            pub_date=pub_date,
            downloaded=False,
            local_file='',
            audio_size=length,
            audio_time='0',
            podcast_id=pod_id
        )

        db.session.add(episode)
        db.session.commit()

    return redirect(url_for('podcast.podcast_episode_list',id=pod_id))


# ---> Create Feed
@podcast.route('/podcast/create_feed/<id>', methods=['GET'])
def podcast_create_feed(id):

    podcast = Podcast.query.filter_by(id=id).first()
    pod_info = PodcastInfo(podcast)
    pod_info.create_feed()
    
    redirect_page = url_for('podcast.podcast_episode_list', id=id)

    session['last_url'] = redirect_page

    return redirect(redirect_page)


###########################################################################################
# Podcast Link Add, Edit, Del
###########################################################################################

# ---> Podcast Link Add
@podcast.route('/podcast/add_link/<id>', methods=['GET', 'POST'])
def podcast_add_link(id):

    form = LinkForm()

    if form.validate_on_submit():

        name = form.name.data
        social_name = form.social_name.data
        url = form.url.data

        if social_name != 'none':
            name = social_name

        podcast = Podcast.query.filter_by(id=id).first()
        
        podcast_link = Podcast_Link(name=name,url=url,podcast=podcast)

        db.session.add(podcast_link)
        db.session.commit()

        redirect_page = url_for('podcast.podcast_episode_list', id=id)

        session['last_url'] = redirect_page

        return redirect(redirect_page)


    session['last_url'] = url_for('podcast.podcast_add_link', id=id)

    template_page = 'podcast_add_link.html'

    return render_template(template_page, form=form, bookmark_manager=bookmark_manager)


# ---> Podcast Link Edit
@podcast.route('/podcast/edit_link/<id>', methods=['GET', 'POST'])
def podcast_edit_link(id):

    podcast_link = Podcast_Link.query.filter_by(id=id).first()

    form = LinkForm()

    if form.validate_on_submit():

        podcast_link.name = form.name.data
        podcast_link.url = form.url.data

        db.session.commit()

        redirect_page = url_for('podcast.podcast_episode_list', id=podcast_link.podcast_id)

        session['last_url'] = redirect_page

        return redirect(redirect_page)

    form.name.data = podcast_link.name
    form.url.data = podcast_link.url

    session['last_url'] = url_for('podcast.podcast_edit_link',id=id)

    template_page = 'podcast_edit_link.html'

    return render_template(template_page, form=form, bookmark_manager=bookmark_manager)


# ---> Delete Podcast Link
@podcast.route('/podcast/delete_link/<id>', methods=['GET', 'POST'])
def podcast_delete_link(id):

    podcast_link = Podcast_Link.query.filter_by(id=id).first()
    db.session.delete(podcast_link)
    db.session.commit()

    redirect_page = url_for('podcast.podcast_episode_list',id=podcast_link.podcast_id)

    session['last_url'] = redirect_page

    return redirect(redirect_page)


###########################################################################################
## Fav, Unfav, Stars
###########################################################################################

# ---> Podcast Fav
@podcast.route('/podcast_fav/<id>', methods=['GET'])
def podcast_fav(id):
    podcast = Podcast.query.filter_by(id=id).first()

    podcast.fav = True

    db.session.commit()

    redirect_page = url_for('podcast.podcast_show', id=id)

    session['last_url'] = redirect_page

    return redirect(redirect_page)

# ---> Podcast UnFav
@podcast.route('/podcast_unfav/<id>', methods=['GET'])
def podcast_unfav(id):
    podcast = Podcast.query.filter_by(id=id).first()

    podcast.fav = False

    db.session.commit()

    redirect_page = url_for('podcast.podcast_show', id=id)

    session['last_url'] = redirect_page

    return redirect(redirect_page)

# ---> Podcast Bookmark
@podcast.route('/podcast_bookmark/<id>', methods=['GET'])
def podcast_bookmark(id):
    podcast = Podcast.query.filter_by(id=id).first()

    bookmark_url_list = [ bookmark.url for bookmark in bookmark_manager.bookmark_list ]

    url = url_for('podcast.podcast_episode_list',id=id)
    image_url = '/static/images/podcasts/' + podcast.image
    priority = len(bookmark_url_list) + 1

    if not(url in bookmark_url_list):

        bookmark = Bookmark(url=url,
                            image_url=image_url,
                            priority=priority)

        db.session.add(bookmark)
        db.session.commit()

    bookmark_manager.update_bookmark_list()

    redirect_page = url_for('podcast.podcast_episode_list', id=id)

    session['last_url'] = redirect_page

    return redirect(redirect_page)


# ---> Podcast Set Stars
@podcast.route('/podcast/stars/<id>/<stars>', methods=['GET'])
def podcast_stars(id,stars):
    podcast = Podcast.query.filter_by(id=id).first()

    podcast.stars = int(stars)

    db.session.commit()

    redirect_page = url_for('podcast.podcast_show',id=id)

    session['last_url'] = redirect_page

    return redirect(redirect_page)


# ---> Podcast External URL
@podcast.route('/podcast/episode_url/<id>/<track_num>', methods=['GET'])
def podcast_episode_url(id,track_num):

    podcast = Podcast.query.filter_by(id=id).first()
    pod_info = PodcastInfo(podcast)

    ext_url = pod_info.episode_ext_url(int(track_num))

    return redirect(ext_url)

