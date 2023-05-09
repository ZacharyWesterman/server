let Perms
let UserData = {}

export async function revoke_sessions(username)
{
	const self_msg = 'Are you sure you want to revoke your sessions? This will log you out of all devices, including this one.'
	const other_msg = 'Are you sure you want to revoke all sessions for user "' + username + '"? This will log them out of all devices.'

	const choice = await _.modal({
		title: 'Revoke User Sessions',
		text: (username === api.username) ? self_msg : other_msg,
		buttons: ['Yes', 'No'],
	}).catch(() => 'no')

	if (choice !== 'yes') return

	await mutate.users.revoke(username)
	$('session-ct-' + username).innerText = await query.users.sessions(username)
}

export async function set_perms()
{
	UserData.perms = []
	for (var perm of Perms)
	{
		if ($('perm-'+perm.name).checked) UserData.perms.push(perm.name)
	}

	const res = await mutate.users.permissions(UserData.username, UserData.perms)
	if (res.__typename !== 'UserData') {
		_.modal({
			type: 'error',
			title: 'ERROR',
			text: res.message,
			buttons: ['OK']
		}).catch(()=>{})
		return
	}

	sync_perm_descs()
}

export async function load_user_data(username, self_view = false)
{
	$.hide('mainpage')

	if (!Perms)
	{
		Perms = await api.get_json('/config/permissions.json')
	}

	UserData = await query.users.get(username)
	await _('userdata', {
		perms: Perms,
		user: UserData,
		sessions: query.users.sessions(username),
		self_view: self_view,
	})

	sync_perm_descs()
}

function sync_perm_descs()
{
	for (const perm of Perms)
	{
		const desc = $('perm-'+perm.name).checked ? "true" : "false"
		$('perm-tooltip-'+perm.name).innerText = perm[desc]
	}
}

export async function update_password(password, username)
{
	if ((password.length < 8) || (password === username) || (password.includes(username) && (password.length < username.length * 2)))
	{
		const criteria = [
			'Must be at least 8 characters long',
			'May not contain the username, unless it\'s at least 2&times; the length',
		]

		_.modal({
			type: 'error',
			title: 'Invalid Password',
			text: 'Password must fit <i>all</i> of the following criteria:<ul><li>' + criteria.join('</li><li>') + '</li></ul>',
			buttons: ['OK'],
		}).catch(() => {})
		return
	}

	const hashed_pass = await api.hash(password)
	const res = await mutate.users.password(username, hashed_pass)

	if (res.__typename !== 'UserData')
	{
		_.modal({
			type: 'error',
			title: 'ERROR',
			text: res.message,
			buttons: ['OK'],
		})
		return
	}

	_.modal({
		title: 'Success',
		text: 'Password has been updated.',
		buttons: ['OK'],
	})
}

export async function show_sessions_info()
{
	await _.modal({
		type: 'info',
		title: 'What is a session?',
		text: await api.get('/html/snippit/login_sessions.html'),
		buttons: ['OK'],
	}).catch(() => {})
}
