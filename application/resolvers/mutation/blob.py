import application.exceptions as exceptions
from application.db.blob import delete_blob, get_blob_data, set_blob_tags
import application.db.perms as perms

def resolve_delete_blob(_, info, id: str) -> dict:
	try:
		blob_data = get_blob_data(id)

		# Make sure user is either an admin,
		# or are trying to delete their own blob.
		if not perms.satisfies(info, ['admin'], blob_data):
			return perms.bad_perms()

		blob_data = delete_blob(id)
		blob_data['id'] = blob_data['_id']
		return { '__typename': 'Blob', **blob_data }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

def resolve_set_blob_tags(_, info, id: str, tags: list) -> dict:
	try:
		return { '__typename': 'Blob', **set_blob_tags(id, tags) }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }
