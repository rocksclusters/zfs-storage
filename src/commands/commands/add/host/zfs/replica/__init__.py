# $Id: __init__.py,v 1.5 2012/12/14 06:10:44 phil Exp $
#
# @Copyright@
# 
# 				Rocks(r)
# 		         www.rocksclusters.org
# 		         version 5.6 (Emerald Boa)
# 		         version 6.1 (Emerald Boa)
# 
# Copyright (c) 2000 - 2013 The Regents of the University of California.
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
# Revision 1.5  2012/12/14 06:10:44  phil
# changes to support zfs on linux. revert replication user to root until delegation and extended acls works
#
# Revision 1.4  2012/11/27 00:49:43  phil
# Copyright Storm for Emerald Boa
#
# Revision 1.3  2012/05/06 05:49:54  phil
# Copyright Storm for Mamba
#
# Revision 1.2  2011/10/16 07:03:27  anoop
# Modify the way cron values are checked.
#
# Revision 1.1  2011/09/23 22:17:27  anoop
# Renamed thumper-conf roll as ZFS storage roll
# and included in the mainline rocks tree
#
# Revision 1.3  2010/09/02 22:05:24  anoop
# Cleanup & Bug fix
# Make sure we don't have duplicated entries in the zfs_keys table
# Add the zfs keys to replica server(remote_host) and not
# replica client(local_host)
#
# Revision 1.2  2010/08/30 18:46:11  anoop
# When a replica is added, log in to the client and fetch the zfsuser ssh key
# automatically if possible. This saves the administrator a step in the process
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
# Revision 1.7  2009/06/23 02:22:08  clem
# fixed the input arguments of add rocks replica
#
# Revision 1.6  2009/06/05 19:06:51  clem
# the maxSnaps is not currently implemented...
# I updated the documentation of the command line to report this
#
# Revision 1.5  2008/12/19 03:46:02  clem
# First round of tests, patch some minor bugs
#
# Revision 1.4  2008/12/16 20:38:09  clem
# New version of the thumper replica sysetm with remote filesystem
#
# Revision 1.3  2008/10/20 23:02:19  clem
#
# Changed the frequency parameter to handle only daily weekly monthly values
#
# clem
#
# Revision 1.2  2008/10/16 00:49:51  anoop
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
import re
import rocks.commands
from subprocess import Popen, PIPE

class Command(rocks.commands.HostArgumentProcessor, rocks.commands.add.command):
	"""
	Adds a zfs replication to a host and
	sets the associated values 

	<arg type='string' name='host'>
	Host name of replication client
	</arg>
	
	<param type='string' name='local_fs'>
	The name of the zfs file system that has to be backed up
	</param>
	
	<param type='string' name='remote_host'>
	Hostname of the replication server. This machine
	must be running a zfs file system.
	</param>

	<param type='string' name='remote_fs'>
	Remote ZFS filesystem to hold the backup data. If not present 
	default is export.
	The remote zfs filesytem path must point to the first level of 
	the remote zfs where the user wants to place the data. No 
	starting trailing slash, the backup system uses its own directory 
	structure. With the example below data will be
	placed on /zfspool1/backup/&lt;hostname&gt;/&lt;currentdate&gt;/snapshot
	</param>

	<param type='string' name='remote_user' optional='1'>
	Remote user. This is the username for logging in
	to the remote host. This is to be supplied by the
	system administrator of the remote host. This parameter
	is optional and defaults to 'root'
	</param>

	<param type='string' name='frequency' optional='1'>
        This parameter specifies the frequency of backup 
	of the zfs file system in question.
	Optional parameter - defaults to 'daily'
	This parameter can be: daily, weekly, monthly or a
	crontab string in the form of 'm h D M d', ie.
	(minute, hour, day, month, day of week). See crontab(5)
	for more information about format.
	</param>

	<param type='string' name='maxBackup'>
	This parameters is not implemented yet, it will be ignored.
	Maximum number of snapshots of you data will be kept.
	If not specified the default value is 100.
	</param>
	
        <example cmd='add host replica storage-0 local_fs=export/data
	remote_host=storage-1 remote_fs=zfspool1 frequency="daily" maxBackup=10'>
        This command specifies that the file system export/data on 
	the node storage-0 will be replicated to storage-1
        at midnight every day, keeping 10 differential backups.
        </example>
	"""

	def run(self, params, args):

		(local_fs, remote_host, remote_fs, 
			remote_user, frequency, maxBackup) = self.fillParams(
			[('local_fs', ),
			('remote_host', ),
			('remote_fs', ),
			('remote_user',),
			('frequency', ),
			('maxBackup', )])

		hosts = self.getHostnames(args)
		
		if not local_fs:
			self.abort('Local file system name missing. Please specify')
		
		if not remote_host:
			self.abort('missing remote_host parameter')
		if not remote_fs:
			remote_fs = ''

		if not remote_user:
			remote_user='root'
			
		if not frequency:
			frequency = 'daily'

		if not maxBackup:
			maxBackup = 100

		if len(hosts) != 1:	
			self.abort('must supply only one host')
		local_host = hosts[0]

		# Define a Hash table to translate between frequency mentioned
		# on the command line, and something that crontab can understand
		freq_to_cron = {
			'daily' : '02 4 * * *',
			'weekly': '22 4 * * 0',
			'monthly':'42 4 1 * *',
		}

		# If the user specifies a cron string and not one of the
		# pre-set values, then put the cron string in the database.
		# as a user specified string. Here we do not check the sanity
		# of the crontab string
		if not freq_to_cron.has_key(frequency):
			if not self.check_cron_string(frequency):
				self.abort("frequency parameter is not correct. Please refer to help")
			freq_to_cron['user_specified'] = frequency
			frequency = 'user_specified'
		# create the entry for replication
		self.db.execute(
			"""insert into zfs_replication 
			(local_host, local_fs, 
			remote_host, remote_fs, remote_user,
			maxBackup)
			values (
			(select id from nodes where name="%s"),
			'%s', '%s', '%s', '%s', %d)"""
			% (local_host, local_fs, 
			remote_host, remote_fs, remote_user,
			int(maxBackup)))

		# Get the just inserted ID to use in frequency table
		i_id = self.db.database.insert_id()
		
		sql_cmd = 'insert into zfs_rep_frequency '  + \
			' (zfs_id, frequency, cron_string)' + \
			' values (%d, "%s", "%s")'	\
			% (i_id, frequency, freq_to_cron[frequency])

		self.db.execute(sql_cmd)

		# Get the ssh public key of the zfs replication client
		# XXX: look at this when ZFS on Linux supports extended ACLs
		#      replication currently done as root
		if 0 == 1:
			ssh_key = self.get_ssh_key(local_host)
			if ssh_key is None:
				self.abort("Could not get ssh public key for %s\n" % local_host +\
					"Add public key manually using 'rocks add host zfs key'\n" +\
					"and sync keys using 'rocks sync host zfs key'")
			self.command('add.host.zfs.key',[remote_host, 
							'key=%s' % ssh_key,
							'user=%s' % remote_user])

	def check_cron_string(self, freq):
		cron_string = freq.split()
		# Check to make sure minimum number of cron elements
		# are present.
		if len(cron_string) != 5:
			return False
		
		# Define cron limits in order (m, h, D, M, d)
		cron_limit = [
			(0,59), # Minutes
			(0,23), # Hours
			(1,31), # Day Of Month
			(1,12), # Month
			(1,7),  # Day of Week
			]
		# This regexp catches *, */2, */3, etc.
		re_m = re.compile("^\*(\/[0-9]+)*$")

		# This regexp catches integers >= 0
		re_c = re.compile("^[0-9]+(,[0-9]+)*$")
		for i in range(5):
			if(re_m.match(cron_string[i]) == None):
				if (re_c.match(cron_string[i]) == None):
					return False
				if (int(cron_string[i])) > (cron_limit[i][1]):
					return False
				if (int(cron_string[i])) < (cron_limit[i][0]):
					return False
			
		return True

	def get_ssh_key(self, host):
		p = Popen(['ssh','-T','-o NumberOfPasswordPrompts=0', host,\
			'cat /opt/rocks/thumper/zfsuser/.ssh/id_dsa.pub'], \
			stdin=PIPE, stdout=PIPE, stderr=PIPE)

		err_code = p.wait()
		if (err_code != 0):
			print "Returned Error code: %d" % p.poll()
			print p.communicate()[1].strip()
			return None
		key = p.communicate()[0].strip()
		return key
