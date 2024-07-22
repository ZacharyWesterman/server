from application.db.datafeed import get_user_feeds, get_documents, count_documents
from application.exceptions import ClientError
from application.objects import Sorting

def resolve_get_user_feeds(_, info, username: str) -> list[dict]:
	try:
		return get_user_feeds(username)
	except ClientError:
		return []

def resolve_get_feed_documents(_, info, feed: str, start: int, count: int, sorting: Sorting) -> list[dict]:
	return get_documents(feed, start, count, sorting)

def resolve_count_feed_documents(_, info, feed: str) -> int:
	return count_documents(feed)