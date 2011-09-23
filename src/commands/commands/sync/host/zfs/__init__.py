# $Id: __init__.py,v 1.1 2011/09/23 22:17:27 anoop Exp $

# @Copyright@
# @Copyright@

# $Log: __init__.py,v $
# Revision 1.1  2011/09/23 22:17:27  anoop
# Renamed thumper-conf roll as ZFS storage roll
# and included in the mainline rocks tree
#
# Revision 1.3  2010/09/02 22:02:49  anoop
# Make sure the hosts that we iterate against
# are in the zfs_replica table.
#
# Revision 1.2  2010/08/30 18:47:24  anoop
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
from subprocess import Popen, PIPE
import os
import sys

class Command(rocks.commands.sync.host.command, rocks.commands.HostArgumentProcessor):
	"""
	Synchronizes the zfs replication, key and permissions
	configurations to the zfs clients and servers in the
	cluster.
	"""
	def run(self, params, args):
		if len(args) > 0:
			hosts = self.getHostnames(args)
		else:
			self.db.execute('select distinct nodes.name '	+\
				'from zfs_replication, nodes where '	+\
				'zfs_replication.local_host=nodes.id')
			hosts = self.db.fetchall()
			f = lambda(x): x[0]
			hosts = map(f, hosts)
		for host in hosts:
			self.runPlugins(host)
