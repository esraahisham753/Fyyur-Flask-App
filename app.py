#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import Artist, Venue, Show, app, db
from flask import render_template, redirect, url_for, request, jsonify, flash
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#



# TODO: connect to a local postgresql database


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

def area_exists(areas, area):
  for a in areas:
    if(a['city'] == area['city']) and (a['state'] == area['state']):
      a['venues'].append(area['venues'][0])
      return True
  return False

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  all_venues = Venue.query.all()
  areas = []
  for venue in all_venues:
    print(venue.city)
    area = {'city':'', 'state':'', 'venues':[]}
    area['city'] = venue.city
    area['state'] = venue.state
    area['venues'].append(venue)
    if area_exists(areas, area):
      continue
    else:
      areas.append(area)

  return render_template('pages/venues.html', areas=areas)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  keyword = request.form.to_dict()['search_term']
  venues_result = Venue.query.filter(Venue.name.ilike(f'%{keyword}%')).all()
  response={
    "count": len(venues_result),
    "data": venues_result
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  shows = venue.shows
  data1={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": venue.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  current_time = datetime.now()
  for show in shows:
    show_dict = {'artist_id': show.artist, 'artist_name': Artist.query.get(show.artist).name, 'artist_image_link': Artist.query.get(show.artist).image_link, 'start_time': str(show.start_time)}
    if show.start_time < current_time:
      data1['past_shows'].append(show_dict)
    else:
      data1['upcoming_shows'].append(show_dict)
  data1['past_shows_count'] = len(data1['past_shows'])
  data1['upcoming_shows_count'] = len(data1['upcoming_shows'])
  data = data1
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  new_venue_dict = request.form.to_dict()
  new_venue = Venue(
    name=new_venue_dict['name'],
    city=new_venue_dict['city'],
    state=new_venue_dict['state'],
    address=new_venue_dict['address'],
    phone=new_venue_dict['phone'],
    image_link=new_venue_dict['image_link'],
    facebook_link=new_venue_dict['facebook_link'],
    genres=','.join(request.form.getlist('genres')),
    website_link='',
    seeking=False
  )
  try:
    db.session.add(new_venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + new_venue_dict['name'] + ' could not be listed.')
  finally:
    return render_template('pages/home.html')

  # TODO: modify data to be the data object returned from db insertion
  
  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue = Venue.query.get(venue_id)
  succeed = False
  try:
    for show in venue.shows:
      db.session.delete(show)
    db.session.delete(venue)
    db.session.commit()
    succeed = True
    flash('Venue ' + venue.name + ' was successfully Deleted!')
  except:
    db.session.rollback()
    flash('Venue ' + venue.name + ' cannot be Deleted!')
  finally:
    return jsonify({
    "Succeed": succeed
  })
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data= Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  response={
    "count": len(artists),
    "data": artists
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.get(artist_id)
  shows = artist.shows
  data1={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": "",
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": artist.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  current_time = datetime.now()
  for show in shows:
    show_dict = {'venue_id': show.venue, 'venue_name': Venue.query.get(show.venue).name, 'venue_image_link': Venue.query.get(show.venue).image_link, 'start_time': str(show.start_time)}
    if show.start_time < current_time:
      data1['past_shows'].append(show_dict)
    else:
      data1['upcoming_shows'].append(show_dict)
  data1['past_shows_count'] = len(data1['past_shows'])
  data1['upcoming_shows_count'] = len(data1['upcoming_shows'])
  return render_template('pages/show_artist.html', artist=data1)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  form.name.data = artist.name
  form.genres.data = artist.genres.split(',')
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  edit_artist_dict = request.form.to_dict()
  genres_list = request.form.getlist('genres')
  artist = Artist.query.get(artist_id)
  artist.name = edit_artist_dict['name']
  artist.city = edit_artist_dict['city']
  artist.state = edit_artist_dict['state']
  artist.phone = edit_artist_dict['phone']
  artist.genres = ','.join(genres_list)
  artist.facebook_link = edit_artist_dict['facebook_link']
  artist.image_link = edit_artist_dict['image_link']
  db.session.commit()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  # TODO: populate form with values from venue with ID <venue_id>
  form.name.data = venue.name
  form.genres.data = venue.genres.split(',')
  form.address.data = venue.address
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  edit_venue_dict = request.form.to_dict()
  genres_list = request.form.getlist('genres')
  venue = Venue.query.get(venue_id)
  venue.name = edit_venue_dict['name']
  venue.city = edit_venue_dict['city']
  venue.state = edit_venue_dict['state']
  venue.address = edit_venue_dict['address']
  venue.phone = edit_venue_dict['phone']
  venue.genres = ','.join(genres_list)
  venue.facebook_link = edit_venue_dict['facebook_link']
  venue.image_link = edit_venue_dict['image_link']
  db.session.commit()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  new_artist_dict = request.form.to_dict()
  new_artist = Artist(
    name=new_artist_dict['name'],
    city=new_artist_dict['city'],
    state=new_artist_dict['state'],
    phone=new_artist_dict['phone'],
    image_link=new_artist_dict['image_link'],
    facebook_link=new_artist_dict['facebook_link'],
    genres=','.join(request.form.getlist('genres')),
    website_link='',
    seeking=False
  )
  try:
    db.session.add(new_artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    flash('Artist ' + request.form['name'] + ' cannot be listed!')
  finally:
    return render_template('pages/home.html')
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.all()
  data = []
  for show in shows:
    item = {
      'venue_id': show.venue,
      'venue_name': Venue.query.get(show.venue).name,
      'artist_id': show.artist, 
      'artist_name': Artist.query.get(show.artist).name,
      'artist_image_link': Artist.query.get(show.artist).image_link,
      'start_time': str(show.start_time)}
    data.append(item)
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  new_show_dict = request.form.to_dict()
  new_show = Show(
    artist=new_show_dict['artist_id'],
    venue=new_show_dict['venue_id'],
    start_time=new_show_dict['start_time']
  )
  try:
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('Show cannot be listed!')
  finally:
    return render_template('pages/home.html')
  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
