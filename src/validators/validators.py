import logging

import sqlalchemy
from sqlalchemy.orm.query import Query

from db.models import Vocabulary
from tools.escape_markdown import escape_markdown
from tools.read_data import app_data
