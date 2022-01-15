"""
Route management.

This provides all of the websites routes and handles what happens each
time a browser hits each of the paths. This serves as the interaction
between the browser and the database while rendering the HTML templates
to be displayed.

You will have to make
"""
import secrets
import functools

from modules import *
from flask import *
import database

user_details = {}                   # User details kept for us
session = {}                        # Session information (logged in state)
page = {}                           # Determines the page information

# Initialise the application
app = Flask(__name__)
app.secret_key = """bXrb+FnpdadYxt4qu1HlK1ob2tJSxK0UGqfl4YHOEDyq1SBuhHXUJ9ynwlS1msytwdWd2IrGEqRL
eDkelBIB6HG0d077K1tsYRuh0K/JFWXk4Z6ieErNOfs6uOCZszJei7ga0IBJ1cuedeEx7iS7gFxm
2bLrCt7kE5OYTgnOWkxqO43KGmWz4V+F1ry2//Rtn/Doi7dzcv9wJaEGCfV6mybDJCmzr9SMpuF9
B9ahzy0c7E/tPo+S5tm62P9SSg4Qg17qLzYN0sk="""

def route(_flask_rule, login: bool=True, admin: bool=False, **kwargs):
    def decorator(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            try:
                if login and ('logged_in' not in session or not session['logged_in']):
                    return redirect(url_for('login'))

                if admin:
                    database.ensure_super(user_details['username'])

                return func(*args, **kwargs)
            except database.UserException as e:
                flash(str(e))
                return render_template(
                    'admin-only.html',
                    session=session,
                    page=page,
                    user=user_details,
                )
        flask_decorator = app.route(_flask_rule, **kwargs)
        return flask_decorator(wrapped)
    return decorator

#####################################################
#   INDEX
#####################################################

@route('/')
def index():
    """
    Provides the main home screen if logged in.
        - Shows user playlists
        - Shows user Podcast subscriptions
        - Shows superUser status
    """
    page['title'] = 'User Management'

    username = user_details['username']

    user_playlists = database.user_playlists(username)
    user_subscribed_podcasts = database.user_podcast_subscriptions(username)
    user_in_progress_items = database.user_in_progress_items(username)
    contacts = database.get_user_contacts(username)

    return render_template(
        'index.html',
        session=session,
        page=page,
        user=user_details,
        playlists=user_playlists,
        subpodcasts=user_subscribed_podcasts,
        usercurrent=user_in_progress_items,
        contacts=contacts,
    )

#####################################################
#####################################################
####    User Management
#####################################################
#####################################################

@route('/login', methods=['POST', 'GET'], login=False)
def login():
    """
    Provides /login
        - [GET] If they are just viewing the page then render login page.
        - [POST] If submitting login details, check login.
    """
    if request.method == 'GET':
        return render_template('login.html', session=session, page=page)

    try:
        login_return_data = database.check_login(
            request.form['username'],
            request.form['password']
        )
        page['bar'] = True
        flash('You have been logged in successfully')
        session['logged_in'] = True

        global user_details
        user_details = login_return_data
        return redirect(url_for('index'))
    except database.UserException as e:
        page['bar'] = False
        flash(str(e))
        return redirect(url_for('login'))


#####################################################
#   LOGOUT
#####################################################

@route('/logout')
def logout():
    """
    Logs out of the current session
        - Removes any stored user data.
    """
    session['logged_in'] = False
    page['bar'] = True
    flash('You have been logged out')
    return redirect(url_for('index'))


#####################################################
#####################################################
####    List All items
#####################################################
#####################################################


#####################################################
#   List Artists
#####################################################
@route('/list/artists')
def list_artists():
    """
    Lists all the artists in your media server
    Can do this without a login
    """
    # # Check if the user is logged in, if not: back to login.
    # if('logged_in' not in session or not session['logged_in']):
    #     return redirect(url_for('login'))

    page['title'] = 'List Artists'

    # Get a list of all artists from the database
    allartists = None
    allartists = database.get_allartists()

    # Data integrity checks
    if allartists == None:
        allartists = []


    return render_template('listitems/listartists.html',
                           session=session,
                           page=page,
                           user=user_details,
                           allartists=allartists)


#####################################################
#   List Songs
#####################################################
@route('/list/songs')
def list_songs():
    """
    Lists all the songs in your media server
    Can do this without a login
    """
    # # Check if the user is logged in, if not: back to login.
    # if('logged_in' not in session or not session['logged_in']):
    #     return redirect(url_for('login'))

    page['title'] = 'List Songs'

    # Get a list of all songs from the database
    allsongs = None
    allsongs = database.get_allsongs()


    # Data integrity checks
    if allsongs == None:
        allsongs = []


    return render_template('listitems/listsongs.html',
                           session=session,
                           page=page,
                           user=user_details,
                           allsongs=allsongs)

#####################################################
#   List Podcasts
#####################################################
@route('/list/podcasts')
def list_podcasts():
    """
    Lists all the podcasts in your media server
    Can do this without a login
    """
    # # Check if the user is logged in, if not: back to login.
    # if('logged_in' not in session or not session['logged_in']):
    #     return redirect(url_for('login'))

    page['title'] = 'List podcasts'

    # Get a list of all podcasts from the database
    allpodcasts = None
    allpodcasts = database.get_allpodcasts()

    # Data integrity checks
    if allpodcasts == None:
        allpodcasts = []


    return render_template('listitems/listpodcasts.html',
                           session=session,
                           page=page,
                           user=user_details,
                           allpodcasts=allpodcasts)


#####################################################
#   List Movies
#####################################################
@route('/list/movies')
def list_movies():
    """
    Lists all the movies in your media server
    Can do this without a login
    """
    # # Check if the user is logged in, if not: back to login.
    # if('logged_in' not in session or not session['logged_in']):
    #     return redirect(url_for('login'))

    page['title'] = 'List Movies'

    # Get a list of all movies from the database
    allmovies = None
    allmovies = database.get_allmovies()


    # Data integrity checks
    if allmovies == None:
        allmovies = []


    return render_template('listitems/listmovies.html',
                           session=session,
                           page=page,
                           user=user_details,
                           allmovies=allmovies)


#####################################################
#   List Albums
#####################################################
@route('/list/albums')
def list_albums():
    """
    Lists all the albums in your media server
    Can do this without a login
    """
    # # Check if the user is logged in, if not: back to login.
    # if('logged_in' not in session or not session['logged_in']):
    #     return redirect(url_for('login'))

    page['title'] = 'List Albums'

    # Get a list of all Albums from the database
    allalbums = None
    allalbums = database.get_allalbums()


    # Data integrity checks
    if allalbums == None:
        allalbums = []


    return render_template('listitems/listalbums.html',
                           session=session,
                           page=page,
                           user=user_details,
                           allalbums=allalbums)


#####################################################
#   List TVShows
#####################################################
@route('/list/tvshows')
def list_tvshows():
    """
    Lists all the tvshows in your media server
    Can do this without a login
    """
    # # Check if the user is logged in, if not: back to login.
    # if('logged_in' not in session or not session['logged_in']):
    #     return redirect(url_for('login'))

    page['title'] = 'List TV Shows'

    # Get a list of all tvshows from the database
    alltvshows = None
    alltvshows = database.get_alltvshows()


    # Data integrity checks
    if alltvshows == None:
        alltvshows = []


    return render_template('listitems/listtvshows.html',
                           session=session,
                           page=page,
                           user=user_details,
                           alltvshows=alltvshows)




#####################################################
#####################################################
####    List Individual items
#####################################################
#####################################################

#####################################################
#   Individual Artist
#####################################################
@route('/artist/<artist_id>')
def single_artist(artist_id):
    """
    Show a single artist by artist_id in your media server
    Can do this without a login
    """
    # # Check if the user is logged in, if not: back to login.
    # if('logged_in' not in session or not session['logged_in']):
    #     return redirect(url_for('login'))

    page['title'] = 'Artist ID: '+artist_id

    # Get a list of all artist by artist_id from the database
    artist = None
    artist = database.get_artist(artist_id)

    # Data integrity checks
    if artist == None:
        artist = []

    return render_template('singleitems/artist.html',
                           session=session,
                           page=page,
                           user=user_details,
                           artist=artist)


#####################################################
#   Individual Song
#####################################################
@route('/song/<song_id>')
def single_song(song_id):
    """
    Show a single song by song_id in your media server
    Can do this without a login
    """
    # # Check if the user is logged in, if not: back to login.
    # if('logged_in' not in session or not session['logged_in']):
    #     return redirect(url_for('login'))

    page['title'] = 'Song'


    # Get a list of all song by song_id from the database
    song = None
    song = database.get_song(song_id)

    songmetadata = None
    songmetadata = database.get_song_metadata(song_id)

    # Data integrity checks
    if song == None:
        song = []

    if songmetadata == None:
        songmetadata = []

    return render_template('singleitems/song.html',
                           session=session,
                           page=page,
                           user=user_details,
                           song=song,
                           songmetadata=songmetadata)

#####################################################
#   Query 6
#   Individual Podcast
#####################################################
@route('/podcast/<podcast_id>')
def single_podcast(podcast_id):
    """
    Show a single podcast by podcast_id in your media server
    Can do this without a login
    """
    #########
    # TODO  #
    #########

    #############################################################################
    # Fill in the Function below with to do all data handling for a podcast     #
    #############################################################################


    # Check if the user is logged in, if not: back to login.
    # if('logged_in' not in session or not session['logged_in']):
    #     return redirect(url_for('login'))

    # Set up some variables to manage the returns from the database fucntions
    # Get a list of all podcasts from the database
    alleppodcasts = None
    alleppodcasts = database.get_all_podcasteps_for_podcast(podcast_id)
    podcast_meta = None
    podcast_meta = database.get_podcast_metadata(podcast_id)
    podcast = database.get_podcast(podcast_id)
    page['title'] = podcast['podcast_title']
    print(podcast)
    artwork_list = []
    description_list = []
    copyrights_list = []
    other_data_list = []
    genre_list = []
    # Data integrity checks
    if alleppodcasts == None:
        alleppodcasts = []

    if podcast_meta == None:
        podcast_meta = []
    else :
        for item in podcast_meta:
            print(item)
            if (item['md_type_name'] == 'description') :
                description_list.append(item['md_value'])
            elif (item['md_type_name'] == 'artwork') :
                artwork_list.append(item['md_value'])
            elif (item['md_type_name'] == 'copyright holder') :
                copyrights_list.append(item['md_value'])
            elif (item['md_type_name'] == 'podcast genre') :
                genre_list.append(item['md_value'])
            else :
                other_data_list.append(item['md_value'])

    # NOTE :: YOU WILL NEED TO MODIFY THIS TO PASS THE APPROPRIATE VARIABLES
    return render_template('singleitems/podcast.html',
                           session=session,
                           page=page,
                           user=user_details,
                           podcast = podcast,
                           alleppodcasts=alleppodcasts,
                           podcast_meta = podcast_meta,
                           description_list = description_list,
                           artwork_list = artwork_list,
                           copyrights_list = copyrights_list,
                           other_data_list = other_data_list,
                           genre_list = genre_list)

#####################################################
#   Query 7
#   Individual Podcast Episode
#####################################################
# /podcastep/
@route('/podcast/<podcast_id>/podcastep/<media_id>')
def single_podcastep(podcast_id, media_id):
    """
    Show a single podcast epsiode by media_id in your media server
    Can do this without a login
    """
    #########
    # TODO  #
    #########

    #############################################################################
    # Fill in the Function below with to do all data handling for a podcast ep  #
    #############################################################################
    podcasteplist = database.get_podcastep(podcast_id, media_id)
    podcastep =  None
    page['title'] = "Nothing is here" # Add the title
    artwork_list = []
    description_list = []
    copyrights_list = []
    other_data_list = []
    genre_list = []
    # Data integrity check
    if podcasteplist != None:
        podcastep = podcasteplist[0]
        page['title'] = podcastep['podcast_episode_title'] # Add the title
        for item in podcasteplist:
            print(item)
            if (item['md_type_name'] == 'description') :
                description_list.append(item['md_value'])
            elif (item['md_type_name'] == 'artwork') :
                artwork_list.append(item['md_value'])
            elif (item['md_type_name'] == 'copyright holder') :
                copyrights_list.append(item['md_value'])
            elif (item['md_type_name'] == 'podcast genre') :
                genre_list.append(item['md_value'])
            else :
                other_data_list.append(item['md_value'])
    # Set up some variables to manage the returns from the database fucntions

    # Once retrieved, do some data integrity checks on the data

    # NOTE :: YOU WILL NEED TO MODIFY THIS TO PASS THE APPROPRIATE VARIABLES
    return render_template('singleitems/podcastep.html',
                           session=session,
                           page = page,
                           user = user_details,
                           podcastep = podcastep,
                           description_list = description_list,
                           artwork_list = artwork_list,
                           copyrights_list = copyrights_list,
                           other_data_list = other_data_list,
                           genre_list = genre_list)


#####################################################
#   Individual Movie
#####################################################
@route('/movie/<movie_id>')
def single_movie(movie_id):
    """
    Show a single movie by movie_id in your media server
    Can do this without a login
    """
    # # Check if the user is logged in, if not: back to login.
    # if('logged_in' not in session or not session['logged_in']):
    #     return redirect(url_for('login'))

    page['title'] = 'List Movies'

    # Get a list of all movies by movie_id from the database
    movie = None
    movie = database.get_movie(movie_id)


    # Data integrity checks
    if movie == None:
        movie = []


    return render_template('singleitems/movie.html',
                           session=session,
                           page=page,
                           user=user_details,
                           movie=movie)


#####################################################
#   Individual Album
#####################################################
@route('/album/<album_id>')
def single_album(album_id):
    """
    Show a single album by album_id in your media server
    Can do this without a login
    """
    # # Check if the user is logged in, if not: back to login.
    # if('logged_in' not in session or not session['logged_in']):
    #     return redirect(url_for('login'))

    page['title'] = 'List Albums'

    # Get the album plus associated metadata from the database
    album = None
    album = database.get_album(album_id)

    album_songs = None
    album_songs = database.get_album_songs(album_id)

    album_genres = None
    album_genres = database.get_album_genres(album_id)

    # Data integrity checks
    if album_songs == None:
        album_songs = []

    if album == None:
        album = []

    if album_genres == None:
        album_genres = []

    return render_template('singleitems/album.html',
                           session=session,
                           page=page,
                           user=user_details,
                           album=album,
                           album_songs=album_songs,
                           album_genres=album_genres)


#####################################################
#   Individual TVShow
#####################################################
@route('/tvshow/<tvshow_id>')
def single_tvshow(tvshow_id):
    """
    Show a single tvshows and its eps in your media server
    Can do this without a login
    """
    # # Check if the user is logged in, if not: back to login.
    # if('logged_in' not in session or not session['logged_in']):
    #     return redirect(url_for('login'))

    page['title'] = 'TV Show'

    # Get a list of all tvshows by tvshow_id from the database
    tvshow = None
    tvshow = database.get_tvshow(tvshow_id)

    tvshoweps = None
    tvshoweps = database.get_all_tvshoweps_for_tvshow(tvshow_id)

    # Data integrity checks
    if tvshow == None:
        tvshow = []

    if tvshoweps == None:
        tvshoweps = []

    return render_template('singleitems/tvshow.html',
                           session=session,
                           page=page,
                           user=user_details,
                           tvshow=tvshow,
                           tvshoweps=tvshoweps)

#####################################################
#   Individual TVShow Episode
#####################################################
@route('/tvshowep/<tvshowep_id>')
def single_tvshowep(tvshowep_id):
    """
    Show a single tvshow episode in your media server
    Can do this without a login
    """
    # # Check if the user is logged in, if not: back to login.
    # if('logged_in' not in session or not session['logged_in']):
    #     return redirect(url_for('login'))

    page['title'] = 'List TV Shows'

    # Get a list of all tvshow eps by media_id from the database
    tvshowep = None
    tvshowep = database.get_tvshowep(tvshowep_id)


    # Data integrity checks
    if tvshowep == None:
        tvshowep = []


    return render_template('singleitems/tvshowep.html',
                           session=session,
                           page=page,
                           user=user_details,
                           tvshowep=tvshowep)


#####################################################
#####################################################
####    Search Items
#####################################################
#####################################################

#####################################################
#   Search TVShow
#####################################################
@route('/search/tvshow', methods=['POST','GET'])
def search_tvshows():
    """
    Search all the tvshows in your media server
    """

    # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    page['title'] = 'TV Show Search'

    # Get a list of matching tv shows from the database
    tvshows = None
    if(request.method == 'POST'):

        tvshows = database.find_matchingtvshows(request.form['searchterm'])

    # Data integrity checks
    if tvshows == None or tvshows == []:
        tvshows = []
        page['bar'] = False
        flash("No matching tv shows found, please try again")
    else:
        page['bar'] = True
        flash('Found '+str(len(tvshows))+' results!')
        session['logged_in'] = True

    return render_template('searchitems/search_tvshows.html',
                           session=session,
                           page=page,
                           user=user_details,
                           tvshows=tvshows)

@route('/fuzzysearch/movies', methods=['GET'])
def fuzzysearch_movies():
    page['title'] = 'Movie Search'
    return render_template(
        'searchitems/search_movies_standalone.html',
        session=session,
        page=page,
        user=user_details
    )


#####################################################
#   Query 10
#   Search Movie
#####################################################
@route('/search/movie', methods=['POST','GET'])
def search_movies():
    """
    Search all the movies in your media server
    """
    page['title'] = 'Movie Search'

    if request.method == 'POST':
        movies = database.find_matchingmovies(request.form['searchterm'])

        if movies:
            page['bar'] = True
            flash(f'Found {len(movies)} results!')
        else:
            page['bar'] = False
            flash("No matching tv shows found, please try again")
        return render_template(
            'searchitems/search_movies.html',
            session=session,
            page=page,
            user=user_details,
            movies=movies
        )
    else:
        # NOTE :: YOU WILL NEED TO MODIFY THIS TO PASS THE APPROPRIATE VARIABLES
        return render_template(
            'searchitems/search_movies.html',
            session=session,
            page=page,
            user=user_details,
            movies=[]
        )


#####################################################
#   Add Movie
#####################################################
@route('/add/movie', methods=['POST','GET'])
def add_movie():
    """
    Add a new movie
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    page['title'] = 'Movie Creation'

    movies = None
    print("request form is:")
    newdict = {}
    print(request.form)

    # Check your incoming parameters
    if(request.method == 'POST'):

        # verify that the values are available:
        if ('movie_title' not in request.form):
            newdict['movie_title'] = 'Empty Film Value'
        else:
            newdict['movie_title'] = request.form['movie_title']
            print("We have a value: ",newdict['movie_title'])

        if ('release_year' not in request.form):
            newdict['release_year'] = '0'
        else:
            newdict['release_year'] = request.form['release_year']
            print("We have a value: ",newdict['release_year'])

        if ('description' not in request.form):
            newdict['description'] = 'Empty description field'
        else:
            newdict['description'] = request.form['description']
            print("We have a value: ",newdict['description'])

        if ('storage_location' not in request.form):
            newdict['storage_location'] = 'Empty storage location'
        else:
            newdict['storage_location'] = request.form['storage_location']
            print("We have a value: ",newdict['storage_location'])

        if ('film_genre' not in request.form):
            newdict['film_genre'] = 'drama'
        else:
            newdict['film_genre'] = request.form['film_genre']
            print("We have a value: ",newdict['film_genre'])

        if ('artwork' not in request.form):
            newdict['artwork'] = 'https://user-images.githubusercontent.com/24848110/33519396-7e56363c-d79d-11e7-969b-09782f5ccbab.png'
        else:
            newdict['artwork'] = request.form['artwork']
            print("We have a value: ",newdict['artwork'])

        print('newdict is:')
        print(newdict)

        #forward to the database to manage insert
        movies = database.add_movie_to_db(newdict['movie_title'],newdict['release_year'],newdict['description'],newdict['storage_location'],newdict['film_genre'])


        max_movie_id = database.get_last_movie()[0]['movie_id']
        print(movies)
        if movies is not None:
            max_movie_id = movies[0]

        # ideally this would redirect to your newly added movie
        return single_movie(max_movie_id)
    else:
        return render_template('createitems/createmovie.html',
                           session=session,
                           page=page,
                           user=user_details)


#####################################################
#   Query 9
#   Add song
#####################################################
@route('/add/song', methods=['POST','GET'])
def add_song():
    """
    Add a new Song
    """
    # # Check if the user is logged in, if not: back to login.
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    #########
    # TODO  #
    #########

    #############################################################################
    # Fill in the Function below with to do all data handling for adding a song #
    #############################################################################

    page['title'] = 'Song Creation' # Add the title

    songs = None
    print("request form is:")
    newdict = {}
    print(request.form)

    if request.method == 'POST':

        # verify that the values are available:
        if ('song_title' not in request.form):
            newdict['song_title'] = 'Empty Song Value'
        else:
            newdict['song_title'] = request.form['song_title']
            print("We have a value: ",newdict['song_title'])

        if ('song_length' not in request.form):
            newdict['song_length'] = '0'
        else:
            newdict['song_length'] = request.form['song_length']
            print("We have a value: ",newdict['song_length'])

        if ('description' not in request.form):
            newdict['description'] = 'Empty description field'
        else:
            newdict['description'] = request.form['description']
            print("We have a value: ",newdict['description'])

        if ('storage_location' not in request.form):
            newdict['storage_location'] = 'Empty storage location'
        else:
            newdict['storage_location'] = request.form['storage_location']
            print("We have a value: ",newdict['storage_location'])

        if ('song_genre' not in request.form):
            newdict['song_genre'] = 'Pop'
        else:
            newdict['song_genre'] = request.form['song_genre']
            print("We have a value: ",newdict['song_genre'])

        if ('artwork' not in request.form):
            newdict['artwork'] = 'https://user-images.githubusercontent.com/24848110/33519396-7e56363c-d79d-11e7-969b-09782f5ccbab.png'
        else:
            newdict['artwork'] = request.form['artwork']
            print("We have a value: ",newdict['artwork'])

        if ('artist_name' not in request.form):
            newdict['artist'] = 'No artist'
        else:
            newdict['artist'] = request.form['artist_name']
            print("We have a value: ",newdict['artist'])

        print('newdict is:')
        print(newdict)

        #forward to the database to manage insert

        songs = database.add_song_to_db(newdict['song_title'],newdict['song_length'],newdict['description'],newdict['storage_location'],newdict['song_genre'], newdict['artwork'], newdict['artist'])

        max_song_id = database.get_last_song()[0]['song_id']

        if songs is not None:
            max_song_id = songs[0]


        # Set up some variables to manage the post returns

        # Once retrieved, do some data integrity checks on the data

        # Once verified, send the appropriate data to the database for insertion

        # NOTE :: YOU WILL NEED TO MODIFY THIS TO PASS THE APPROPRIATE VARIABLES
        return single_song(max_song_id)
    else:
        return render_template('createitems/createsong.html',
                           session=session,
                           page=page,
                           user=user_details)


@route('/signup', methods=['GET', 'POST'], login=False)
def signup():
    """sign up a new account"""

    if request.method == 'GET':
        return render_template('signup.html', session=session, page=page)

    username = request.form['username']
    pw1 = request.form['password']
    pw2 = request.form['password2']
    #password should be checked on user side. but this is a SQL assignment, why bother?
    if pw1 != pw2:
        flash("two password is not the same")
        return redirect(url_for('signup'))

    try:
        database.signup(username, pw1)
    except database.UserException as e:
        flash(str(e))
        return redirect(url_for('signup'))

    flash('Sign up Successfully, please login in')
    return redirect(url_for('login'))

@route('/changepw', methods=['GET', 'POST'])
def changepw():
    if('logged_in' not in session or not session['logged_in']):
        return redirect(url_for('login'))

    if request.method == 'GET':
        return render_template(
            'changepw.html',
            session=session,
            page=page,
            user=user_details,
        )

    pw1 = request.form['password']
    pw2 = request.form['password2']
    #password should be checked on user side. but this is a SQL assignment, why bother?
    if pw1 != pw2:
        flash("two password is not the same")
        return redirect(url_for('changepw'))

    try:
        database.update_user_credential(
            user_details['username'],
            pw1,
        )
    except database.UserException as e:
        flash(str(e))
        return redirect(url_for('changepw'))

    flash("Password changed, please relogin")
    return redirect(url_for('logout'))

@route('/delete_contact', methods=['POST'])
def delete_contact():
    database.delete_contact(
        user_details['username'],
        request.form['type'],
        request.form['value'],
    )
    flash("contact deleted")
    return redirect(url_for("index"))

@route('/add_contact', methods=['POST'])
def add_contact():
    try:
        database.add_contact(
            user_details['username'],
            request.form['type'],
            request.form['value'],
        )
        flash("contact added")
    except database.UserException as e:
        flash(str(e))
    return redirect(url_for("index"))

"""
search text format:
example:
batman; -tag=sometag; +artist=someone; year=2001; -abc

**Note**: ";" is mandatory for delimiter.

means:
terms must not include: "abc"
metadata must not include: tag: something
metadata must include: artist=someone, year=2001

title or maybe description contains some words similiar to batman.

XHR payload:
{
# allowed values ["all", "movie", "podcast", "song", "tvshow"]
# only movie is implemented
   "type": "all",
   "query":
   {
       "terms": ["+bat", "-something"],
       "metadata": # metadata tags
           {
              "artists": ["+abc", "cde"],
              "tags": ["+a", "-bb"]
           },
       "invaild": ["unreconisable=format=likethis"],
   }
}
in api_get_hint, only terms are processed to reduce query overhead.

api response:
{
   "code": "api response code",
   "errmsg": "api error message describing the code",
   "payload":
      {
          "errors": [], # optional error messages for query. Not implemented
          "items": [<match item 1>, <match item 2>, ...]
      }
}

for movie item
{
    "type": "music", # or movie ...
    "title": "some title",
    "release_year": "1990",
    "similarity": 1
}

"""

@app.route("/api/gethint", methods=['POST'])
def api_get_hint():
    """only search for term not metadata tags"""
    json = request.json
    print(json)
    try:
        mtype = json['type']
        terms = json['query']['term']
    except Exception:
        return jsonify({
            "code": 1000,
            "errmsg": "invaild request"
        })
    try:
        ret = database.movie_fuzzy_search(terms)
    except database.UserException as e:
        return jsonify({
            "code": 1,
            "errmsg": str(e)
        })
    return jsonify({
        "code": 0,
        "errmsg": "success",
        "payload": ret
    })

@app.route("/api/search", methods=['POST'])
def api_fuzzy_search():
    json = request.json
    print(json)
    try:
        mtype = json['type']
        terms = json['query']['term']
        meta = json['query']['metadata']
        limit = json['query']['limit']
        offset = json['query']['offset']
    except Exception:
        return jsonify({
            "code": 1000,
            "errmsg": "invaild request"
        })
    try:
        ret = database.movie_fuzzy_search(terms, meta, limit)
    except database.UserException as e:
        return jsonify({
            "code": 1,
            "errmsg": str(e)
        })
    return jsonify({
        "code": 0,
        "errmsg": "success",
        "payload": ret
    })

DEBUG_API_KEY = secrets.token_hex(10)
if __debug__:
    print("debug api key:", DEBUG_API_KEY)

def debug_api(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        if request.headers['api_key'] != DEBUG_API_KEY:
            return jsonify({'code': 'failed', 'why': 'Unauthorized'})
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return jsonify({"code": "failed", 'why': str(e)})
    return wrapped

@app.route('/debug/api/setuser', methods=['POST'])
@debug_api
def debug_api_setuser():
    database.update_user_credential(
        request.form['username'],
        request.form['password'],
        request.form['issuper'],
    )
    return jsonify({'code': 'success'})
