from google.appengine.ext import ndb

class InstaUser(ndb.Model):
	user = ndb.UserProperty()
	username = ndb.StringProperty()
	profile_image = ndb.BlobKeyProperty()
	following = ndb.StringProperty(repeated=True)
	followers = ndb.StringProperty(repeated=True)
	posts = ndb.KeyProperty(kind="Post", repeated=True)
	
class Post(ndb.Model):
	posted_by = ndb.StringProperty()
	post_image = ndb.BlobKeyProperty()
	caption = ndb.StringProperty()
	date = ndb.DateTimeProperty()
	
class Comment(ndb.Model):
	post = ndb.KeyProperty(kind='Post')
	commented_by = ndb.StringProperty()
	user_comment = ndb.StringProperty()
	date = ndb.DateTimeProperty()