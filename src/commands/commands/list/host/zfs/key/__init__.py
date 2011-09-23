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

import os
import rocks.commands
import tempfile
import subprocess

class Command(rocks.commands.list.host.Command):
	"""
	Prints the fingerprint of public keys that need to be placed
	on the various replication servers
	<arg type="string" name="host">
	Hostname(s)
	</arg>
	"""
	def run(self, params, args):
		self.beginOutput()
		for host in self.getHostnames(args):
			self.db.execute('select zfs_keys.user, ' +\
				'zfs_keys.fingerprint ' +\
				'from nodes, zfs_keys where ' +\
				'nodes.name="%s" ' % (host) +\
				'and zfs_keys.host=nodes.id')
			for row in self.db.fetchall():
				username = row[0]
				fingerprint = row[1]
				self.addOutput(host, (username, fingerprint))
		self.endOutput(header=['Host','User','Public_Key_Fingerprint'], trimOwner=0)
