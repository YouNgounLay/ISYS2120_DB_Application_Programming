"""
MediaServer Database module.
Contains all interactions between the webapp and the queries to the database.
"""

import configparser
import json
import sys
from contextlib import contextmanager
from typing import Iterable
from modules import pg8000

class UserException(Exception):
    """Used for display information for user,
    should not contain any information about the internal of database"""

class NoResultFound(Exception):
    pass

_db_config = configparser.ConfigParser()
with open('config.ini', "r") as fp:
    _db_config.read_file(fp)


@contextmanager
def get_connection():
    conn = pg8000.connect(
        database=_db_config['DATABASE']['database'],
        user=_db_config['DATABASE']['user'],
        password=_db_config['DATABASE']['password'],
        host=_db_config['DATABASE']['host'],
    )
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

@contextmanager
def get_cursor():
    with get_connection() as conn:
        cur = conn.cursor()
        try:
            yield cur
        finally:
            cur.close()

################################################################################
#   Welcome to the database file, where all the query magic happens.
#   My biggest tip is look at the *week 8 lab*.
#   Important information:
#       - If you're getting issues and getting locked out of your database.
#           You may have reached the maximum number of connections.
#           Why? (You're not closing things!) Be careful!
#       - Check things *carefully*.
#       - There may be better ways to do things, this is just for example
#           purposes
#       - ORDERING MATTERS
#           - Unfortunately to make it easier for everyone, we have to ask that
#               your columns are in order. WATCH YOUR SELECTS!! :)
#   Good luck!
#       And remember to have some fun :D
################################################################################

#####################################################
#   Database Connect
#   (No need to touch
#       (unless the exception is potatoing))
#####################################################

def database_connect():
    """
    Connects to the database using the connection string.
    If 'None' was returned it means there was an issue connecting to
    the database. It would be wise to handle this ;)
    """
    config = configparser.ConfigParser()
    with open('config.ini', "r") as fp:
        config.read_file(fp)
    if 'database' not in config['DATABASE']:
        config['DATABASE']['database'] = config['DATABASE']['user']

    # Create a connection to the database
    return pg8000.connect(database=config['DATABASE']['database'],
                          user=config['DATABASE']['user'],
                          password=config['DATABASE']['password'],
                          host=config['DATABASE']['host'])

##################################################
# Print a SQL string to see how it would insert  #
##################################################

def print_sql_string(inputstring, params=None):
    """
    Prints out a string as a SQL string parameterized assuming all strings
    """

    if params is not None:
        if params != []:
           inputstring = inputstring.replace("%s","'%s'")

    print(inputstring % params)

#####################################################
#   SQL Dictionary Fetch
#   useful for pulling particular items as a dict
#   (No need to touch
#       (unless the exception is potatoing))
#   Expected return:
#       singlerow:  [{col1name:col1value,col2name:col2value, etc.}]
#       multiplerow: [{col1name:col1value,col2name:col2value, etc.},
#           {col1name:col1value,col2name:col2value, etc.},
#           etc.]
#####################################################

def dictfetchall(cursor,sqltext,params=None):
    """ Returns query results as list of dictionaries."""

    result = []
    if (params is None):
        print(sqltext)
    else:
        print("we HAVE PARAMS!")
        print_sql_string(sqltext,params)

    cursor.execute(sqltext,params)
    cols = [a[0].decode("utf-8") for a in cursor.description]
    print(cols)
    returnres = cursor.fetchall()
    for row in returnres:
        result.append({a:b for a,b in zip(cols, row)})
    # cursor.close()
    return result

def dictfetchone(cursor,sqltext,params=None):
    """ Returns query results as list of dictionaries."""
    # cursor = conn.cursor()
    result = []
    cursor.execute(sqltext,params)
    cols = [a[0].decode("utf-8") for a in cursor.description]
    returnres = cursor.fetchone()
    result.append({a:b for a,b in zip(cols, returnres)})
    return result

def _fetch_all(cursor, sqltext, params=None):
    cursor.execute(sqltext, params)

    cols = [a[0].decode("utf-8") for a in cursor.description]
    return [
        {a:b for a,b in zip(cols, row)} for row in cursor.fetchall()
    ]

def _fetch_one(cur, sql, params=None):
    cur.execute(sql, params)
    cols = [a[0].decode("utf-8") for a in cur.description]
    r = cur.fetchone()
    if r:
        return {a:b for a,b in zip(cols, r)}
    raise NoResultFound

#####################################################
#   Query (1)
#   Login
#####################################################

def check_login(username, password) -> dict:
    """Success or die"""
    with get_cursor() as cur:
        try:
            return _fetch_one(
                cur,
                ("select username, issuper from mediaserver.UserAccount where username = %s"
                 " and password = crypt(%s, password);"),
                (username, password)
            )
        except NoResultFound:
            raise UserException("user not exists or password is wrong") from None

#####################################################
#   Is Superuser? -
#   is this required? we can get this from the login information
#####################################################

def ensure_super(username: str):
    with get_cursor() as cur:
        try:
            if not _fetch_one(
                cur,
                """select issuper from mediaserver.useraccount where username = %s""",
                (username, )
            )['issuper']:
                raise UserException("You are not allow to access this page")
        except NoResultFound:
            raise UserException(f"user {username} not exists") from None

def is_superuser(username):
    """
    Check if the user is a superuser.
        - True => Get the departments as a list.
        - False => Return None
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """SELECT isSuper
                 FROM mediaserver.useraccount
                 WHERE username=%s AND isSuper"""
        print("username is: "+username)
        cur.execute(sql, (username))
        r = cur.fetchone()              # Fetch the first row
        print(r)
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error:", sys.exc_info()[0])
        raise
    finally:
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Query (1 b)
#   Get user playlists
#####################################################
def user_playlists(username):
    """Get playlists for current user """
    with get_cursor() as cur:
        sql = """select mc.collection_id, mc.collection_name, count(media_id)
        from mediaserver.MediaCollectionContents as mcc
        natural join mediaserver.MediaCollection as mc
        where username = %s
        group by mc.collection_id;
        """

        return _fetch_all(cur, sql, (username, ))

#####################################################
#   Query (1 c)
#   Get user podcasts
#####################################################
def user_podcast_subscriptions(username):
    """ Get user podcast subscriptions."""
    # We first connect to the db
    with get_cursor() as cur:
        sql = """select pd.podcast_id, pd.podcast_title, pd.podcast_uri,
        pd.podcast_last_updated
        from mediaserver.podcast as pd
        natural join mediaserver.Subscribed_Podcasts as spd
        where username = %s;
        """
        return _fetch_all(cur, sql, (username,))

#####################################################
#   Query (1 c)
#   Get user in progress items
#####################################################
def user_in_progress_items(username):
    """ Get user in progress items that aren't 100% """
    with get_cursor() as cur:
        return _fetch_all(
            cur,
            """
            select
                ums.media_id as media_id,
                ums.progress as progress,
                ums.lastviewed as lastviewed,
                ums.play_count as playcount,
                mi.storage_location as storage_location
            from mediaserver.UserMediaConsumption ums
            natural join mediaserver.MediaItem mi
            where ums.username = %s and progress < 1;
            """,
            (username,)
        )


#####################################################
#   Get all artists
#####################################################
def get_allartists():
    """
    Get all the artists in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """select
            a.artist_id, a.artist_name, count(amd.md_id) as count
        from
            mediaserver.artist a left outer join mediaserver.artistmetadata amd on (a.artist_id=amd.artist_id)
        group by a.artist_id, a.artist_name
        order by a.artist_name;"""

        r = dictfetchall(cur,sql)
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All Artists:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Get all songs
#####################################################
def get_allsongs():
    """
    Get all the songs in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """select
            s.song_id, s.song_title, string_agg(saa.artist_name,',') as artists
        from
            mediaserver.song s left outer join
            (mediaserver.Song_Artists sa join mediaserver.Artist a on (sa.performing_artist_id=a.artist_id)
            ) as saa  on (s.song_id=saa.song_id)
        group by s.song_id, s.song_title
        order by s.song_id"""

        r = dictfetchall(cur,sql)
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All Songs:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Get all podcasts
#####################################################
def get_allpodcasts():
    """
    Get all the podcasts in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:

        # Try executing the SQL and get from the database
        sql = """select
                p.*, pnew.count as count
            from
                mediaserver.podcast p,
                (select
                    p1.podcast_id, count(*) as count
                from
                    mediaserver.podcast p1 left outer join mediaserver.podcastepisode pe1 on (p1.podcast_id=pe1.podcast_id)
                    group by p1.podcast_id) pnew
            where p.podcast_id = pnew.podcast_id;"""

        r = dictfetchall(cur,sql)
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All Podcasts:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None



#####################################################
#   Get all albums
#####################################################
def get_allalbums():
    """
    Get all the Albums in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """select
                a.album_id, a.album_title, anew.count as count, anew.artists
            from
                mediaserver.album a,
                (select
                    a1.album_id, count(distinct as1.song_id) as count, array_to_string(array_agg(distinct ar1.artist_name),',') as artists
                from
                    mediaserver.album a1
                        left outer join mediaserver.album_songs as1 on (a1.album_id=as1.album_id)
                        left outer join mediaserver.song s1 on (as1.song_id=s1.song_id)
                        left outer join mediaserver.Song_Artists sa1 on (s1.song_id=sa1.song_id)
                        left outer join mediaserver.artist ar1 on (sa1.performing_artist_id=ar1.artist_id)
                group by a1.album_id) anew
            where a.album_id = anew.album_id;"""

        r = dictfetchall(cur,sql)
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All Albums:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None



#####################################################
#   Query (3 a,b c)
#   Get all tvshows
#####################################################
def get_alltvshows():
    """
    Get all the TV Shows in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        #########
        # TODO  # --- Done ---
        #########

        #############################################################################
        # Fill in the SQL below with a query to get all tv shows and episode counts #
        #############################################################################
        sql = """
        SELECT tvshow_id,
               tvshow_title,
               count(episode)
        FROM mediaserver.TVShow NATURAL JOIN mediaserver.TVEpisode
        GROUP BY tvshow_id
        ORDER BY tvshow_id asc;
        """

        r = dictfetchall(cur,sql)
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All TV Shows:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Get all movies
#####################################################
def get_allmovies():
    """
    Get all the Movies in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """select
            m.movie_id, m.movie_title, m.release_year, count(mimd.md_id) as count
        from
            mediaserver.movie m left outer join mediaserver.mediaitemmetadata mimd on (m.movie_id = mimd.media_id)
        group by m.movie_id, m.movie_title, m.release_year
        order by movie_id;"""

        r = dictfetchall(cur,sql)
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All Movies:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Get one artist
#####################################################
def get_artist(artist_id):
    """
    Get an artist by their ID in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()


    try:
        # Try executing the SQL and get from the database
        sql = """select *
        from mediaserver.artist a left outer join
            (mediaserver.artistmetadata natural join mediaserver.metadata natural join mediaserver.MetaDataType) amd
        on (a.artist_id=amd.artist_id)
        where a.artist_id=%s"""

        r = dictfetchall(cur,sql,(artist_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Artist with ID: '"+artist_id+"'", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Query (2 a,b,c)
#   Get one song
#####################################################
def get_song(song_id):
    """
    Get a song by their ID in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()


    try:
        #########
        # TODO  #
        #########
        #############################################################################
        # Fill in the SQL below with a query to get all information about a song    #
        # and the artists that performed it                                         #
        #############################################################################
        sql = """SELECT song_title,
                        string_agg(artist_name,',') as artists,
                        length
                 FROM (mediaserver.song natural join mediaserver.song_artists) ssa
                     LEFT OUTER JOIN mediaserver.artist a on (ssa.performing_artist_id = a.artist_id)
                where song_id=%s
                group by song_id, song_title, length"""

        r = dictfetchall(cur,sql,(song_id,))

        print(r)
        print()
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All Songs:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Query (2 d)
#   Get metadata for one song
#####################################################
def get_song_metadata(song_id):
    """
    Get the meta for a song by their ID in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        #########
        # TODO  #
        #########

        #############################################################################
        # Fill in the SQL below with a query to get all metadata about a song       #
        #############################################################################

        sql = """select md_type_name, md_value
        from mediaserver.MediaItemMetaData a natural join
            (mediaserver.MetaData natural join mediaserver.MetaDataType)
        where a.media_id=%s"""

        r = dictfetchall(cur,sql,(song_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting song metadata for ID: "+song_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Query (7 a,b,c,d,e)
#   Get one podcast and return all metadata associated with it
#####################################################
# Get the whole meta of a podcast
def get_podcast_metadata(podcast_id):
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # We need to show the list of episodes of this podcast, and then order them in the order latest to earliest.
        sql = """
        select *
        from (((mediaserver.Podcast
            join
            mediaserver.PodcastMetaData using (podcast_id))
            join
        mediaserver.MetaData using (md_id)) join
        mediaserver.MetaDataType using (md_type_id))
        where podcast_id = %s
        ;
        """
        r = dictfetchall(cur,sql,(podcast_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Podcast with ID: "+podcast_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db



# Main function to get podcast
def get_podcast(podcast_id):
    """
    Get a podcast by their ID in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        #########
        # TODO  #
        #########

        #############################################################################
        # Fill in the SQL below with a query to get all information about a podcast #
        # including all metadata associated with it                                 #
        #############################################################################
        # This returns all the meta data and episodes of the selected podcats

        # We need to show the list of episodes of this podcast, and then order them in the order latest to earliest.
        sql = """
        select podcast_id, podcast_title, podcast_uri, podcast_last_updated
        from mediaserver.Podcast
        where podcast_id = %s;
        """
        r = dictfetchall(cur,sql,(podcast_id,))
        print("return val is:")
        print("--------------------------")
        print(r)
        print("--------------------------")
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r[0]
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Podcast with ID: "+podcast_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Query (7 f)
#   Get all podcast eps for one podcast
#####################################################
def get_all_podcasteps_for_podcast(podcast_id):
    """
    Get all podcast eps for one podcast by their podcast ID in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        #########
        # TODO  #
        #########

        #############################################################################
        # Fill in the SQL below with a query to get all information about all       #
        # podcast episodes in a podcast                                             #
        #############################################################################

        sql = """
        select *
        from mediaserver.Podcast
                full outer join
                mediaserver.podcastepisode using (podcast_id)
        where podcast_id = %s
        order by podcast_episode_published_date DESC;
        """

        r = dictfetchall(cur,sql,(podcast_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All Podcast Episodes for Podcast with ID: "+podcast_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Query (8 a,b,c,d,e,f)
#   Get one podcast ep and associated metadata
#####################################################
def get_podcastep(podcast_id, podcastep_id):
    """
    Get a podcast ep by their ID in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        #########
        # TODO  #
        #########

        #############################################################################
        # Fill in the SQL below with a query to get all information about a         #
        # podcast episodes and it's associated metadata                             #
        #############################################################################
        sql = """
        select *
        from (((mediaserver.PodcastEpisode join mediaserver.AudioMedia using (media_id)) left outer join
            mediaserver.MediaItemMetaData using (media_id)
            left outer join mediaserver.MetaData using (md_id)) join mediaserver.MetaDataType using (md_type_id)) as pd
            where media_id = %s and podcast_id = %s
        ;
        """

        r = dictfetchall(cur,sql,(podcastep_id,podcast_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Podcast Episode with ID: "+podcastep_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Query (5 a,b)
#   Get one album
#####################################################
def get_album(album_id):
    """
    Get an album by their ID in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        #########
        # TODO  #
        #########

        #############################################################################
        # Fill in the SQL below with a query to get all information about an album  #
        # including all relevant metadata                                           #
        #############################################################################
        sql = """SELECT album_title, md_type_name, md_value
                FROM mediaserver.Album LEFT OUTER JOIN (mediaserver.AlbumMetaData NATURAL JOIN mediaserver.MetaData NATURAL JOIN mediaserver.MetaDataType) USING (album_id)
                WHERE album_id=%s
        """



        r = dictfetchall(cur,sql,(album_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Albums with ID: "+album_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Query (5 c)
#   Get all songs for one album
#####################################################
def get_album_songs(album_id):
    """
    Get all songs for an album by the album ID in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        #########
        # TODO  #
        #########

        #############################################################################
        # Fill in the SQL below with a query to get all information about all       #
        # songs in an album, including their artists                                #
        #############################################################################
        sql = """select s.song_id, s.song_title, string_agg(saa.artist_name,',') as artists
                from
                        (mediaserver.album_songs als natural join mediaserver.song s) left outer join
                        (mediaserver.Song_Artists sa join mediaserver.Artist a on (sa.performing_artist_id=a.artist_id)
                        ) as saa  on (s.song_id=saa.song_id)
                where als.album_id=%s
                group by s.song_id, s.song_title, als.track_num
                order by als.track_num
        """

        r = dictfetchall(cur,sql,(album_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Albums songs with ID: "+album_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Query (6)
#   Get all genres for one album
#####################################################
def get_album_genres(album_id):
    """
    Get all genres for an album by the album ID in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        #########
        # TODO  #
        #########

        #############################################################################
        # Fill in the SQL below with a query to get all information about all       #
        # genres in an album (based on all the genres of the songs in that album)   #
        #############################################################################
        sql = """SELECT DISTINCT md_value as songgenres
            FROM (mediaserver.Album NATURAL JOIN mediaserver.Album_Songs)
                        INNER JOIN (mediaserver.MediaItemMetaData natural join mediaserver.MetaData natural join mediaserver.MetaDataType) ON (song_id = media_id)
            where album_id=%s AND md_type_name='song genre'
        """

        r = dictfetchall(cur,sql,(album_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting Albums genres with ID: "+album_id, sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Query (4 a,b)
#   Get one tvshow
#####################################################
def get_tvshow(tvshow_id):
    """
    Get one tvshow in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        #########
        # TODO  # --- Done ---
        #########

        #############################################################################
        # Fill in the SQL below with a query to get all information about a tv show #
        # including all relevant metadata       #
        #############################################################################
        sql = """
            SELECT *
            FROM mediaserver.TVShow LEFT OUTER JOIN
                (mediaserver.TVShowMetaData NATURAL JOIN mediaserver.MetaData
                                            NATURAL JOIN mediaserver.MetaDataType)
                                            USING (tvshow_id)
            WHERE tvshow_id = %s;
        """

        r = dictfetchall(cur,sql,(tvshow_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All TV Shows:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Query (4 c)
#   Get all tv show episodes for one tv show
#####################################################
def get_all_tvshoweps_for_tvshow(tvshow_id):
    """
    Get all tvshow episodes for one tv show in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        #########
        # TODO  # --- Done ---
        #########

        #############################################################################
        # Fill in the SQL below with a query to get all information about all       #
        # tv episodes in a tv show                                                  #
        #############################################################################
        sql = """
        SELECT media_id,
               tvshow_episode_title,
               season,
               episode,
               air_date
        FROM mediaserver.TVEpisode
        WHERE tvshow_id = %s
        ORDER BY season, episode


        """

        r = dictfetchall(cur,sql,(tvshow_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All TV Shows:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Get one tvshow episode
#####################################################
def get_tvshowep(tvshowep_id):
    """
    Get one tvshow episode in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """select *
        from mediaserver.TVEpisode te left outer join
            (mediaserver.mediaitemmetadata natural join mediaserver.metadata natural join mediaserver.MetaDataType) temd
            on (te.media_id=temd.media_id)
        where te.media_id = %s"""

        r = dictfetchall(cur,sql,(tvshowep_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All TV Shows:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################

#   Get one movie
#####################################################
def get_movie(movie_id):
    """
    Get one movie in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """select *
        from mediaserver.movie m left outer join
            (mediaserver.mediaitemmetadata natural join mediaserver.metadata natural join mediaserver.MetaDataType) mmd
        on (m.movie_id=mmd.media_id)
        where m.movie_id=%s;"""

        r = dictfetchall(cur,sql,(movie_id,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All Movies:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Find all matching tvshows
#####################################################
def find_matchingtvshows(searchterm):
    """
    Get all the matching TV Shows in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """
            select
                t.*, tnew.count as count
            from
                mediaserver.tvshow t,
                (select
                    t1.tvshow_id, count(te1.media_id) as count
                from
                    mediaserver.tvshow t1 left outer join mediaserver.TVEpisode te1 on (t1.tvshow_id=te1.tvshow_id)
                    group by t1.tvshow_id) tnew
            where t.tvshow_id = tnew.tvshow_id and lower(tvshow_title) ~ lower(%s)
            order by t.tvshow_id;"""

        r = dictfetchall(cur,sql,(searchterm,))
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error getting All TV Shows:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Query (10)
#   Find all matching Movies
#####################################################
def find_matchingmovies(searchterm):
    """
    Get all the matching Movies in your media server
    """

    try:
        conn = database_connect()
        cur = conn.cursor()

        #Query
        sql = """
            select m.* from mediaserver.movie m
            where lower(m.movie_title) ~ lower(%s)
            order by m.movie_id;
        """

        return dictfetchall(cur, sql, (searchterm,))
    finally:
        cur.close()
        conn.close()



#####################################################
#   Add a new Movie
#####################################################
def add_movie_to_db(title,release_year,description,storage_location,genre):
    """
    Add a new Movie to your media server
    """
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """
        SELECT
            mediaserver.addMovie(
                %s,%s,%s,%s,%s);

        """

        cur.execute(sql,(storage_location,description,title,release_year,genre))
        conn.commit()                   # Commit the transaction
        r = cur.fetchone()
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error adding a movie:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None

#####################################################
#   Query (9)
#   Add a new Song
#####################################################
def add_song_to_db(*song_params):
    """
    Get all the matching Movies in your media server
    """
    #########
    # TODO  #
    #########

    #############################################################################
    # Fill in the Function  with a query and management for how to add a new    #
    # song to your media server. Make sure you manage all constraints           #
    #############################################################################
    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()

    try:
        # Try executing the SQL and get from the database
        sql = """
        SELECT
            mediaserver.addSong(
                %s,%s,%s,%s,%s,%s,%s);
        """
        location = song_params[3]
        desc = song_params[2]
        title = song_params[0]
        length = song_params[1]
        genre = song_params[4]
        artwork = song_params[5]
        artist = song_params[6]

        cur.execute(sql,(location, desc, title, length, genre, artwork, artist))
        conn.commit()                   # Commit the transaction
        r = cur.fetchone()
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error adding a song:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None




#####################################################
#   Get last Movie
#####################################################
def get_last_movie():
    """
    Get all the latest entered movie in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """
        select max(movie_id) as movie_id from mediaserver.movie"""

        r = dictfetchone(cur,sql)
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error adding a movie:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None


#####################################################
#   Get last Song
#####################################################
def get_last_song():
    """
    Get all the latest entered movie in your media server
    """

    conn = database_connect()
    if(conn is None):
        return None
    cur = conn.cursor()
    try:
        # Try executing the SQL and get from the database
        sql = """
        select max(song_id) as song_id from mediaserver.Song"""

        r = dictfetchone(cur,sql)
        print("return val is:")
        print(r)
        cur.close()                     # Close the cursor
        conn.close()                    # Close the connection to the db
        return r
    except:
        # If there were any errors, return a NULL row printing an error to the debug
        print("Unexpected error adding a song:", sys.exc_info()[0])
        raise
    cur.close()                     # Close the cursor
    conn.close()                    # Close the connection to the db
    return None



#  FOR MARKING PURPOSES ONLY
#  DO NOT CHANGE

def to_json(fn_name, ret_val):
    """
    TO_JSON used for marking; Gives the function name and the
    return value in JSON.
    """
    return {'function': fn_name, 'res': json.dumps(ret_val)}

# =================================================================
# =================================================================
# new functions

def signup(user: str, password: str, is_super: bool=False):
    with get_cursor() as cur:
        try:
            cur.execute("select mediaserver.storeSecurePassword(%s, %s);", (user, password))
            cur.execute("update mediaserver.UserAccount set issuper = %s where username = %s;",
                        (is_super, user))
        except pg8000.core.ProgrammingError as e:
            if "duplicate key" in str(e):
                raise UserException("User exists") from None
            raise

def update_user_credential(user: str, password: str, is_super: bool=False):
    with get_cursor() as cur:
        cur.execute(
            """
            update
                mediaserver.UserAccount
            set
                password = public.crypt(%s, public.gen_salt('bf', 8)),
                issuper = %s
            where
                username = %s; """,
            (password, is_super, user)
        )

def get_user_contacts(user: str):
    with get_cursor() as cur:
        return _fetch_all(
            cur,
            """
            select
                ct.contact_type_name as type,
                cm.contact_type_value as value
            from
                mediaserver.ContactMethod as cm
            natural join
                mediaserver.ContactType as ct
            where
                username = %s;
            """,
            (user,)
        )

def __get_contact_type_id_mapping(cur):
    """The ContactType table make no sense"""
    ds = _fetch_all(
        cur,
        """select contact_type_name as n, contact_type_id as id from mediaserver.ContactType;"""
    )
    return {d['n']: d['id'] for d in ds}

def delete_contact(user: str, contact_type: str, value: str):
    with get_cursor() as cur:
        try:
            ctid = __get_contact_type_id_mapping(cur)[contact_type]
        except KeyError:
            raise UserException("Invaild contact type")
        cur.execute(
            """delete from mediaserver.ContactMethod
            where (
                username = %s and
                contact_type_value = %s and
                contact_type_id = %s
            );
            """,
            (user, value, ctid)
        )
        return


def add_contact(user: str, contact_type: str, value: str):
    with get_cursor() as cur:
        try:
            ctid = __get_contact_type_id_mapping(cur)[contact_type]
        except KeyError:
            raise UserException("Invaild contact type")
        cur.execute(
            """
            insert into mediaserver.ContactMethod
            (username, contact_type_value, contact_type_id)
            values
                (%s, %s, %s);
            """,
            (user, value, ctid)
        )

def __get_metadata_type_id_mapping(cur):
    ds = _fetch_all(
        cur,
        """select md_type_name as n, md_type_id as id from mediaserver.MetaDataType;"""
    )
    return {d['n']: d['id'] for d in ds}

def __build_in_clause(item, n_values, not_in=False):
    return "({} {}in ({}))".format(item, "not " if not_in else "", ",".join("%s" for _ in range(n_values)))

def __build_where_clause(and_where, or_where, and_where_params, or_where_params):
    and_where.append("({})".format(" or ".join(or_where)))
    if and_where:
        return "where ({})".format(" and ".join(and_where)), [*and_where_params, *or_where_params]
    return "", []

def __movie_metadata_subquery_builder(md_id, md_values, disallow=False):
    and_where = ["mtm.media_id = q1.movie_id", "mt.md_type_id = %s"]
    or_where = []

    not_include = []
    could_include = []

    for v in md_values:
        if v[0] == '-':
            if len(v) == 1:
                continue
            not_include.append(v[1:])
        else:
            could_include.append(v)

    if len(could_include) > 0:
        or_where.append(
            __build_in_clause("md_value", len(could_include))
        )
    if len(not_include) > 0:
        and_where.append(
            __build_in_clause("md_value", len(not_include), True)
        )

    where_clause, where_params = __build_where_clause(
        and_where,
        or_where,
        (md_id, *not_include),
        could_include
    )
    sql = """((select count(*) from mediaserver.metadata as mt natural
    join mediaserver.mediaitemmetadata as mtm {}) != 0)""".format(where_clause)
    return sql, where_params

def movie_fuzzy_search(terms: Iterable[str], metadata=[], limit: int=10):
    with get_cursor() as cur:
        md_mapping = __get_metadata_type_id_mapping(cur)

        where_and = []
        where_and_param = []

        words = []
        for t in filter(lambda t: len(t) >= 2, terms):
            if t[0] == '-':
                if len(t) == 1:
                    continue
                t = t[1:]
                where_and.append(f"lower(movie_title) != lower(%s)")
                where_and_param.append(t)
            else:
                words.append(t)

        q2_where_and = ["similarity >= 0.7"]
        q2_where_and_param = []

        for mk in metadata:
            if mk[0] == '-':
                if len(mk) == 1:
                    continue
                mk = mk[1:]
                disallow=True
            else:
                disallow=False

            try:
                sql, param = __movie_metadata_subquery_builder(md_mapping[mk], metadata[mk], disallow)
                q2_where_and.append(sql)
                q2_where_and_param.extend(param)
            except KeyError:
                raise UserException("invaild metadata type")

        where_clause = "where(({where_and_clause}))".format(
            where_and_clause=" and ".join(where_and) or "true",
        )
        q2_where_clause = "where({where_and_clause})".format(
            where_and_clause=" and ".join(q2_where_and) or "true",
        )
        print(words)
        if words:
            select_stmt = "select movie_id, movie_title, release_year, total_similarity(title_words, %s::varchar[]) as similarity"
        else:
            select_stmt = "select movie_id, movie_title, release_year, 1 as similarity"

        sql = """select * from (
            {select_stmt}
            from mediaserver.movie as t
            {where_clause}
            order by similarity desc
            limit %s
        ) as q1 {q2_where_clause};""".format(
            select_stmt=select_stmt,
            where_clause=where_clause,
            q2_where_clause=q2_where_clause,
        )
        if words:
            print(sql % (words, *where_and_param, limit, *q2_where_and_param))
        else:
            print(sql % (*where_and_param, limit, *q2_where_and_param))
        if words:
            params = (words, *where_and_param, limit, *q2_where_and_param)
        else:
            params = (*where_and_param, limit, *q2_where_and_param)
        return _fetch_all(cur, sql, params)
