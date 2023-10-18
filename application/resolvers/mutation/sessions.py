from application.db.sessions import revoke_sessions, count_valid_sessions
import application.db.perms as perms

@perms.require(['admin'], perform_on_self = True)
def resolve_revoke_user_sessions(_, info, username: str) -> int:
	session_count = count_valid_sessions(username)
	revoke_sessions(username)
	return session_count
