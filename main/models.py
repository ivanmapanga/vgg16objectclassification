#from google.appengine.ext import ndb
#from datastore_entity import DatastoreEntity, EntityValue
''' BaseModel class
'''
class BaseModel(object):#DatastoreEntity):
	#name = ndb.StringProperty()
	#__kind__ = "user"
	#def get(self, key, value):
	#	return self.get_obj(key, value)
	pass

'''Detected class
'''
class Detected(BaseModel):#, UserMixin):
	percent = None #= EntityValue()#ndb.FloatProperty()
	label = None #= EntityValue()#ndb.StringProperty()
	frame = None #= EntityValue()#ndb.BlobKeyProperty()
