import json
import datetime
import os, sys

try:
	from dropbox import client as dropbox_client
	from dropbox import rest, session
except ImportError:
	print "Dropbox module not installed\nInstall it with:\n\tpip install dropbox"
	exit()

def main():
	client_secrets = json.loads(open("client_secrets.json").read())

	try:
		if len(client_secrets["app_key"]) and len(client_secrets["app_secret"]):
			# ready to go
			pass
		else:
			print "app_key and app_secret not provided\n\nCreate a app at https://www.dropbox.com/developers/apps/create and insert the app_key and app_secret in client_secrets.json\nAnd try again"
			raw_input()
			client_secrets = json.loads(open("client_secrets.json").read())
	except KeyError, e:
		raise e

	sess = session.DropboxSession(client_secrets.get("app_key"), client_secrets.get("app_secret"), client_secrets.get("access_type")) # created the session object

	try:
		if len(client_secrets["access_key"]) and len(client_secrets["access_secret"]):
			# authorized
			pass
		else:
			request_token = sess.obtain_request_token() # obtain the request token
			url = sess.build_authorize_url(request_token)
			# Make the user sign in and authorize this token
			print "url:", url
			print "Please visit this website and press the 'Allow' button, then hit 'Enter' here."
			raw_input()
			# This will fail if the user didn't visit the above URL and hit 'Allow'
			access_token = sess.obtain_access_token(request_token)
			print "access_key --> " + access_token.key
			print "access_secret --> " + access_token.secret
			print "\nCopy the access_key and access_secret to client_secrets.json"
			return
	except KeyError, e:
		raise e

	# pass the key and the secret
	sess.set_token(client_secrets.get("access_key"),client_secrets.get("access_secret"))
	# create the client object
	client = dropbox_client.DropboxClient(sess)
	nameOfFile = datetime.datetime.today().strftime("%Y%m%d") + "-db-backup.gz"
	try:
		with open(nameOfFile): pass #check existance of while
		print "Uploading started..."
		print client.put_file("/db_backup/" + nameOfFile, open(nameOfFile))
		print "Uploading completed..."
	except IOError, e:

		traceback_str = traceback.format_exc()
		content = "String of error:\n\n"+str(traceback_str)+"\n\n***********\n\n"
		content = content.replace("<","").replace(">","")
		content +="File trying to work with:"+nameOfFile
		subject = "Kikar: Problem with DB backup"
		addresses = "agam.rafaeli@gmail.com,yotammanor@gmail.com"
		os.system('echo "%s" | mail -s "%s" "%s"' % (content, subject, addresses))
	return

if __name__ == '__main__':
	main()
