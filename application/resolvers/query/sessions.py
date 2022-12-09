from application.db.sessions import revoke_sessions, count_valid_sessions
import application.db.creds as creds

@creds.require(['admin'])
def resolve_count_user_sessions(_, info, username: str) -> int:
	return count_valid_sessions(username)
