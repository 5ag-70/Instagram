import webapp2
import jinja2
import os
import time
from google.appengine.api import users
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers
from models import InstaUser, Post, Comment
from datetime import datetime

class InstaLoginPage(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if not user:
			url = users.create_login_url(self.request.uri)
			template_values = {
				'url':url,
			}
			template = JINJA_ENVIROMENT.get_template('insta-login.html')
			self.response.write(template.render(template_values))
		else:
			self.redirect('/timeline')
	def post(self):
		self.redirect('/')
			
class PostPage(webapp2.RequestHandler):
	def get(self, key):
		current_user = users.get_current_user()
		if not current_user:
			url = users.create_login_url(self.request.uri)
			template_values = {
				'url':url,
			}
			template = JINJA_ENVIROMENT.get_template('insta-login.html')
			self.response.write(template.render(template_values))
		else:
			ndb_post_key = ndb.Key(urlsafe = key)
			post = ndb_post_key.get()			
			logout_url = users.create_logout_url(self.request.uri)
			comments = Comment.query(Comment.post == ndb_post_key).order(-Comment.date).fetch()
			upload_url = blobstore.create_upload_url('/upload_photo')
			template_values = {
				'upload_url':upload_url,
				'logout_url':logout_url,
				'current_user':current_user,
				'comments':comments,
				'post':post,
			}
			template = JINJA_ENVIROMENT.get_template('post.html')
			self.response.write(template.render(template_values))
			
class ProfilePage(webapp2.RequestHandler):
	def get(self, user_name):
		current_user = users.get_current_user()
		if not current_user:
			url = users.create_login_url(self.request.uri)
			template_values = {
				'url':url,
			}
			template = JINJA_ENVIROMENT.get_template('insta-login.html')
			self.response.write(template.render(template_values))
		else:
			user_profile = InstaUser.query(InstaUser.username == user_name).get()
			followers = len(user_profile.followers)
			following = len(user_profile.following)				
			posts = Post.query(Post.posted_by == user_profile.username).fetch()
			number_of_posts = len(posts)
			logout_url = users.create_logout_url(self.request.uri)
			upload_url = blobstore.create_upload_url('/upload_photo')
			insta_users = InstaUser.query().fetch()
			user_names = []
			for insta_user in insta_users:
				user_names.append(str(insta_user.username))
			template_values = {
				'upload_url':upload_url,
				'logout_url':logout_url,
				'following':following,
				'followers':followers,
				'user_profile':user_profile,
				'current_user':current_user,
				'posts':posts,
				'number_of_posts':number_of_posts,
				'user_names':user_names,
			}
			template = JINJA_ENVIROMENT.get_template('profile.html')
			self.response.write(template.render(template_values))
			
class TimeLinePage(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if not user:
			url = users.create_login_url(self.request.uri)
			template_values = {
				'url':url,
			}
			template = JINJA_ENVIROMENT.get_template('insta-login.html')
			self.response.write(template.render(template_values))
		else:
			ndb_user_key = ndb.Key(InstaUser, user.email())
			logged_user = ndb_user_key.get()
			user_profile = logged_user
			first_time_login = False
			if logged_user is None:
				new_user = InstaUser()
				new_user.key = ndb_user_key
				new_user.user = user
				new_user.put()
				user_profile = new_user
			username = user_profile.username
			if not username:
				first_time_login = True
			else:
				first_time_login = False
			followings = []
			following_keys = user_profile.following
			for following_key in following_keys:
				ndb_following_key = ndb.Key(InstaUser, following_key)
				following = ndb_following_key.get()
				followings.append(following.username)
			if not followings:
				posts = Post.query(Post.posted_by==user_profile.username).order(-Post.date).fetch(50)
			else:
				posts = Post.query(ndb.OR(Post.posted_by==user_profile.username,Post.posted_by.IN(followings))).order(-Post.date).fetch(50)
			comments = Comment.query().order(-Comment.date).fetch()
			logout_url = users.create_logout_url(self.request.uri)
			insta_users = InstaUser.query().fetch()
			upload_url = blobstore.create_upload_url('/upload_photo')
			user_names = []
			for insta_user in insta_users:
				user_names.append(str(insta_user.username))
			template_values = {
				'upload_url':upload_url,
				'logout_url':logout_url,
				'user_profile':user_profile,
				'current_user':user,
				'users':insta_users,
				'posts':posts,
				'comments':comments,
				'user_names':user_names,
				'error':''
			}
			if first_time_login:
				template = JINJA_ENVIROMENT.get_template('username.html')
				self.response.write(template.render(template_values))
			else:
				template = JINJA_ENVIROMENT.get_template('timeline.html')
				self.response.write(template.render(template_values))
				
				
class UserName(webapp2.RequestHandler):
	def post(self):
		user = users.get_current_user()
		if not user:
			url = users.create_login_url(self.request.uri)
			template_values = {
				'url':url,
			}
			template = JINJA_ENVIROMENT.get_template('insta-login.html')
			self.response.write(template.render(template_values))
		else:
			request = self.request.POST
			new_name = request['username']
			insta_user = InstaUser.query(InstaUser.username == new_name).get()
			if not insta_user:
				insta_user = InstaUser.query(InstaUser.user == user).get()
				insta_user.username = new_name
				insta_user.put()
				self.redirect('/')
			else:
				template_values = {
					'error':'name already exist',
				}
				template = JINJA_ENVIROMENT.get_template('username.html')
				self.response.write(template.render(template_values))
			
class Follow(webapp2.RequestHandler):
	def get(self, victim_email):
		user = users.get_current_user()
		if not user:
			url = users.create_login_url(self.request.uri)
			template_values = {
				'url':url,
			}
			template = JINJA_ENVIROMENT.get_template('insta-login.html')
			self.response.write(template.render(template_values))
		else:
			ndb_user_key = ndb.Key(InstaUser, user.email())
			logged_user = ndb_user_key.get()
			ndb_victim_key = ndb.Key(InstaUser, victim_email)
			victim_user = ndb_victim_key.get()
			victim_user.followers.append(user.email())
			logged_user.following.append(victim_email)
			victim_user.put()
			logged_user.put()
			time.sleep(0.1)
			self.redirect('/profile/'+victim_user.username)

class Unfollow(webapp2.RequestHandler):
	def get(self, victim_email):
		user = users.get_current_user()
		if not user:
			url = users.create_login_url(self.request.uri)
			template_values = {
				'url':url,
			}
			template = JINJA_ENVIROMENT.get_template('insta-login.html')
			self.response.write(template.render(template_values))
		else:
			ndb_user_key = ndb.Key(InstaUser, user.email())
			logged_user = ndb_user_key.get()
			ndb_victim_key = ndb.Key(InstaUser, victim_email)
			victim_user = ndb_victim_key.get()
			victim_user.followers.remove(user.email())
			logged_user.following.remove(victim_email)
			victim_user.put()
			logged_user.put()
			time.sleep(0.1)
			self.redirect('/profile/'+victim_user.username)

class Followers(webapp2.RequestHandler):
	def get(self, victim_email):
		user = users.get_current_user()
		if not user:
			url = users.create_login_url(self.request.uri)
			template_values = {
				'url':url,
			}
			template = JINJA_ENVIROMENT.get_template('insta-login.html')
			self.response.write(template.render(template_values))
		else:
			ndb_victim_key = ndb.Key(InstaUser, victim_email)
			victim_user = ndb_victim_key.get()
			followers = victim_user.followers
			insta_users = InstaUser.query().fetch()
			user_names = []
			for insta_user in insta_users:
				user_names.append(str(insta_user.username))
			template_values = {
				'followers':followers,
				'user_profile':victim_user,
				'current_user':user,
				'user_names':user_names,
			}
			template = JINJA_ENVIROMENT.get_template('followers.html')
			self.response.write(template.render(template_values))

class Following(webapp2.RequestHandler):
	def get(self, victim_email):
		user = users.get_current_user()
		if not user:
			url = users.create_login_url(self.request.uri)
			template_values = {
				'url':url,
			}
			template = JINJA_ENVIROMENT.get_template('insta-login.html')
			self.response.write(template.render(template_values))
		else:
			ndb_victim_key = ndb.Key(InstaUser, victim_email)
			victim_user = ndb_victim_key.get()
			followings = victim_user.following
			insta_users = InstaUser.query().fetch()
			user_names = []
			for insta_user in insta_users:
				user_names.append(str(insta_user.username))
			template_values = {
				'followings':followings,
				'user_profile':victim_user,
				'current_user':user,
				'user_names':user_names,
			}
			template = JINJA_ENVIROMENT.get_template('following.html')
			self.response.write(template.render(template_values))
			
class PostComment(webapp2.RequestHandler):
	def post(self, post_key):
		user = users.get_current_user()
		user_comment = self.request.get('comment')
		if not user:
			url = users.create_login_url(self.request.uri)
			template_values = {
				'url':url,
			}
			template = JINJA_ENVIROMENT.get_template('insta-login.html')
			self.response.write(template.render(template_values))
		else:
			insta_user = InstaUser.query(InstaUser.user == user).get()
			ndb_post_key = ndb.Key(urlsafe=post_key)
			post = ndb_post_key.get()
			comment = Comment()
			comment.post = ndb_post_key
			comment.commented_by = insta_user.username
			comment.user_comment = user_comment
			comment.date = datetime.now()
			comment.put()
			self.redirect("/")
			
class PhotoUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
	def post(self):
		current_user = users.get_current_user()
		upload = self.get_uploads()[0]
		caption = self.request.POST['caption']
		if caption == 'profile':
			user = InstaUser.query(InstaUser.user==current_user).get()
			user.profile_image = upload.key()
			user.put()
			self.redirect('profile/'+str(user.user.email()))
		else:
			insta_user = InstaUser.query(InstaUser.user == current_user).get()
			post = Post()
			post.post_image = upload.key()
			post.caption = caption
			post.date = datetime.now()
			post.posted_by = insta_user.username
			post.put()
			self.redirect('/')
		
class ViewProfilePhotoHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, username):
		user_profile = InstaUser.query(InstaUser.username == username).get()
		photo_key = user_profile.profile_image
		self.send_blob(photo_key)
			
class ViewPhotoHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, photo_key):
        if not blobstore.get(photo_key):
            self.error(404)
        else:
            self.send_blob(photo_key)
			
JINJA_ENVIROMENT = jinja2.Environment(
	loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
	extensions = ['jinja2.ext.autoescape'],
	autoescape = True
)

app = webapp2.WSGIApplication([
	('/', InstaLoginPage),
	('/timeline', TimeLinePage),
	('/follow/(.*)', Follow),
	('/unfollow/(.*)', Unfollow),
	('/profile/(.*)', ProfilePage),
	('/username', UserName),
	('/post/(.*)', PostPage),
	('/followers/(.*)', Followers),
	('/following/(.*)', Following),
	('/post_comment/(.*)', PostComment),
	('/upload_photo', PhotoUploadHandler),
	('/view_profile_photo/([^/]+)?', ViewProfilePhotoHandler),
	('/view_photo/([^/]+)?', ViewPhotoHandler),
], debug = True)