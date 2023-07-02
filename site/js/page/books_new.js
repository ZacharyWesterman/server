//Start the NFC reader ONCE per session, and don't stop it.
//Trying to stop/restart it multiple times in a session
//just causes the browser to crash. :/
if (window.NFC === undefined)
{
	try {
		window.NFC = new NDEFReader
	} catch(e) {
		window.NFC = {
			scan: () => {}
		}
	}
}

NFC.scan()

export function init()
{
	window.unload.push(() => {
		NFC.onreading = undefined
	})

	NFC.onreading = event =>
	{
		//Check if a book with the tag ID already exists
		api(`
		query ($rfid: String!) {
			getBookByTag (rfid: $rfid) {
				__typename
			}
		}`, {
			rfid: event.serialNumber,
		}).then(res => {
			if (res.__typename === 'Book')
			{
				_.modal({
					type: 'error',
					title: 'Book Already Linked',
					text: 'A book with this tag has already been cataloged. Please try a different tag or un-link the one from this book.',
					buttons: ['OK'],
				}).catch(() => {})
			}
			else
			{
				$('new-tagid').value = event.serialNumber
				_.modal.checkmark()
			}
		})
	}

	$.bind('new-title', search_books)
	$.bind('new-author', search_books)
}

export async function search_books()
{
	const title = $.val('new-title')
	const author = $.val('new-author')

	if (`${author}${title}` === '')
	{
		await _('booklist', [])
		return
	}

	const res = await api(`
	query ($title: String!, $author: String!) {
		searchBooks(title: $title, author: $author) {
			__typename
			...on BookList {
				books {
					id
					title
					subtitle
					authors
					description
					thumbnail
				}
			}
			...on ApiFailedError {
				message
			}
		}
	}`, {
		title: title,
		author: author,
	})

	if (res.__typename !== 'BookList')
	{
		_.modal({
			type: 'error',
			title: 'ERROR',
			text: res.message,
			buttons: ['OK'],
		}).catch(() => {})
		return
	}

	await _('booklist', res.books)
}

export async function select_book(book_id, book_title)
{
	const tagid = $.val('new-tagid')
	if (tagid === '')
	{
		_.modal({
			type: 'error',
			title: 'Tag ID Missing',
			text: 'Please scan an RFID tag so it can be associated with this book.',
			buttons: ['OK'],
		}).catch(() => {})
		return
	}

	const choice = await _.modal({
		title: book_title,
		text: `Do you want to associate this book with Tag ID ${tagid}?`,
		buttons: ['Yes', 'No'],
	}).catch(() => 'no')
	if (choice !== 'yes') return

	const res = await api(`
	mutation ($rfid: String!, $bookId: String!) {
		linkBookTag (rfid: $rfid, bookId: $bookId) {
			__typename
			...on BookTagExistsError {
				message
			}
			...on ApiFailedError {
				message
			}
		}
	}`, {
		rfid: tagid,
		bookId: book_id,
	})

	if (res.__typename !== 'BookTag')
	{
		_.modal({
			type: 'error',
			title: 'Failed to link book',
			text: res.message,
			buttons: ['OK']
		}).catch(() => {})
		return
	}

	_.modal.checkmark()

	//Wipe all fields
	$('new-tagid').value = ''
	$('new-title').value = ''
	$('new-author').value = ''
	await search_books()
}

export function help()
{
	_.modal({
		type: 'info',
		title: 'Where does this data come from?',
		text: api.snippit('new_book_help'),
		buttons: ['OK'],
	}).catch(() => {})
}