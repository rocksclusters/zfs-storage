# $Id: __init__.py,v 1.2 2012/05/06 05:49:54 phil Exp $
# 
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
#
# $Log: __init__.py,v $
# Revision 1.2  2012/05/06 05:49:54  phil
# Copyright Storm for Mamba
#
# Revision 1.1  2011/09/23 22:17:27  anoop
# Renamed thumper-conf roll as ZFS storage roll
# and included in the mainline rocks tree
#
# Revision 1.3  2009/10/15 20:38:13  anoop
# We learn something new everyday. All crontab files need to
# have permissions 0600 root:sys
#
# Revision 1.2  2009/08/25 21:24:16  anoop
# Minor bug fix. Don't output anything for hosts that don't exist in
# the zfs_replication table
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
# Revision 1.3  2009/06/05 19:06:51  clem
# the maxSnaps is not currently implemented...
# I updated the documentation of the command line to report this
#
# Revision 1.2  2008/12/16 20:38:09  clem
# New version of the thumper replica sysetm with remote filesystem
#
# Revision 1.1  2008/10/20 23:08:05  clem
# Moved config to replica and added necessary code to handle properly the
# daily weekly monthly crontab script
#
# Revision 1.2  2008/10/16 00:49:52  anoop
# Cleanup of replication commands
# Changed xml files to work correctly on a linux frontend
#
# Revision 1.1  2008/09/25 00:16:33  anoop
# Major checkin for replication.\n zfs_backup is now a new package that builds on Solaris only.\n
#
# Revision 1.2  2008/09/17 21:29:29  clem
# Now the sshKeyPath is an optional parameter...
#
# Revision 1.1  2008/09/17 21:00:28  clem
# config command for the replica of thumper
#
# clem
#
#
#

import rocks.commands

class Command(rocks.commands.report.host.command):
	"""
	Output the crontab entries necessary to configure 
	the replica between thumpers for a specific hosts.

	<arg type='string' name='host'>
	One host name.
	</arg>

	<example cmd='report host replica thumper-0-0 '>
	Output all the contab entries that have to be 
	installed on thumper-0-0 to perform the 
	configured backups
	</example>
	"""


	def run(self, params, args):
		#change this path accorndingly
		replicaScriptPath = '/opt/rocks/sbin/zfs-backup'
		crontab		= '/var/spool/cron/crontabs/zfsuser'

		local_fs	=	None
		local_host	=	None

		remote_user	=	None
		remote_host	=	None
		remote_fs	=	None

		frequency	=	None
		maxBackup	=	None

		# only takes one host
		#
		hosts = self.getHostnames(args)
		if len(hosts) != 1:
			self.abort('Must supply a single host')
		local_host = hosts[0]


		sql_cmd = 'select z.local_fs, ' + \
			'z.remote_user, z.remote_host, z.remote_fs, ' +\
			'z.maxBackup, f.cron_string from ' + \
			'zfs_replication z, nodes n, zfs_rep_frequency f ' + \
			'where z.local_host=n.id and n.name="%s" ' % local_host +\
			'and f.zfs_id=z.id'

		rows = self.db.execute(sql_cmd)
		if rows == 0:
			return

		self.beginOutput()
		self.addText('<file name="%s" perms="0600" owner="root:sys">\n' % (crontab))
		self.addText('## ZFS Replication ##\n')
		for (local_fs, remote_user, remote_host, remote_fs, \
			maxBackup, cron_string) in self.db.fetchall():
			commandLine = replicaScriptPath + \
				" -z " + local_fs	+ \
				" -u " + remote_user	+ \
				" -r " + remote_host	+ \
				" -f " + remote_fs

			commandLine = cron_string + ' ' + commandLine
			self.addText(commandLine + '\n')

		self.addText('</file>\n')
		self.endOutput()
