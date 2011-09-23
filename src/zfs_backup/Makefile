# --------------------------------------------------- -*- Makefile -*- --
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
# Revision 1.4  2009/10/16 20:04:08  phil
# set permissions so that members of sys group can execute backup script
#
# Revision 1.3  2009/10/12 15:41:24  phil
# Added Edmond's/NCMIR trimSnapshots
#
# Revision 1.2  2009/05/22 06:49:00  anoop
# Moved permissions script out of xml file, which was
# causing XML errors during jumpstart generation.
#
# Revision 1.1  2008/09/25 00:16:33  anoop
# Major checkin for replication.\n zfs_backup is now a new package that builds on Solaris only.\n
#
#

PKGROOT		= /opt/rocks
REDHAT.ROOT     = $(CURDIR)/../../
-include $(ROCKSROOT)/etc/Rules.mk
include Rules.mk
	
build: 

install::
	mkdir -p $(ROOT)/$(PKGROOT)/sbin
	mkdir -p $(ROOT)/$(PKGROOT)/thumper/
	$(INSTALL) -m0750 -g sys zfs-backup.pl $(ROOT)/$(PKGROOT)/sbin/zfs-backup
	$(INSTALL) -m0750 -g sys trimSnapshots.pl $(ROOT)/$(PKGROOT)/sbin/trimSnapshots
	$(INSTALL) -m0755 -g sys zfs-perms-setup.sh $(ROOT)/$(PKGROOT)/thumper/zfs-perms-setup.sh

clean::
