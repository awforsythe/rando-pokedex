import os

rootdir = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Enable debug mode by default, for
DEBUG = True

# An environment variable called 'PORT' will override this setting
#PORT = 5000

# Use sqlite database for development.
# PostgreSQL is recommended for production; in which case URI should be:
# - postgres://<user>:<password>@<host>/<database>
SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % os.path.join(rootdir, 'pokemon.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Settings for hacky forwarding, with a secret key for validation. If running
# on the internet, set API_SECRET and enable VALIDATE_POST_REQUESTS to serve as
# a mirror. In that case, the local instance should have the same API_SECRET,
# and should enable FORWARD_POST_REQUESTS, with FORWARD_TO set to the URL of
# the internet mirror.
#
# These settings should be configured in instance/config.py, not in this file.
API_SECRET = ''
VALIDATE_POST_REQUESTS = False
FORWARD_POST_REQUESTS = False
FORWARD_TO = ''

# If a Twitch username is set, the site will display buttons linking to that
# user's Twitch page. The game description, if set, will appear in the info
# dialog: for example, 'Pokémon White Randomizer' or 'Pokémon Black 2 Nuzlocke'
TWITCH_USERNAME = ''
GAME_DESCRIPTION = ''
