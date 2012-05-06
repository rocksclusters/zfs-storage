# $Id: __init__.py,v 1.2 2012/05/06 05:49:54 phil Exp $

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
# Revision 1.2  2012/05/06 05:49:54  phil
# Copyright Storm for Mamba
#
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

class Command(rocks.commands.report.host.Command):
	"""
	Prints out machine readable authorized_keys file
	for the ZFS user
	<arg type="string" name="host">
	Hostname of the replica server
	</arg>
	"""
	def run(self, params, args):

		hosts = self.getHostnames(args)
		if len(hosts) > 1:
			self.abort("Must supply one host only")
			
		host = hosts[0]

		self.db.execute(
			'select zfs_keys.public_key, zfs_keys.user from ' + \
			'zfs_keys, nodes where zfs_keys.host=nodes.id and'+ \
			' nodes.name="%s"' % host)

		user_keys = {}
		for (pkey, user) in self.db.fetchall():
			if not user_keys.has_key(user):
				user_keys[user] = []
			user_keys[user].append(pkey)

		self.beginOutput()
		for user in user_keys:
			self.addText('<file ' +\
				'name="/opt/rocks/thumper/%s/.ssh/authorized_keys"' % user +\
			 	' owner="%s:sys">\n' % user)
			for key in user_keys[user]:
				self.addText(key + '\n')
			self.addText('</file>\n')

		self.endOutput()
