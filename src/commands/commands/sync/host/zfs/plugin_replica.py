# $Id: plugin_replica.py,v 1.1 2011/09/23 22:17:27 anoop Exp $

# @Copyright@
# @Copyright@

# $Log: plugin_replica.py,v $
# Revision 1.1  2011/09/23 22:17:27  anoop
# Renamed thumper-conf roll as ZFS storage roll
# and included in the mainline rocks tree
#
# Revision 1.2  2010/09/02 22:03:00  anoop
# Bug fix
#
# Revision 1.1  2010/08/30 18:47:24  anoop
# Fix synchronization of the zfs replication configuration. Now
# a single "rocks sync host zfs" command should synchronize the
# replication, keys and permission information
#

import rocks.commands

class Plugin(rocks.commands.Plugin):

	def provides(self):
		return "replica"

	def run(self, host):
		self.owner.command('sync.host.zfs.replica', [host])
