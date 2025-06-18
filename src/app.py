import os
from flask import (
    Flask, render_template, request, redirect, url_for, session, flash, send_from_directory, g
)
from werkzeug.utils import secure_filename

from database import get_db, close_db, init_db, query_db, execute_db