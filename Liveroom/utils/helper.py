from django.conf import settings

def avatar_allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in settings.ALLOWED_EXTENSIONS

def file_allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in settings.FILE_ALLOWED_EXTENSIONS
