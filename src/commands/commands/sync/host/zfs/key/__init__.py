# $Id: __init__.py,v 1.1 2011/09/23 22:17:27 anoop Exp $

# @Copyright@
# @Copyright@

# $Log: __init__.py,v $
# Revision 1.1  2011/09/23 22:17:27  anoop
# Renamed thumper-conf roll as ZFS storage roll
# and included in the mainline rocks tree
#
# Revision 1.3  2010/10/08 21:51:54  anoop
# Cleanup. Moved zfs key syncing to it's own command
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
import sys

class Command(rocks.commands.sync.host.command,
	rocks.commands.HostArgumentProcessor):
	"""
	This command logs into replication servers,
	and creates relevant authorized_keys files
	so that replication clients can log in without
	passwords
	"""
	def run(self, params, args):	
		if len(args) > 0:
			hosts = self.getHostnames(args)
		else:
			self.db.execute('select distinct n.name from '	+\
				'from zfs_keys z, nodes n where '	+\
				'zfs_keys.local_host=nodes.id')
			hosts = self.db.fetchall()
			f = lambda(x): x[0]
			hosts = map(f, hosts)
		# For every host.....
		for host in hosts:
			# Obtain the authorized_keys file contents
			auth_key_file = self.command(		\
					'report.host.zfs.key',	\
					[host])

			# Convert xml to executable shell commands
			p = Popen(['/opt/rocks/bin/rocks', 'report', 'script'],\
				stdin=PIPE, stdout=PIPE)
			shell_cmd = p.communicate(auth_key_file)[0]

			# SSH into the replication server and execute the
			# reported shell commands
			p1 = Popen(['ssh','-T','root@%s' % host], stdin=PIPE, \
				stdout=PIPE, stderr=PIPE)
			(p1_stdout, p1_stderr) = p1.communicate(shell_cmd)
			if p1.returncode != 0:
				print '################# BEGIN %s ##################' % host
				sys.stdout.write(p1_stderr)
				print '################# END %s ##################' % host
