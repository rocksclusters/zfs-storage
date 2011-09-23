# $Id: plugin_perms.py,v 1.1 2011/09/23 22:17:27 anoop Exp $

# @Copyright@
# @Copyright@

# $Log: plugin_perms.py,v $
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
import string
import sys
from subprocess import Popen, PIPE

class Plugin(rocks.commands.Plugin):

	def provides(self):
		return "perms"

	def run(self, host):
		self.owner.db.execute('select z.local_fs from ' +\
			'zfs_replication z, nodes n where '	+\
			'n.name="%s" and z.local_host=n.id' % host)

		cmd = '/opt/rocks/thumper/zfs-perms-setup.sh'
		for (localfs,) in self.owner.db.fetchall():
			cmd_line = string.join([cmd,localfs],' ') + '\n'

		p = Popen(['ssh','-T','-q','root@%s' % host], stdin=PIPE, \
			stdout=PIPE, stderr=PIPE)
		(p_stdout, p_stderr) = p.communicate(cmd_line)
		if p.returncode != 0:
			print '############### BEGIN %s ##################' % host
			print p_stderr
			print '################# END %s ##################' % host
