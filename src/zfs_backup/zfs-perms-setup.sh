#!/bin/bash

# $Id: zfs-perms-setup.sh,v 1.3 2011/10/16 07:03:28 anoop Exp $

# $Log: zfs-perms-setup.sh,v $
# Revision 1.3  2011/10/16 07:03:28  anoop
# Additional permissions given to zfsuser to
# backup zfs snapshots correctly
#
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
ZFS_PERM_SPEC="create,destroy,mount,receive,send,snapshot,hold,release"
ZFS_FILESYSTEM=$1

ZFS_MOUNT=`zfs get -H -o value mountpoint $ZFS_FILESYSTEM`

# ACL specification
ACL_SET="add_subdirectory/add_file/delete/delete_child/list_directory"
ACL_INHERIT="fd"

# Set permissions
# Add permissions to zfsuser only if they don't exist
ls -dv $ZFS_MOUNT | grep user:$ZFS_USER > /dev/null
if [ $? -ne 0 ]; then 
	/bin/chmod A+user:$ZFS_USER:$ACL_SET:$ACL_INHERIT:allow $ZFS_MOUNT
fi
/sbin/zfs allow -s $ZFS_PERM_SET $ZFS_PERM_SPEC $ZFS_FILESYSTEM
/sbin/zfs allow $ZFS_USER $ZFS_PERM_SET $ZFS_FILESYSTEM
