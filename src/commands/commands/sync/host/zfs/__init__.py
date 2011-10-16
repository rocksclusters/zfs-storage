# $Id: __init__.py,v 1.2 2011/10/16 07:03:27 anoop Exp $

# @Copyright@
# @Copyright@

# $Log: __init__.py,v $
# Revision 1.2  2011/10/16 07:03:27  anoop
# Attempt to connect to replication server to setup zfs-permissions correctly.
# This will only work if the replication server is part of our cluster
#
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
import os
import sys
from rocks.commands.sync.host import Parallel
from rocks.commands.sync.host import timeout

class Command(rocks.commands.sync.host.command, rocks.commands.HostArgumentProcessor):
	"""
	Synchronizes the zfs replication, key and permissions
	configurations to the zfs clients and servers in the
	cluster.
	"""
	def run(self, params, args):
		# lambda function to return first element in a tuple.
		# ("hostname", ) is the tuple that the sql statement
		# returns, and we want just "hostname"
		f = lambda(x): x[0]

		if len(args) > 0:
			hosts = self.getHostnames(args)
		else:
			self.db.execute('select distinct nodes.name '	+\
				'from zfs_replication, nodes where '	+\
				'zfs_replication.local_host=nodes.id')
			hosts = self.db.fetchall()
			hosts = map(f, hosts)
		for host in hosts:
			self.runPlugins(host)


		# Select all the replication servers, and try to set permissions
		# on their backup filesystems. Do this only for hosts that are under
		# our control. Since we cannot run the list of remote hosts
		# through the getHostnames function, we have to try and login
		# to every host without a password, and hope they connect.
		self.db.execute('select remote_host, remote_fs from ' +\
			'zfs_replication group by remote_host, remote_fs')
		rows = self.db.fetchall()
		cmd_line = '/opt/rocks/thumper/zfs-perms-setup.sh'
		ssh_cmd = 'ssh -xT -o NumberOfPasswordPrompts=0'
		threads = []
		for (host, fs) in rows:
			cmd = '%s %s "%s %s"' % (ssh_cmd, host, cmd_line, fs)
			p = Parallel(cmd, host)
			threads.append(p)
			p.start()
		
		for thread in threads:
			thread.join(timeout)
