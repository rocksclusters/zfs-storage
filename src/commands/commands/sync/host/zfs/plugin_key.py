# $Id: plugin_key.py,v 1.1 2011/09/23 22:17:27 anoop Exp $

# @Copyright@
# @Copyright@

# $Log: plugin_key.py,v $
# Revision 1.1  2011/09/23 22:17:27  anoop
# Renamed thumper-conf roll as ZFS storage roll
# and included in the mainline rocks tree
#
# Revision 1.3  2010/10/08 21:51:54  anoop
# Cleanup. Moved zfs key syncing to it's own command
#
# Revision 1.2  2010/09/02 22:03:00  anoop
# Bug fix
#
# Revision 1.1  2010/08/30 18:47:24  anoop
# Fix synchronization of the zfs replication configuration. Now
# a single "rocks sync host zfs" command should synchronize the
# replication, keys and permission information
#
# Revision 1.1  2009/08/25 21:23:42  anoop
# Added the sync commands. This can sync the authorized_keys files
# on the replication servers, and sync the replication crontab files
# on the replication clients.
#

import rocks.commands

class Plugin(rocks.commands.Plugin):

	def provides(self):
		return "key"

	def run(self, host):
		# Get a list of all the replication servers the the clients
		# replicate to.
		self.owner.db.execute('select distinct z.remote_host '	+\
			'from zfs_replication z, nodes n where '	+\
			'n.name="%s" and z.local_host=n.id' % host)
		rhosts = self.owner.db.fetchall()
		f = lambda(x): x[0]
		rhosts = map(f, rhosts)

		# Run them through our host argument processor to filter the
		# ones that belong to the cluster
		rhostnames = self.owner.getHostnames(rhosts)

		# Run the sync command through all of them
		self.owner.command('sync.host.zfs.key',rhostnames)
