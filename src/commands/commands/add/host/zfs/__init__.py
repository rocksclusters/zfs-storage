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
# Revision 1.2  2010/09/02 22:05:24  anoop
# Cleanup & Bug fix
# Make sure we don't have duplicated entries in the zfs_keys table
# Add the zfs keys to replica server(remote_host) and not
# replica client(local_host)
#
# Revision 1.1  2009/08/19 02:31:51  anoop
# Major overhaul of the replication infrastructure
# - commands are now moved to
#   <add/list/remove/report>/host/zfs/<key/replica>
#   for consistency
# - major changes to database schema corresponds to
#   the changes in command line
# - cleanup of commands
#

import rocks.commands

class command(rocks.commands.add.host.command):
	pass
