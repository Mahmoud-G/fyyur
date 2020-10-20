#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import sys



from flask import (Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify)
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler

from models import (Venue, Artist, Show, format_datetime)

from forms import (VenueForm, ArtistForm, ShowForm)
from config import db
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = db.init_app(app)

# TODO: connect to a local postgresql database

migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  query = Venue.query.with_entities(Venue.city, Venue.state).distinct()

  result = []
  for q in query:
    result.append({"city": q.city,
                    "state": q.state,
                    "venues": Venue.query.filter(Venue.city == q.city).all()})

  return render_template('pages/venues.html', areas=result);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  # get the search word from the request
  search_term = request.form.get('search_term', '').lower()



# Need your help to
  # qry = Venue.query.outerjoin(Venue.shows).filter(Venue.name.ilike('%' + q + '%')).with_entities(
  #                     func.count('venue_id').label("num_upcoming_shows2"),
  #                     func.sum(func.IF('start_time', 1, 0)).label('num_upcoming_shows'),
  #                     Venue.name.label("name"),
  #                     Venue.id.label("id"),
  #                     ).group_by(Venue.id)
  # print(qry.all())
  # print(qry)

  # query = (select([Venue.id,Venue.name]).select_from(Venue.outerjoin(Venue.shows)))

  # raw sql method
  # Kindly I need your help to convert this raw sql to ORM
  # sql = '''
  #             SELECT
  #                 venue.ID AS ID,
  #                 venue.NAME AS NAME,
  #                 SUM ( CASE WHEN show_1.start_time >= CURRENT_TIMESTAMP THEN 1 ELSE 0 END ) AS num_upcoming_shows
  #
  #             FROM
  #                 venue
  #                 LEFT OUTER JOIN  SHOW AS show_1 ON venue.ID = show_1.venue_id
  #             WHERE
  #                 LOWER ( venue.NAME ) LIKE  CONCAT('%', :word, '%')
  #             GROUP BY
  #                 venue.ID
  # '''
  # results = db.engine.execute(text(sql), {"word": q})
  # # data = json.dumps([dict(r) for r in results])
  # data = [dict(r) for r in results]
  # print(data)
  #
  # response = {
  #   "count": data.__len__(),
  #   "data": data
  # }

  query = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
  response = {
    "count": len(query),
    "data": query
  }


  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  query = Venue.query.get(venue_id)

  return render_template('pages/show_venue.html', venue=query)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  error = False
  body = {}
  try:
    # print(request.form.getlist('genres'))
    # print(request.form)
    new_venue = Venue(name=request.form.get('name'),
                      city=request.form.get('city'),
                      state=request.form.get('state'),
                      address=request.form.get('address'),
                      phone=request.form.get('phone'),
                      image_link=request.form.get('image_link'),
                      facebook_link=request.form.get('facebook_link'),
                      website=request.form.get('website'),
                      genres=request.form.getlist('genres'),
                      seeking_talent=request.form.get('seeking_talent'),
                      seeking_description=request.form.get('seeking_description'))

    db.session.add(new_venue)
    db.session.commit()

    # on successful db insert, flash success
    flash('Venue ' + request.form.get('name') + ' was successfully listed!')
  except():
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    db.session.rollback()
    error = True
    print(sys.exc_info)
    flash('An error occurred. Venue ' + request.form.get('name') + ' could not be listed.')

  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    return render_template('pages/home.html', data=jsonify(body))


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  error = False
  try:

    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except():
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    return jsonify({'success': True})
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  # return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  query = Artist.query.all()

  return render_template('pages/artists.html', artists=query)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  query = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()

  response = {
    "count": len(query),
    "data": query
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  query = Artist.query.get(artist_id)

  return render_template('pages/show_artist.html', artist=query)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  # TODO: populate form with fields from artist with ID <artist_id>

  query = Artist.query.get(artist_id)

  form.name.data = query.name
  form.city.data = query.city
  form.state.data = query.state
  form.phone.data = query.phone
  form.genres.data = query.genres
  form.facebook_link.data = query.facebook_link

  return render_template('forms/edit_artist.html', form=form, artist=query)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  query = Artist.query.get(artist_id)
  try:
    # print(request.form.getlist('genres'))
    # print(request.form)
    error = False

    query.name                = request.form.get('name')
    query.city                = request.form.get('city')
    query.state               = request.form.get('state')
    query.phone               = request.form.get('phone')
    query.image_link          = request.form.get('image_link')
    query.facebook_link       = request.form.get('facebook_link')
    query.website             = request.form.get('website')
    query.genres              = request.form.getlist('genres')
    query.seeking_venue       = request.form.get('seeking_venue')
    query.seeking_description = request.form.get('seeking_description')

    db.session.commit()

    # on successful db insert, flash success
    flash('Artist ' + request.form.get('name') + ' was successfully listed!')
  except():
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    db.session.rollback()
    error = True
    print(sys.exc_info)
    flash('An error occurred. Artist ' + request.form.get('name') + ' could not be listed.')

  finally:
    db.session.close()
  if error:
    abort(500)
  else:

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  form = VenueForm()
  # TODO: populate form with values from venue with ID <venue_id>

  query = Venue.query.get(venue_id)

  form.name.data = query.name
  form.city.data = query.city
  form.state.data = query.state
  form.address.data = query.address
  form.phone.data = query.phone
  form.image_link.data = query.image_link
  form.genres.data = query.genres
  form.facebook_link.data = query.facebook_link


  return render_template('forms/edit_venue.html', form=form, venue=query)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  query = Venue.query.get(venue_id)
  error = False
  body = {}
  try:
    # print(request.form.getlist('genres'))
    # print(request.form)
    query.name                = request.form.get('name')
    query.city                = request.form.get('city')
    query.state               = request.form.get('state')
    query.address             = request.form.get('address')
    query.phone               = request.form.get('phone')
    query.image_link          = request.form.get('image_link')
    query.facebook_link       = request.form.get('facebook_link')
    query.website             = request.form.get('website')
    query.genres              = request.form.getlist('genres')
    query.seeking_talent      = request.form.get('seeking_talent')
    query.seeking_description = request.form.get('seeking_description')

    db.session.commit()

    # on successful db insert, flash success
    flash('Venue ' + request.form.get('name') + ' was successfully listed!')
  except():
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    db.session.rollback()
    error = True
    print(sys.exc_info)
    flash('An error occurred. Venue ' + request.form.get('name') + ' could not be listed.')

  finally:
    db.session.close()
  if error:
    abort(500)
  else:
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

  error = False
  body = {}
  try:
    # print(request.form.getlist('genres'))
    # print(request.form)
    new_artist = Artist(name=request.form.get('name'),
                      city=request.form.get('city'),
                      state=request.form.get('state'),
                      phone=request.form.get('phone'),
                      image_link=request.form.get('image_link'),
                      facebook_link=request.form.get('facebook_link'),
                      website=request.form.get('website'),
                      genres=request.form.getlist('genres'),
                      seeking_venue=request.form.get('seeking_venue'),
                      seeking_description=request.form.get('seeking_description'))
    db.session.add(new_artist)
    db.session.commit()

    # on successful db insert, flash success
    flash('Artist ' + request.form.get('name') + ' was successfully listed!')
  except():
    # TODO: on unsuccessful db insert, flash an error instead.
    db.session.rollback()
    error = True
    print(sys.exc_info)
    flash('An error occurred. Artist ' + request.form.get('name') + ' could not be listed.')

  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  query = Show.query.join(Artist).join(Venue).add_columns(Show.start_time,
                                                          Show.venue_id, Venue.name.label('venue_name'),
                                                          Show.artist_id, Artist.name.label('artist_name'),
                                                          Artist.image_link.label('artist_image_link')).all()
  return render_template('pages/shows.html', shows=query)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  body = {}
  try:
    # print(request.form.getlist('genres'))
    # print(request.form)
    new_show = Show(venue_id=request.form.get('venue_id'),
                    artist_id=request.form.get('artist_id'),
                    start_time=request.form.get('start_time'))
    db.session.add(new_show)
    db.session.commit()

    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except():
    # TODO: on unsuccessful db insert, flash an error instead.
    db.session.rollback()
    error = True
    print(sys.exc_info)
    flash('An error occurred. Show could not be listed.')

  finally:
    db.session.close()
  if error:
    abort(500)
  else:
    return render_template('pages/home.html')


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
