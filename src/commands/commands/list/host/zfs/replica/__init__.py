# $Id: __init__.py,v 1.1 2011/09/23 22:17:27 anoop Exp $
# 
# @Copyright@
# @Copyright@
#
# Changes
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
# Revision 1.4  2008/12/19 03:46:02  clem
# First round of tests, patch some minor bugs
#
# Revision 1.3  2008/12/16 20:38:09  clem
# New version of the thumper replica sysetm with remote filesystem
#
# Revision 1.2  2008/10/16 00:49:52  anoop
# Cleanup of replication commands
# Changed xml files to work correctly on a linux frontend
#
# Revision 1.1  2008/09/25 00:16:33  anoop
# Major checkin for replication.\n zfs_backup is now a new package that builds on Solaris only.\n
#
# Revision 1.2  2008/09/17 21:02:55  clem
# there was a typo in the log cvs keyword ($Log: __init__.py,v $
# there was a typo in the log cvs keyword (Revision 1.1  2011/09/23 22:17:27  anoop
# there was a typo in the log cvs keyword (Renamed thumper-conf roll as ZFS storage roll
# there was a typo in the log cvs keyword (and included in the mainline rocks tree
# there was a typo in the log cvs keyword (
# there was a typo in the log cvs keyword (Revision 1.1  2009/08/19 02:31:52  anoop
# there was a typo in the log cvs keyword (Major overhaul of the replication infrastructure
# there was a typo in the log cvs keyword (- commands are now moved to
# there was a typo in the log cvs keyword (  <add/list/remove/report>/host/zfs/<key/replica>
# there was a typo in the log cvs keyword (  for consistency
# there was a typo in the log cvs keyword (- major changes to database schema corresponds to
# there was a typo in the log cvs keyword (  the changes in command line
# there was a typo in the log cvs keyword (- cleanup of commands
# there was a typo in the log cvs keyword (
# there was a typo in the log cvs keyword (Revision 1.4  2008/12/19 03:46:02  clem
# there was a typo in the log cvs keyword (First round of tests, patch some minor bugs
# there was a typo in the log cvs keyword (
# there was a typo in the log cvs keyword (Revision 1.3  2008/12/16 20:38:09  clem
# there was a typo in the log cvs keyword (New version of the thumper replica sysetm with remote filesystem
# there was a typo in the log cvs keyword (
# there was a typo in the log cvs keyword (Revision 1.2  2008/10/16 00:49:52  anoop
# there was a typo in the log cvs keyword (Cleanup of replication commands
# there was a typo in the log cvs keyword (Changed xml files to work correctly on a linux frontend
# there was a typo in the log cvs keyword (
# there was a typo in the log cvs keyword (Revision 1.1  2008/09/25 00:16:33  anoop
# there was a typo in the log cvs keyword (Major checkin for replication.\n zfs_backup is now a new package that builds on Solaris only.\n
# there was a typo in the log cvs keyword ()
#
#

import rocks.commands

class Command(rocks.commands.list.host.command):
	"""
	Lists the the replica that are currently configured

	<arg optional='1' type='string' name='host' repeat='1'>
	Zero, one or more host names. If no host names are supplied,
	info about all the known hosts is listed.
	</arg>

	<example cmd='list host replica compute-0-0'>
	List replicas that are configured for compute-0-0.
	</example>

	<example cmd='list host replica'>
	List all the configured replica on this cluster
	</example>
	"""

	def run(self, params, args):
		self.beginOutput()

		for host in self.getHostnames(args):
			self.db.execute('select z.id, n.name, z.local_fs, ' + \
				'z.remote_host, z.remote_fs, z.remote_user, ' + \
				'f.cron_string, z.maxBackup from ' + \
				'zfs_replication z, nodes n, zfs_rep_frequency f ' + \
				'where z.local_host=n.id and n.name="%s" ' % host + \
				'and z.id=f.zfs_id')
			for row in self.db.fetchall():
				self.addOutput(host, row)

		self.endOutput(header=['host', 'id','host', 'local_fs', 
			'remote_host', 'remote_fs', 'remote_user', 
			'crontab','maxBackup'], trimOwner=1)
