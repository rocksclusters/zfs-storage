# $Id: __init__.py,v 1.1 2011/09/23 22:17:27 anoop Exp $
#
# @Copyright@
# @Copyright@
#
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
# Revision 1.2  2008/10/16 00:49:52  anoop
# Cleanup of replication commands
# Changed xml files to work correctly on a linux frontend
#
# Revision 1.1  2008/09/25 00:16:33  anoop
# Major checkin for replication.\n zfs_backup is now a new package that builds on Solaris only.\n
#
# Revision 1.1  2008/08/27 19:25:22  clem
# First version of the
# rocks add/list/remove host replica
# to manipulate the thumper replication system
#
# Luca
#
#
#


import os
import stat
import time
import sys
import string
import locale
import rocks.commands


class Command(rocks.commands.remove.host.command):
	"""
	Remove a replica definition. Note that this
	command removes only the definition, and does
	not remove the actual replica on the replication
	servers.

	<arg type='string' name='host'>
	Hostname of the replication client
	</arg>
	
	<param type='string' name='local_fs'>
	The local zfs file system to remove from replication database
	If not specified, then all replicated filesystems are removed
	from the database, unless other parameters narrow the entry.
	</param>

	<param type='string' name='remote_host'>
	Host name of the replication server
	</param>

	<param type='string' name='remote_fs'>
	Remote filesystem to be removed from database
	</param>
	<example cmd='remove host zfs replica nas-0-0'>
	Removes all the replica definitions for nas-0-0
	</example>
	<example cmd='remove host zfs replica nas-0-0 local_fs=export/data'>
	Removes all replica definitions for nas-0-0 for filesystem export/data
	</example>
	<example cmd='remove host zfs replica nas-0-0 remote_host=nas-0-1'>
	Removes all replica definitions for client nas-0-0 and server nas-0-1
	</example>
	<example cmd='remove host zfs replica nas-0-0 local_fs=export/data remote_host=nas-0-1'>
	Removes only the replica definition
	</example>
	"""

	def run(self, params, args):
		(local_fs, remote_host, remote_fs) = self.fillParams([
		('local_fs',),
		('remote_host',),
		('remote_fs',),
		])

		if not local_fs \
			and not remote_host \
			and not remote_fs   \
			and len(args) == 0:
			self.abort('Please specify a parameter')

		hosts = self.getHostnames(args)

		for host in hosts:
			sql_string = \
				'delete zfs_replication, zfs_rep_frequency ' +\
				'from zfs_replication INNER JOIN '	     +\
				'zfs_rep_frequency INNER JOIN nodes ' 	     +\
				'where zfs_replication.id=zfs_rep_frequency.zfs_id ' + \
				'and local_host=nodes.id and nodes.name="%s"' % host

			if local_fs:
				sql_string = sql_string + \
					' and local_fs="%s"' % local_fs
			if remote_host:
				sql_string = sql_string + \
					' and remote_host="%s"' % remote_host
			if remote_fs:
				sql_string = sql_string + \
					' and remote_fs="%s"' % remote_fs

			self.db.execute(sql_string)
