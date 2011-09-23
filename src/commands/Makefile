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

PKGROOT		= /opt/rocks
REDHAT.ROOT     = $(CURDIR)/../../
-include $(ROCKSROOT)/etc/Rules.mk
include Rules.mk
	
build: 

install::
	mkdir -p $(ROOT)/$(PY.ROCKS)/rocks/commands
	(								\
		find . -name "*.py" | 					\
			cpio -pduv $(ROOT)/$(PY.ROCKS)/rocks/commands;	\
	)
	find $(ROOT)/$(PY.ROCKS)/rocks/commands -name "*.py" | gawk	\
		'{ print "\nRollName = \"$(ROLL)\"" >> $$1; }'  
	find $(ROOT) -type d -exec chmod a+rx {} \;

clean::
