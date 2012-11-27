# $Id: plugin_key.py,v 1.3 2012/11/27 00:49:44 phil Exp $

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

# $Log: plugin_key.py,v $
# Revision 1.3  2012/11/27 00:49:44  phil
# Copyright Storm for Emerald Boa
#
# Revision 1.2  2012/05/06 05:49:54  phil
# Copyright Storm for Mamba
#
# Revision 1.1  2011/09/23 22:17:27  anoop
# Renamed thumper-conf roll as ZFS storage roll
# and included in the mainline rocks tree
#
# Revision 1.3  2010/10/08 21:51:54  anoop
# Cleanup. Moved zfs key syncing to it's own command
#
# Revision 1.2  2010/09/02 22:03:00  anoop
# Bug fix
#
# Revision 1.1  2010/08/30 18:47:24  anoop
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

class Plugin(rocks.commands.Plugin):

	def provides(self):
		return "key"

	def run(self, host):
		# Get a list of all the replication servers the the clients
		# replicate to.
		self.owner.db.execute('select distinct z.remote_host '	+\
			'from zfs_replication z, nodes n where '	+\
			'n.name="%s" and z.local_host=n.id' % host)
		rhosts = self.owner.db.fetchall()
		f = lambda(x): x[0]
		rhosts = map(f, rhosts)

		# Run them through our host argument processor to filter the
		# ones that belong to the cluster
		rhostnames = self.owner.getHostnames(rhosts)

		# Run the sync command through all of them
		self.owner.command('sync.host.zfs.key',rhostnames)
