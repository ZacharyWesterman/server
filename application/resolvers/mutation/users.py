import application.exceptions as exceptions
from application.db.users import *
import application.db.perms as perms

@perms.require(['admin'])
def resolve_create_user(_, info, username: str, password: str) -> dict:
	try:
		userdata = create_user(username, password)
		return { '__typename' : 'UserData', **userdata }
	except exceptions.ClientError as e:
		return { '__typename' : e.__class__.__name__, 'message' : str(e) }

@perms.require(['admin'], perform_on_self = False)
def resolve_delete_user(_, info, username: str) -> dict:
	try:
		userdata = delete_user(username)
		return { '__typename' : 'UserData', **userdata }
	except exceptions.ClientError as e:
		return { '__typename' : e.__class__.__name__, 'message' : str(e) }

@perms.require(['admin'])
def resolve_update_user_theme(_, info, username: str, theme: dict) -> dict:
	try:
		userdata = update_user_theme(username, theme)
		return { '__typename': 'UserData', **userdata }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

@perms.require(['admin'])
def resolve_delete_user_theme(_, info, username: str) -> dict:
	try:
		userdata = update_user_theme(username, {'colors': [], 'sizes': []})
		return { '__typename': 'UserData', **userdata }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

@perms.require(['admin'])
def resolve_update_user_perms(_, info, username: str, perms: list) -> dict:
	try:
		userdata = update_user_perms(username, perms)
		return { '__typename': 'UserData', **userdata }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

@perms.require(['admin'])
def resolve_update_user_password(_, info, username: str, password: str) -> dict:
	try:
		userdata = update_user_password(username, password)
		return { '__typename': 'UserData', **userdata }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }

@perms.require(['admin'])
def resolve_update_user_display_name(_, info, username: str, display_name: str) -> dict:
	try:
		userdata = update_user_display_name(username, display_name)
		return { '__typename': 'UserData', **userdata }
	except exceptions.ClientError as e:
		return { '__typename': e.__class__.__name__, 'message': str(e) }