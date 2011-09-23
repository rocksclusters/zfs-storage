# $Id: __init__.py,v 1.1 2011/09/23 22:17:27 anoop Exp $

# @Copyright@
# @Copyright@

# $Log: __init__.py,v $
# Revision 1.1  2011/09/23 22:17:27  anoop
# Renamed thumper-conf roll as ZFS storage roll
# and included in the mainline rocks tree
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

class Command(rocks.commands.sync.host.command,
	rocks.commands.HostArgumentProcessor):
	"""
	This command creates the crontab script for 
	the zfsuser on the replication clients
	"""
	def run(self, params, args):

		hosts = self.getHostnames(args)

		# Iterate over the hosts, and populate the zfsuser crontab
		for host in hosts:
			cron_file = self.command(		\
				'report.host.zfs.replica',	\
				[host])

			# Convert xml to executable shell commands
			p = Popen(['/opt/rocks/bin/rocks', 'report', 'script'],\
				stdin=PIPE, stdout=PIPE)
			shell_cmd = p.communicate(cron_file)[0]

			# SSH into the replication server and execute the
			# reported shell commands
			p1 = Popen(['ssh','-T','root@%s' % host], stdin=PIPE, \
				stdout=PIPE, stderr=PIPE)
			(p1_stdout, p1_stderr) = p1.communicate(shell_cmd)
			if p1.returncode != 0:
				print '################# BEGIN %s ##################' % host
				sys.stdout.write(p1_stderr)
				print '################# END %s ##################' % host
