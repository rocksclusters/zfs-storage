#
# $Id: Makefile,v 1.3 2012/11/27 00:49:44 phil Exp $
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
# $Log: Makefile,v $
# Revision 1.3  2012/11/27 00:49:44  phil
# Copyright Storm for Emerald Boa
#
# Revision 1.2  2012/05/06 05:49:54  phil
# Copyright Storm for Mamba
#
# Revision 1.1  2011/09/23 22:17:26  anoop
# Renamed thumper-conf roll as ZFS storage roll
# and included in the mainline rocks tree
#
# Revision 1.2  2010/04/03 03:33:53  phil
# update smartmontools to build on latest Solaris
#
# Revision 1.1  2009/11/14 00:32:13  phil
# Add smartmontools so that we can look at SATA drive low-level health info
#
# Revision 1.5  2009/06/27 00:49:52  anoop
# Enable linux build for socat
#
# Revision 1.4  2009/06/24 18:53:31  anoop
# Bug fix. Don't use PWD. Use CURDIR instead
#
# Revision 1.3  2009/06/24 18:35:57  anoop
# Bug fix
#
# Revision 1.2  2009/06/24 18:33:33  anoop
# Added socat to roll build
#
# Revision 1.1  2009/06/24 05:26:31  phil
# socat (updated netcat).
#
# Revision 1.14  2007/06/23 04:03:52  mjk
# mars hill copyright
#
# Revision 1.13  2006/12/06 22:23:02  bruno
# new
#
#

PKGROOT		= /opt/$(NAME)
REDHAT.ROOT     = $(CURDIR)/../../

-include $(ROCKSROOT)/etc/Rules.mk
include Rules.mk

build:
	gunzip -c $(NAME)-$(VERSION).tar.gz | $(TAR) xvf -
	(					\
		cd $(NAME)-$(VERSION);		\
		./configure --prefix=$(PKGROOT);\
		$(MAKE);			\
	)


install::
	mkdir -p $(ROOT)/$(PKGROOT)
	mkdir -p $(ROOT)/$(INIT_SCRIPTS_DIR)
	(				\
		cd $(NAME)-$(VERSION);	\
		$(MAKE) prefix=$(ROOT)/$(PKGROOT) \
			install;	\
	)
	$(INSTALL) -m0755 sunos/smartd   $(ROOT)/$(INIT_SCRIPTS_DIR)/smartd
	$(INSTALL) -m0644 sunos/smartd.xml $(ROOT)/$(PKGROOT)/share/smartd.xml

clean::
	rm -rf $(NAME)-$(VERSION)
