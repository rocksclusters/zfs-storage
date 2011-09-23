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
import subprocess
import sys

class Command(rocks.commands.remove.host.Command):
	"""
	Removes one or all public keys for a given
	replication server a given key for multiple
	replication servers
	<arg type="string" name="host">
	Hostname of the replication server
	</arg>
	<param type="string" name="user">
	User whose keys should be removed
	</param>
	<param type="string" name="key">
	Public key fingerprint that you'd like to remove. If this
	argument is not given, all keys associated with
	the host are removed from the database. To get the fingerprint
	of a particular public key, run "rocks list host zfs key" command
	</param>

	<related>list host zfs key</related>
	<related>add host zfs key</related>
	"""
	def run(self, params, args):
		(key,user) = self.fillParams([('key',),('user',)])
		if not key and not user and len(args)==0:
			self.abort('Must specify host, or key, or user')
		hosts = self.getHostnames(args)
		for host in hosts:
			sql_cmd = 'delete zfs_keys from zfs_keys INNER JOIN ' + \
				'nodes where zfs_keys.host=nodes.id and ' + \
				'nodes.name="%s"' % host
			if key:
				sql_cmd = sql_cmd + \
					" and zfs_keys.fingerprint='%s'" % key
			if user:
				sql_cmd = sql_cmd + \
					" and zfs_keys.user='%s'" % user

			self.db.execute(sql_cmd)
