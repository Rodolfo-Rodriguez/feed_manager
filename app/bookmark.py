import os
import time

from .models import Bookmark
from . import CONFIG

################################################################################################################################################################
# Bookmark Manager 
################################################################################################################################################################

class BookmarkManager:

  bookmark_list = [] 

  def __init__(self):
    self.bookmark_list = Bookmark.query.order_by(Bookmark.priority).all() 

  def update_bookmark_list(self):

    self.bookmark_list = Bookmark.query.order_by(Bookmark.priority).all() 

