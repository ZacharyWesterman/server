from application.tokens import decode_user_token, get_request_token
import application.exceptions as exceptions
import application.tags as tags

from bson.objectid import ObjectId
from datetime import datetime
import mimetypes
import threading
import os

db = None
blob_path = None

def path(id: str, ext: str = None) -> str:
	global blob_path
	return f'{blob_path}/{id}.{ext}' if ext is not None else f'{blob_path}/{id}'

def save_blob_data(file: object) -> str:
	global blob_path
	id, ext = create_blob(file.filename)

	# make file size readable
	filesize = file.content_length
	sizetype = 'B'
	if filesize >= 1000:
		filesize /= 1000
		sizetype = 'KiB'
	if filesize >= 1000:
		filesize /= 1000
		sizetype = 'MiB'
	if filesize >= 1000:
		filesize /= 1000
		sizetype = 'GiB'
	filesize = round(filesize, 3)

	print(f'Beginning stream of file "{file.filename}" ({filesize} {sizetype})...')
	file.save(path(id, ext))
	print(f'Finished stream of file "{file.filename}" ({filesize} {sizetype}).')
	mark_as_completed(id)

	return id

def create_blob(name: str, tags: list = []) -> str:
	global db
	pos = name.rfind('.')
	ext = name[pos+1::]

	username = decode_user_token(get_request_token()).get('username')
	mime = mimetypes.guess_type(name)[0]
	if mime is None:
		mime = 'application/octet-stream'

	return db.data.blob.insert_one({
		'created': datetime.utcnow(),
		'name': name[0:pos],
		'ext': ext,
		'mimetype': mime,
		'tags': tags,
		'creator': username,
		'complete': False,
	}).inserted_id, ext

def mark_as_completed(id: str) -> None:
	db.data.blob.update_one({'_id': ObjectId(id)}, {'$set': {'complete': True}})

def get_user_blobs(username: str, start: int, count: int, tagstr: str) -> list:
	global db
	blobs = []
	mongo_tag_query = tags.parse(tagstr).output()

	for i in db.data.blob.find({'$and': [{'creator': username}, mongo_tag_query]}, sort=[('created', -1)]).limit(count).skip(start):
		i['id'] = i['_id']
		blobs += [i]

	return blobs

def get_all_blobs(start: int, count: int, tagstr: str) -> list:
	global db
	mongo_tag_query = tags.parse(tagstr).output()

	blobs = []
	for i in db.data.blob.find(mongo_tag_query, sort=[('created', -1)]).limit(count).skip(start):
		i['id'] = i['_id']
		blobs += [i]

	return blobs

def count_user_blobs(username: str, tagstr: str) -> int:
	global db
	mongo_tag_query = tags.parse(tagstr).output()
	return db.data.blob.count_documents({'$and': [{'creator': username}, mongo_tag_query]})

def count_all_blobs(tagstr: str) -> int:
	global db
	mongo_tag_query = tags.parse(tagstr).output()
	return db.data.blob.count_documents(mongo_tag_query)

def get_blob_data(blob_id: str) -> dict:
	global db
	blob_data = db.data.blob.find_one({'_id': ObjectId(blob_id)})
	if blob_data:
		blob_data['id'] = blob_data['_id']
	return blob_data

def delete_blob(blob_id: str) -> bool:
	global db
	blob_data = db.data.blob.find_one({'_id': ObjectId(blob_id)})
	if blob_data:
		try:
			os.remove(path(blob_id, blob_data['ext']))
		except FileNotFoundError:
			pass
		db.data.blob.delete_one({'_id': ObjectId(blob_id)})
		return blob_data

	raise exceptions.BlobDoesNotExistError(blob_id)
