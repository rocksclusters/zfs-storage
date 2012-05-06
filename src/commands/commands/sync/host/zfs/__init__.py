# $Id: __init__.py,v 1.3 2012/05/06 05:49:54 phil Exp $

# @Copyright@
# 
# 				Rocks(r)
# 		         www.rocksclusters.org
# 		         version 5.5 (Mamba)
# 		         version 6.0 (Mamba)
# 
# Copyright (c) 2000 - 2012 The Regents of the University of California.
# All rights reserved.	
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
# notice unmodified and in its entirety, this list of conditions and the
# following disclaimer in the documentation and/or other materials provided 
# with the distribution.
# 
# 3. All advertising and press materials, printed or electronic, mentioning
# features or use of this software must display the following acknowledgement: 
# 
# 	"This product includes software developed by the Rocks(r)
# 	Cluster Group at the San Diego Supercomputer Center at the
# 	University of California, San Diego and its contributors."
# 
# 4. Except as permitted for the purposes of acknowledgment in paragraph 3,
# neither the name or logo of this software nor the names of its
# authors may be used to endorse or promote products derived from this
# software without specific prior written permission.  The name of the
# software includes the following terms, and any derivatives thereof:
# "Rocks", "Rocks Clusters", and "Avalanche Installer".  For licensing of 
# the associated name, interested parties should contact Technology 
# Transfer & Intellectual Property Services, University of California, 
# San Diego, 9500 Gilman Drive, Mail Code 0910, La Jolla, CA 92093-0910, 
# Ph: (858) 534-5815, FAX: (858) 534-7345, E-MAIL:invent@ucsd.edu
# 
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# @Copyright@

# $Log: __init__.py,v $
# Revision 1.3  2012/05/06 05:49:54  phil
# Copyright Storm for Mamba
#
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
