#!/bin/bash

# $Id: zfs-perms-setup.sh,v 1.2 2011/10/07 22:52:40 anoop Exp $

# $Log: zfs-perms-setup.sh,v $
# Revision 1.2  2011/10/07 22:52:40  anoop
# Bug fix. Change permissions of only the recipient filesystem
#

# This script configures zfs permissions for the 
# replication user created as part of the ROCKS 
# ZFS-storage roll

# Usage
if [ "$1" == "" ]; then
        echo "Usage: $0 <zfs filesystem>"
        exit
fi

# ZFS user should exist as part of the roll
ZFS_USER="zfsuser"
ZFS_PERM_SET="@replication"
ZFS_FILESYSTEM=$1

ZFS_MOUNT=`zfs get -H -o value mountpoint $ZFS_FILESYSTEM`

# Set permissions
/bin/chmod A+user:$ZFS_USER:add_subdirectory:fd:allow $ZFS_MOUNT
/sbin/zfs allow -s $ZFS_PERM_SET \
	create,destroy,mount,receive,send,snapshot $ZFS_FILESYSTEM
/sbin/zfs allow $ZFS_USER $ZFS_PERM_SET $ZFS_FILESYSTEM
