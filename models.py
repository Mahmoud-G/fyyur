from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime

from config import db
import dateutil.parser
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  # date = dateutil.parser.parse(value)
  if isinstance(value, str):
    date = dateutil.parser.parse(value)
  else:
    date = value
  if format == 'full':
      format="%A %B, %d, %Y at %I:%M%p"
  elif format == 'medium':
      format="%a %b, %d, %y %I:%M%p"
  return date.strftime(format)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# show_table = db.Table('show',
#     db.Column('id', db.Integer, primary_key=True),
#     db.Column('artist_id', db.Integer, db.ForeignKey('artist.id')),
#     db.Column('venue_id', db.Integer, db.ForeignKey('venue.id')),
#     db.Column('start_time', db.DateTime())
# )
class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    # shows = db.relationship('Artist', secondary=show_table, backref=db.backref('venues', lazy=True))
    shows = db.relationship('Show', backref='venue_show', lazy='dynamic')
    genres = db.Column(db.ARRAY(db.String))
    seeking_description = db.Column(db.String)
    seeking_talent = db.Column(db.Boolean, default=False)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    def __repr__(self):
      return '<Venue %r>' % (self.name)

    @hybrid_property
    def upcoming_shows(self):
      # shows = self.shows.with_entities(Show.start_time, Show.artist_id, Artist.name, Artist.image_link.label('artist_image_link')).filter(Show.start_time > datetime.now()).all()
      return self.shows.join(Artist).add_columns(Show.start_time, Show.artist_id, Artist.name.label('artist_name'), Artist.image_link.label('artist_image_link')).filter(Show.start_time > datetime.now()).all()

    @hybrid_property
    def past_shows(self):
      return self.shows.join(Artist).add_columns(Show.start_time, Show.artist_id, Artist.name.label('artist_name'), Artist.image_link.label('artist_image_link')).filter(Show.start_time <= datetime.now()).all()

    # @hybrid_property
    # def shows_count(self):
    #   show_list = self.shows
    #   count = {'upcoming': 0, 'past': 0}
    #   for show in show_list:
    #     if show.start_time > datetime.now():
    #       count['upcoming'] += 1
    #     else:
    #       count['past'] += 1
    #   return count

    @hybrid_property
    def num_upcoming_shows(self):
      return len(self.upcoming_shows)

    @hybrid_property
    def num_past_shows(self):
      # return self.shows_count['past']
      return len(self.past_shows)

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.Unicode))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String)
    shows = db.relationship('Show', backref='artist_show', lazy='dynamic')

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    def __repr__(self):
      return '<Artist %r>' % (self.name)

    # @hybrid_property
    # def shows_count(self):
    #   show_list = self.shows
    #   count = {'upcoming': 0, 'past': 0}
    #   for show in show_list:
    #     if show.start_time > datetime.now():
    #       count['upcoming'] += 1
    #     else:
    #       count['past'] += 1
    #   return count
    @hybrid_property
    def upcoming_shows(self):
      shows = self.shows.join(Venue).add_columns(Show.start_time, Show.venue_id, Venue.name.label('venue_name'),
                                                  Venue.image_link.label('venue_image_link')).filter(
                                                              Show.start_time > datetime.now()).all()
      return shows

    @hybrid_property
    def past_shows(self):
      return self.shows.join(Venue).add_columns(Show.start_time, Show.venue_id, Venue.name.label('venue_name'),
                                                  Venue.image_link.label('venue_image_link')).filter(
        Show.start_time <= datetime.now()).all()

    @hybrid_property
    def num_upcoming_shows(self):
      # return self.shows_count['upcoming']
      return len(self.upcoming_shows)

    @hybrid_property
    def num_past_shows(self):
      # return self.shows_count['past']
      return len(self.past_shows)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
  __tablename__ = 'show'

  id = db.Column(db.Integer, primary_key=True)
  venue_id = db.Column(db.Integer, db.ForeignKey(Venue.id), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey(Artist.id), nullable=False)
  start_time = db.Column(db.DateTime())

  @hybrid_property
  def start_time_pretty(self):
    # return self.shows_count['upcoming']
    return format_datetime(self.start_time)
