# $Id: Makefile,v 1.1 2011/09/23 22:17:26 anoop Exp $
#
# @Copyright@
# @Copyright@
#
# $Log: Makefile,v $
# Revision 1.1  2011/09/23 22:17:26  anoop
# Renamed thumper-conf roll as ZFS storage roll
# and included in the mainline rocks tree
#
# Revision 1.2  2008/09/25 00:16:33  anoop
# Major checkin for replication.\n zfs_backup is now a new package that builds on Solaris only.\n
#
# Revision 1.1  2008/07/16 18:12:46  anoop
# Skeleton thumper roll
#

-include $(shell $(ROCKSROOT)/bin/os).mk
-include $(shell $(ROCKSROOT)/bin/arch).mk

default:	pkg

copyright pkg rpm clean::
	for i in $(SRCDIRS) ; do \
		(cd $$i; $(MAKE) $@) ; \
	done
