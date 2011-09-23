# $Id: __init__.py,v 1.1 2011/09/23 22:17:27 anoop Exp $

# @Copyright@
# @Copyright@

# $Log: __init__.py,v $
# Revision 1.1  2011/09/23 22:17:27  anoop
# Renamed thumper-conf roll as ZFS storage roll
# and included in the mainline rocks tree
#
# Revision 1.1  2009/08/19 02:31:52  anoop
# Major overhaul of the replication infrastructure
# - commands are now moved to
#   <add/list/remove/report>/host/zfs/<key/replica>
#   for consistency
# - major changes to database schema corresponds to
#   the changes in command line
# - cleanup of commands
#

import rocks.commands

class Command(rocks.commands.report.host.Command):
	"""
	Prints out machine readable authorized_keys file
	for the ZFS user
	<arg type="string" name="host">
	Hostname of the replica server
	</arg>
	"""
	def run(self, params, args):

		hosts = self.getHostnames(args)
		if len(hosts) > 1:
			self.abort("Must supply one host only")
			
		host = hosts[0]

		self.db.execute(
			'select zfs_keys.public_key, zfs_keys.user from ' + \
			'zfs_keys, nodes where zfs_keys.host=nodes.id and'+ \
			' nodes.name="%s"' % host)

		user_keys = {}
		for (pkey, user) in self.db.fetchall():
			if not user_keys.has_key(user):
				user_keys[user] = []
			user_keys[user].append(pkey)

		self.beginOutput()
		for user in user_keys:
			self.addText('<file ' +\
				'name="/opt/rocks/thumper/%s/.ssh/authorized_keys"' % user +\
			 	' owner="%s:sys">\n' % user)
			for key in user_keys[user]:
				self.addText(key + '\n')
			self.addText('</file>\n')

		self.endOutput()
