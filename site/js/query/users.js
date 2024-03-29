export default {
	__user_list: null,

	list: async (filter, use_cache = true, restrict = true) =>
	{
		let res
		if (query.users.__user_list === null || !use_cache)
		{
			res = await api(`query ($restrict: Boolean!) {
				listUsers (restrict: $restrict) {
					username
					display_name
				}
			}`, {
				restrict: restrict,
			})
			query.users.__user_list = res
		}
		else
			res = query.users.__user_list
		return (filter ? res.filter(filter) : res).map(i => { return {value: i.username, display: i.display_name} })
	},

	sessions: async username =>
	{
		return await api(`query ($username: String!) {
			countSessions (username: $username)
		}`, {
			username: username,
		})
	},

	get: async username =>
	{
		return await api(`query ($username: String!){
			getUser(username:$username) {
				__typename
				...on UserData {
					username
					theme {
						colors {
							name
							value
						}
						sizes {
							name
							value
						}
					}
					perms
					last_login
					display_name
					groups
				}
				...on UserDoesNotExistError {
					message
				}
				...on InsufficientPerms {
					message
				}
			}
		}`, {
			username: username
		})
	},
}
