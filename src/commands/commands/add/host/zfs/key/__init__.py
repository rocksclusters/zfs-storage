# $Id: __init__.py,v 1.1 2011/09/23 22:17:27 anoop Exp $

# @Copyright@
# @Copyright@

# $Log: __init__.py,v $
# Revision 1.1  2011/09/23 22:17:27  anoop
# Renamed thumper-conf roll as ZFS storage roll
# and included in the mainline rocks tree
#
#

import rocks.commands
import os
import tempfile
import subprocess

class Command(rocks.commands.HostArgumentProcessor, rocks.commands.add.command):
	"""
	This command adds an external public key of a replication client
	that needs to connect to an internal replication server.
	
	<arg type='string' name='host'>
	A single hostname. This is the replication server to which you want
	the particular replication host to connect to. Omitting the hostname 
	will add it to all the NAS appliances that are part of the cluster.
	</arg>

	<param type='string' name='key' optional='0'>
	The public key that needs to be added to the authorized_keys file
	on the replication server.
	</param>

	<param type='string' name='user' optional='1'>
	The username to be used on the replication server. Optional parameter
	Defaults to 'zfsuser'
	</param>

	<example cmd='add host zfs key nas-0-0 user=zfsuser_rocks key="ssh-dss AAAAB3NzaC1kc3MAAAEBAPjJJaJOyV3eCLFU8AzV4pewDlEcj6NUHUYXPLaXLNmr0mNXLCfryvR+LZEmDJJ4kRiDNVzPCkPkOOEDPZI710/0sENVWNAD1LY8yR5ecclgEDBUWAdkMGp4LcMDeQc16VKfpp+nJ23RV9NO8/lpZ80uTHsGv5Wry0hIlHHnqbugI44sxt2SgSY/DD7bVP3qFymp6BM98uEP6X55FsjU5cQHYqEI8offxGb8j7Ehbqf3rJ+14Nq5dR0BKtvzd7k16sWomOZDqNPHiR1WYU+x98gwU0hlv2YKn3GiNbVAWxDKPGZVqFal2DGcl4dq356huS2wcwqDzZxyQYH1IvMLGF8AAAAVAPYuMyFOIANhs2RZob4tYObFfEYlAAABAQC8kNQmvTVpG3yD+xgOTXF3dCsM5b07sXnG536m40WzcSKOuREmM4FBvV9X8/uMKH8d0q0y2+M4iSNNwxP9lvACBtiaMrje1R/q7N98izZKPd+vJGu9H3bOd3bMaDShP2Ll4UJ6tX4sNLDYnUaSV8oFr8R54kb65eO1XmtH8Sy77bwyStP8qpVJuApYheMJ6PA4icg2430PzsnNngNAhu1LcLb3ID8xwYDKdVxKa5RnjmmpGqY9OW11YNJWl3dr9Qx0vcZgznCvP7KuaXusfTmLVok7qWtrOEIR5XckwPyVbtfXuURh+uylS+YNw1ta6LBgRl4DRlYckJWTOuMZUn2bAAABAQCm54LRS85QOhpfr28lbXbwP00KxIQ8z2yLJGSDQQbO9IyH3he4nhfZHh2rF1zEZUvQfJM+sXT4pR4XfBQd3PLFfIcS50T+Ewvx+ENLciC4P/nDY73hkPoKnW/YtqBEkK9BqFqc1+0Wk4lKtdfP5CuNBLiRSe/Zxh1IHkd+gmE0Jf8sZW0Zy2NKc9JxVIo0KxqNjdP4OD7+l/COtS9m+O62eh0kvjNdPkiwfzLIa9ZDL3Lf3TGUGfx6SWtmU9lVt2PI9lTmOnufDY9Sct2Fa7p4e45u5dFN/3jSaWYecKWvQOiIkA6RX065mUF4sUOeJgrGtz8h9ExD3EFLDiNHbP2G zfsuser@nas-2-1.local"'>
	This adds the public key to user zfsuser_rocks@nas-0-0, where nas-0-0 is the replication
	server.
	</example>

	<related>list host zfs key</related>
	<related>remove host zfs key</related>
	<related>sync host zfs key</related>
	<related>report host zfs key</related>
	"""

	def run(self, params, args):
		(user, key) = self.fillParams([
			('user','zfsuser'),
			('key',)
		])
		hosts = self.getHostnames(args)

		if not key:
			self.abort('Please provide public key')

		f = tempfile.mktemp()
		key_file = open(f,'w')
		key_file.write(key + '\n')
		key_file.close()
		s = subprocess.Popen(['ssh-keygen','-l','-f', f], stdout=subprocess.PIPE).stdout
		fingerprint = s.readline().strip().split()[1]
		os.unlink(f)
		for host in hosts:
			r = self.db.execute('select * from zfs_keys, nodes '	+\
					'where nodes.name="%s" and ' % (host)	+\
					'zfs_keys.host=nodes.id and '		+\
					'fingerprint="%s"' % (fingerprint))
			if (r != 0):
				continue

			self.db.execute(
				'insert into zfs_keys ' +\
				'(host, user, public_key, fingerprint) values' +\
				'((select id from nodes where name="%s"),"%s", "%s", "%s")'
				% (host, user, key, fingerprint))
