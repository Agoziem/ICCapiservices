from storages.backends.s3boto3 import S3Boto3Storage

class StaticStore(S3Boto3Storage):
	location = "static"
	default_acl = 'public-read'
	file_overwrite = False

class MediaStore(S3Boto3Storage):
	location = "media"
	default_acl = 'public-read'
	file_overwrite = False  # Changed to False to preserve unique filenames 