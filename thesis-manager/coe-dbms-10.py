import os
import urllib
from google.appengine.ext import ndb
from google.appengine.api import users
import jinja2
import webapp2

#Create Student Database CRUD web app that atleast have the following pages
#1. Create Student page
#url: /student/create
#description: contains the form to create a student

#2. Student List page
#url: /student/list
#description: displays the list of all created student

#3. Student page
#url: /student/<student-id>
#eg: /student/1231231293103012931
#description: displays all details of a student entry
#contains the button to edit or delete a student

#4. Student Edit/Update Page
#url: /student/edit/<student-id> 
#eg: /student/edit/123472739847917983131
#description: contains the form to update a student


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class Student(ndb.Model):
    first_name = ndb.StringProperty(indexed=True)
    last_name = ndb.StringProperty(indexed=True)
    email = ndb.StringProperty(indexed=True)
    student_number = ndb.StringProperty(indexed=True)
    age = ndb.IntegerProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)


class SuccessPage(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('student_success.html')
        self.response.write(template.render())


#Create Student Database CRUD web app that atleast have the following pages
#1. Create Student page
#url: /student/create
#description: contains the form to create a student
class StudentNewHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('student_create.html')
        self.response.write(template.render())

    def post(self):
        student = Student()

        student.first_name = self.request.get('first_name')
        student.last_name = self.request.get('last_name')
        student.email = self.request.get('email')
        student.student_number = self.request.get('student_number')
        student.age = int(self.request.get('age'))
        student.put()
        self.redirect('/success')

#2. Student List page
#url: /student/list
#description: displays the list of all created student
class StudentListHandler(webapp2.RequestHandler):
    def get(self):
        students = Student.query().order(-Student.date).fetch()
        template_values = {
            "student_list": students,
        }
        template = JINJA_ENVIRONMENT.get_template('student_list.html')
        self.response.write(template.render(template_values))

#3. Student page
#url: /student/<student-id>
#eg: /student/1231231293103012931
#description: displays all details of a student entry
#contains the button to edit or delete a student     
class StudentView(webapp2.RequestHandler):
    def get(self,stud_id):
        
        students = Student.query().order(-Student.date).fetch()
        stud_id = int(stud_id)

        values = {
            'student_list': students,
            'id': stud_id
        }

 
        template = JINJA_ENVIRONMENT.get_template('student_view.html')
        self.response.write(template.render(values))



        
#4. Student Edit/Update Page
#url: /student/edit/<student-id> 
#eg: /student/edit/123472739847917983131
#description: contains the form to update a student

class StudentEdit(webapp2.RequestHandler):
    def get(self,stud_id):
        
        students = Student.query().order(-Student.date).fetch()
        stud_id = int(stud_id)

        values = {
            'student_list': students,
            'id':stud_id
        }

 
        template = JINJA_ENVIRONMENT.get_template('student_edit.html')
        self.response.write(template.render(values))


    def post(self, stud_id):

        stud_id = int(stud_id)    
        student = Student.get_by_id(stud_id)

        student.first_name = self.request.get('first_name')
        student.last_name = self.request.get('last_name')
        student.email = self.request.get('email')
        student.student_number = self.request.get('student_number')
        student.age = int(self.request.get('age'))
        student.put()
        self.redirect('/success')

#Student Delete ID
class StudentDelete(webapp2.RequestHandler):
   
       
    def get(self,stud_id):
       
        
        student = Student.get_by_id(int(stud_id))
        student.key.delete()
        self.redirect('/success/deleteID')
        
class SuccessDeletePage(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('student_delete.html')
        self.response.write(template.render())       

#Guestbook 


DEFAULT_GUESTBOOK_NAME = 'default_guestbook'


# We set a parent key on the 'Greetings' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent. However, the write rate should be limited to
# ~1/second.

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    """Constructs a Datastore key for a Guestbook entity.

    We use guestbook_name as the key.
    """
    return ndb.Key('Guestbook', guestbook_name)


class Author(ndb.Model):
    """Sub model for representing an author."""
    identity = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)


class Greeting(ndb.Model):
    """A main model for representing an individual Guestbook entry."""
    author = ndb.StructuredProperty(Author)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


class MainPage(webapp2.RequestHandler):

    def get(self):
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greetings_query = Greeting.query(
            ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
        greetings = greetings_query.fetch(10)

        user = users.get_current_user()
        if user:
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'greetings': greetings,
            'guestbook_name': urllib.quote_plus(guestbook_name),
            'url': url,
            'url_linktext': url_linktext,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class Guestbook(webapp2.RequestHandler):

    def post(self):
        # We set the same parent key on the 'Greeting' to ensure each
        # Greeting is in the same entity group. Queries across the
        # single entity group will be consistent. However, the write
        # rate to a single entity group should be limited to
        # ~1/second.
        guestbook_name = self.request.get('guestbook_name',
                                          DEFAULT_GUESTBOOK_NAME)
        greeting = Greeting(parent=guestbook_key(guestbook_name))

        if users.get_current_user():
            greeting.author = Author(
                    identity=users.get_current_user().user_id(),
                    email=users.get_current_user().email())

        greeting.content = self.request.get('content')
        greeting.put()

        query_params = {'guestbook_name': guestbook_name}
        self.redirect('/?' + urllib.urlencode(query_params))

class ChooseApp(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('Mainpage.html')
        self.response.write(template.render())

    


application = webapp2.WSGIApplication([
    ('/', ChooseApp),
    ('/guestbook', MainPage),
    ('/sign', Guestbook),
    ('/student/create', StudentNewHandler),
    ('/student/list', StudentListHandler),
    ('/success', SuccessPage),
    ('/student/(\d+)', StudentView),
    ('/student/edit/(\d+)', StudentEdit),
    ('/student/delete/(\d+)',StudentDelete),
    ('/success/deleteID', SuccessDeletePage)
   # ('/student/list', StudentUpdatedList)
], debug=True)
