#!/opt/rocks/bin/perl -w
#
# TODO
# - create semaphore locking for script.
# - create time function for snapshots to aide in uniqueness (remove time calc)
# - polish up the getArgs function and usage description/help function.
#
###############################################################################
## Authors:      Edmond Negado, Luca Clementi
##
## Desription:   ZFS replication script. This replicates zfs filesystems
##               from the local host system to a replicant remote system
##               which is specified in the command line parameter list.
##
## Notes:        This version of zfs-backup.pl runs on the latest version
##               of Solaris 10 10/08 with ZFS Version 10. Please note that
##               there are specific zfs commands which are dependent
##               on ZFS Version 10.
##               This script will not run correctly on later versions of ZFS.
##
###############################################################################
use strict;
use Getopt::Long;
use Socket;

######## USER EDITABLE VARIABLES ##############################################

## Path of the log directory on the local production server. 
my $LOG = "/var/log/zfs-backup";
            
            
## set debug to 1 prints out the cases of backups.
my $debug = 1;

## Set the snapshot backupname
my $SNAPSHOT_PREFIX_NAME = "SNAPSHOT";

###############################################################################
###### Globals DO NOT EDIT                                               ######
###############################################################################

## initialize argument variables to store from getArgs().
my $SSH_IDENT;
my $USER;
my $MAX_SNAPS;
my $BACKUP_SERVER;
my @BACKUP_SOURCES;
my @ZFS_LIST;
my $BACKUP_DIR;
my $SOCAT;

## initialize global status for sucess or failure of zfs commands used
## in subroutines.
my $status = 0;

## initialize status message variable used for subroutines to print
## out error messages from zfs commands.
my $stat_msg = "";

## Set timezone info to PST
$ENV{'TZ'} = "US/Pacific";

###############################################################################
###### Collect the date variables to get the current dates.
###############################################################################

## Get the current and previous date.
my $time_today = time;

### collect the current day variable data.
my @today_arr = localtime ($time_today);
my $today_month = sprintf ("%02d", $today_arr[4] + 1);
my $today_year = sprintf ("%4d", $today_arr[5] + 1900);
my $today_day = sprintf("%02d", $today_arr[3]);

## this is used to name the snapshot we are gonna do the format is
## $SNAPSHOT_PREFIX_NAME-YEAR-MONTH-DAY-EPOC
my $today = $SNAPSHOT_PREFIX_NAME;
$today .= "$today_year-$today_month-$today_day-$time_today"; 

############# START OF SUBROUTINES BE VERY CAREFUL WHEN EDITING ###############
###### Below are the routines that are used to make this script work. Before
###### editing, look at the main() routine to understand how the backup works.
###############################################################################


###############################################################################
## Function: getArgs()
## Description: this function gets the arguments passed from the arguement line
##              and validates them.
## Param/Return: none/array
###############################################################################
sub getArgs {
    ## This function collects the required parameters.
    my ($zfsFilesystem, $help, $keypath, $oflag, $remote, $remoteFilesystem, $maxsnap, $user, $socat);

    ## set the flags for processing
    GetOptions(
                "z=s"=>\$zfsFilesystem,
                "k:s"=>\$keypath,
                "r=s"=>\$remote,
                "f:s"=>\$remoteFilesystem,
                "s:i"=> \$maxsnap,
		"u=s"=>\$user,
		"x"=>\$socat,
                "h"=>\$help
    );

    # print out the usage if the flag was set.
    &usage if ($help);

    ## check if the required variables were set
    if ($zfsFilesystem) {
            if ($remote) {
    		## set default user if none specified
    		if ($user) {
		    # keep user specified
    		} else {
		    # set 'zfsuser' as default
		    $user="zfsuser"
    		}
                if (defined ($maxsnap)) {

                    ## return the valid data as an array
                    return ($zfsFilesystem, $keypath, $remote, $remoteFilesystem, $maxsnap, $user, $socat);

                } else { ## setting the default
                    $maxsnap = 50;
                    return ($zfsFilesystem, $keypath, $remote, $remoteFilesystem, $maxsnap, $user, $socat);
                }
            } else { ## missing remote replication server
                print "Remote server not defined. exiting...\n";
                &usage;
            }
    } else { ## missing zfs filesystem
        print "ZFS Filesystem is not defined. exiting...\n";
        &usage;
    }
}



###############################################################################
## Function: usage()
## Description: This function prints out the usage then exits
## Param/Return: none.
###############################################################################
sub usage {
    ## print out the usage documentation and exit.
    print "\n\tUsage: ./zfs-backup.pl [args]\n";
    print "\tOptions: -z <zfs filesystem to be replicated>\n";
    print "\t         -k </path/to/ssh/key> this paramters is optional\n";
    print "\t         -r <FQDN of replicant host>\n";
    print "\t         -f remote ZFS filesystem to hold the backup data. If not present default is export/backups/\n";
    print "\t         -s <max snapshots to keep> if not present the default is 50\n";
    print "\t         -u <username> if not present the default is 'zfsuser'\n";
    print "\t         -x use socat as transfer medium, default is ssh\n";
    print "\t         -h Display help\n";
    print "\n";
    print "\t-z -r are the only required parameters, the others have a default value.\n";
    print "\n";
    print "\tExample: ./zfs-backup.pl -z export/foo -k /root/key -r z.com -i zfspool1 \n";
    print "\n";
    print "\tThe remote zfs filesytem path must point to the first level of the remote zfs where the user\n";
    print "\twants to place the data. No starting trailing slash. With the previous example data will be\n";
    print "\tplaced on /zfspool1/backup/<hostname>/export/foo\@SNAPSHOT2009-04-08-1239214778 \n";
    exit(1);
}



################################################################################
## Subroutine: checkSnapshotExists()
## Description: checks if any snapshots of the passed in zfs filesystem exists.
## (local) system check subroutine.
## Param/return: zfs filesystem / 1 or null
################################################################################
sub checkSnapshotExists {

    my $fs = shift or die ("checkSnapshotExists(): NO snap specifed to be checked.");
    ## check if there is an existing snapshots, if not we need to create one.
    my $ret_val = system ("/sbin/zfs list -H -r -t snapshot -o name $fs | grep $fs\@$SNAPSHOT_PREFIX_NAME > /dev/null 2>&1");
    ## return true if there are existing snapshots, else return null. 
    ($ret_val == 0) ? return 1 : return ;
}



###############################################################################
## Subroutine: createSnapshot()
## Description: creates the snapshot of the zfs fs on the local/current machine
## (local) system check subroutine.
## Param/return: zfs filesystem / 1 or null
###############################################################################
sub createSnapshot {
    my $fs = shift or die("createSnapshot(): NO zfs filesystem specified.");
    ## create the snapshot
    my $ret_val = system ("/sbin/zfs snapshot $fs\@$today");
    ## set status to return val. and set stat_msg if zfs command failedtatus
    if ($ret_val != 0) {
        $status = $ret_val;
        $stat_msg .= "createSnapshot() - could not create snapshot <$fs\@$today>;";
        return;
    } else {
        return 1;
    }
}



###############################################################################
## Subroutine: getLatestRemoteSnapshotName()
## Desciption: it returns the name of latest remote snapshot
## Param/return: zfs filesystem snapshot name or null
## This function returns 'snapname' NOT 'zfsFilesystem@snapName'
###############################################################################
sub getLatestRemoteSnapshotName{

    my $fs = shift or die("getLatestRemoteSnapshotName(): NO remote zfs filesystem specified.");
    my $snapName = `ssh $SSH_IDENT $USER\@$BACKUP_SERVER \"/sbin/zfs list -H -r -t snapshot -o name $fs | grep $fs\@$SNAPSHOT_PREFIX_NAME | tail -1 \"`;
    ## if value from checking snapshot dne, return null.
    if ( ! $snapName ) { 
        return; 
    }
    ## get the snapshot name and return it.
    my @strArr = split(/@/, $snapName);
    my $returnval = $strArr[1];
    chomp($returnval);
    return $returnval;
}



###############################################################################
## Subroutine: getLatestLocalSnapshotName()
## Desciption: it returns the name of latest local snapshot
## Param/return: zfs filesystem snapshot name or null.
## This function returns 'zfsFilesystem@snapname'
###############################################################################
sub getLatestLocalSnapshotName{

    my $fs = shift or die("getLatestLocalSnapshotName(): NO remote zfs filesystem specified.");
    my $snapName = `/sbin/zfs list -H -r -t snapshot -o name $fs | grep $fs\@$SNAPSHOT_PREFIX_NAME | tail -1`;
    if ( $? ) {
        return;
    } else {
        chomp($snapName);
        return $snapName;
    }
}



###############################################################################
## Subroutine: send_inc_snapshot()
## Desciption: sends the incremental snapshot from the local latest snapshot
## and the remote latest snapshot
## Param/return: zfs filesystem / 1 or null
###############################################################################
sub send_inc_snapshot {
    my $fs = shift or die("send_inc_snapshot(): NO zfs filesystem specified.");

    ## get the local snapshot name  'zfsFilesystem@snapname' we are going to send
    ## This should exist since we call 'createSnapshot()' right before we execute
    ## this function. (this is the latest snapshot on the local system)
    my $local_start = &getLatestLocalSnapshotName($fs);

    ## create the remote zfs filesystem 'rfs' and get the latest snapshot 'snapname'
    my $rfs = "$BACKUP_DIR/$fs";
    my $remote_end_candidate = &getLatestRemoteSnapshotName($rfs); 

    ## check if the snap exists on remote, if not the snapshot dne. need to send full.
    if (! $remote_end_candidate) {
        ## create warning: "remote zfs filesystem and snapshots do not exist.
        ## attempting to send full snap."
        $status = 1; ## set status to 1 for failed incremental send.
        $stat_msg .= "sen_inc_snapshot() - no remote snapshot/zfsFS exist. attempting to full send.";
        ## attempt to send the full snapshot. this doesn't include any past snapshots
        ## if there exists on the local zfs filesystem. return the function sendSnapshot()'s
        ## return value to the calling function if any.
        return &sendSnapshot($fs);
    } 
    
    ## check if there is a possible local end candidate based from the latest remote snapshot
    my $local_end = `/sbin/zfs list -H -r -t snapshot -o name $fs | egrep -e "\^$fs\@$remote_end_candidate\$"`;
    chomp($local_end);

    ## if there is a snapshot on the local system which matches the latest
    ## remote snapshot, attempt to do the incremental send.
    if ($local_end) {
        ## initiate the incremental send over ssh.
        my $ret_val = system ("/sbin/zfs send -I $local_end $local_start | ssh -c blowfish $SSH_IDENT $USER\@$BACKUP_SERVER /sbin/zfs recv -F $rfs");
        ## set status to return val. and set stat_msg if zfs command failed.
        if ($ret_val != 0) {
            $status = $ret_val;
            #
            $stat_msg .= "send_recv_snapshot() - could not send incremental snapshot over ssh <$local_end $local_start>;";
            return;
        } else {
             return 1;
        }
        
    ## TODO if there is no local snapshot copy of the latest remote snapshot,
    ## we need to try all remote copies by iterating through all of the remote
    ## snapshots. if none are found. display warning and exit.
    } else {




    }

} ## end of send_inc_snapshot



###############################################################################
## Subroutine: sendSnapshot()
## Desciption: sends the full current snapshot to the remote server. This is
## used the first time the script is run
##
## Param/return: zfs filesystem / 1 or null
###############################################################################
sub sendSnapshot {
    my $fs = shift or die("sendSnapshot(): NO zfs filesystem specified.");

    ## if user specified -x option, send over socat, otherwise over ssh
    if ($SOCAT) {
	print "Sending snapshot via socat...\n";
        ## initiate the incremental send over socat.
        my $socat_port = get_socat_port();
	my $socat_recv = "ssh $BACKUP_SERVER \'/bin/socat TCP-LISTEN:32000 EXEC:\"zfs recv -F $BACKUP_DIR/$fs\@$today\"\'&";
	    #### DEBUG ####
            print "DEBUG: socat recieve cmd - $socat_recv\n";
	    #### DEBUG ####
        system ($socat_recv);
	# sleep for 3 sec to make sure socat recv is listening
	sleep(3);
	my $socat_send = "/bin/socat TCP:$BACKUP_SERVER:$socat_port EXEC:\"zfs send $fs\@$today\"";
	    #### DEBUG ####
	    print "DEBUG: socat send cmd - $socat_send\n";
	    #### DEBUG ####
	my $ret_val = system ($socat_send);
        ## set status to return val. and set stat_msg if zfs command failed.
        if ($ret_val != 0) {
            $status = $ret_val;
            #
            $stat_msg .= "send_recv_snapshot() - could not send full snapshot over socat <$fs\@$today>;";
            return;
        } else {
             return 1;
        }

    } else {
        ## send the incremental snapshot to remote server over ssh.
        my $ret_val = system ("/sbin/zfs send $fs\@$today | ssh -c blowfish $SSH_IDENT $USER\@$BACKUP_SERVER /sbin/zfs recv -F $BACKUP_DIR/$fs\@$today");

       ## set status to return val. and set stat_msg if zfs command failed.
       if ($ret_val != 0) {
            $status = $ret_val;
            $stat_msg .= "sendSnapshot() - could not send full snapshot <$fs\@$today>;";
            return;
       } else {
            return 1;
       }
    }
    ## set the filesystem readonly on the remote backup server
    ## this is set initially on first full send. if the remote filesystem is not set readonly
    ## we can run into issues with upcoming incremental backups if the atime's change on the
    ## remote server. in zfs version 4, we can use the -F option to force incrementals.
    ## 4/2/2009: removed the '@$today' from $BACKUP_DIR/$fs@$today.
    system("ssh -c blowfish $SSH_IDENT $USER\@$BACKUP_SERVER /sbin/zfs set readonly=on $BACKUP_DIR/$fs");
}


###############################################################################
## Subroutine: verifyRemoteBackup()
## Description: checks to see if remote backup zfs path exists. If not it will
## return null, and cause the script to exit from the calling scope.
## (remote) system check routine.
## Param/return: none/1 or null.
###############################################################################
#sub verifyRemoteBackupPath {
#
#    my $fs = shift or die("remote filesystem not specified.");
#    ## check zfs backup path.
#    ## ie: zpool1/backups/crbsdata7
#    my $ret_val = system ("ssh $SSH_IDENT $USER\@$BACKUP_SERVER /sbin/zfs list | grep $BACKUP_DIR/$fs");
#    
#    ## if successful find, then exit. if not try to build
#    if ($ret_val != 0) {
#        $status = $ret_val;
#        $stat_msg .= "verifyRemoteBackupPath() - Remote backup path does not exist <$BACKUP_DIR>;";
#        return;
#    } else {
#        return 1;
#    }
#} 

###############################################################################
## Subroutine: check_tcp_port()
## Desciption: checks if tcp port is listen on specified host
## Param/return: hostname, port number / 0 (not listening), 1 (listening)
###############################################################################
sub check_tcp_port {
# set time until connection attempt times out
my $timeout = 0;
my $host = shift;
my $port = shift;
my $proto = getprotobyname('tcp');
my $iaddr = inet_aton($host);
my $paddr = sockaddr_in($port, $iaddr);

socket(SOCKET, PF_INET, SOCK_STREAM, $proto) || die "socket: $!";

eval {
  local $SIG{ALRM} = sub { die "timeout" };
  alarm($timeout);
  connect(SOCKET, $paddr) || error();
  alarm(0);
};

if ($@) {
  close SOCKET || die "close: $!";
  #print "$host is NOT listening on tcp port $port.\n";
  return 0;
  exit 1;
}
else {
  close SOCKET || die "close: $!";
  #print "$host is listening on tcp port $port.\n";
  return 1;
  exit 0;
}

} # end check_tcp_port

###############################################################################
## Subroutine: get_socat_port()
## Desciption: returns port number to use for socat: zfs recv
## Param/return: / portnumber or -1 if fails
###############################################################################
sub get_socat_port {
my $count;
        # try port 32000 first, if not available try next port until 32010
        for ($count = 0; $count < 10; $count++) {
             ## set port num
                my $port_num = 3200 . $count;
             ## check if port is in use
                my $in_use = check_tcp_port($BACKUP_SERVER, $port_num);
                if ($in_use) {
                        # port is in use
                        print "port $port_num is in use\n";
                } else {
                        # port is free
                        return $port_num;
                        last;
                }
        }
# no ports found
return -1;
} ## end get_socat_port

###############################################################################
## Subroutine: main()
## Description: runs the main backup script based on the zfs filesystem list.
## This does full and incremental backups to a remote zfs-enabled machine.
## Param/return: none/1 or 0 (success)
###############################################################################
sub main {


    ## collect the arguments, if none exists, exit.
    my ($zfsFilesystem, $keypath, $remote, $remoteFilesystem, $maxsnap, $user, $socat) = &getArgs();

    #TODO NOTURGENT maybe we can check if 
    #1. the user is root 
    #2. zfs is in the path

    ## List/array of backup sources to be backed up.
    @ZFS_LIST = `/sbin/zfs list -rH -o name -t filesystem $zfsFilesystem`;
 
    foreach my $i (@ZFS_LIST) {
        chomp($i);
        push (@BACKUP_SOURCES, $i);
        print "$i\n";
    }

    ## set SSH key path
    if ($keypath) {
        $SSH_IDENT = "-i " . $keypath;
    } else {
        $SSH_IDENT = "";
    }

    ## set the remote zfs replication server
    $BACKUP_SERVER = $remote;
    ## set the remote zfs filename 
    ## The remote backup directory where the zfs backup lives. (no trailing '/')
    chop( my $h = `uname -n`);
    if ( $remoteFilesystem ) {
        $BACKUP_DIR = "$remoteFilesystem/$h"; 
    }else{
        #default if not specified
        $BACKUP_DIR = "export/backups/$h";
    }
    ## set the max snaps, default 50
    $MAX_SNAPS = $maxsnap ? $maxsnap : 50 ;
    ## set ssh username
    $USER = $user;
    ## set socat usage
    $SOCAT = $socat;


    ########## DEBUG #########
     print "max snaps : $MAX_SNAPS\n" if $debug;
     print "backup server: $BACKUP_SERVER\n" if $debug;
     print "ssh key: $SSH_IDENT\n" if $debug;
     print "backup sources @BACKUP_SOURCES\n" if $debug;
    ########## DEBUG #########

    ## create log directory if it does not exist.
    if ( !-d $LOG) {
        system ("mkdir -p $LOG");
    }
      
    ## open and create the log file.
    open (LOGFILE, ">>$LOG/zfs-backup-$today_year-$today_month-$today_day.log");

#TODO don't do this check here, do it in the for loop 
#TODO add: if not present create the remote filesystem
#    if ( ! &verifyRemoteBackupPath() ) {
#
#        print LOGFILE "Error - Remote backup path <$BACKUP_DIR> on: $BACKUP_SERVER does not exist.\n";
#        ## exit script.
#        close(LOGFILE);
#        exit 1;
#    }

    foreach my $backup_src (@BACKUP_SOURCES) {

        ## reset status variable used for testing successful zfs calls.
        $status = 0;

        ## reset stat_msg variable; used for status messages on zfs commands.
        $stat_msg = "";

        ## For each zfsFS, print messages to a file/info variable.
        my $info = "$backup_src:"; 

        ## CASE 1: No snapshots exist.
        if ( ! &checkSnapshotExists($backup_src) ) {
            ## We have to create the first snapshot and send it in
            ## full to the remote host. 

            ###### DEBUG ######
            print "DEBUG: - CASE 1 - createSnapshot($backup_src), sendSnapshot($backup_src)\n" if $debug;
            ###### DEBUG ######

            ## create the snapshot for the current zfs filesystem
            ## If we cannot create a snapshot of the filesystem, we have big probs.
            if ( &createSnapshot($backup_src) != 1) {
                ## display error and exit.
                $info .= "ERROR: Cannot create snapshots!!: $stat_msg\n";
                print LOGFILE $info;
                close (LOGFILE);
                exit 1;
            }
            ## send the snapshot (full send)
            &sendSnapshot($backup_src); 
            $info .= ($status != 0) ? "FULL:FAIL:CASE 1:$stat_msg\n" : "FULL:SUCCESS:CASE 1\n";
            ## write logfile 
            print LOGFILE $info;


        ## CASE 2: At least one snapshot exist on local system
        ## create a snapshot on the local host and send it to the remote host
        ## Send incrementals if zfsFS and snaps live on remote system, else, do a full send.
        } else {

            ###### DEBUG ######
            print "DEBUG: - CASE 2 - createSnapshot($backup_src), send incremental snapshot to remote server\n" if $debug;
            ###### DEBUG ######

            ## create the snapshot for the current zfs filesystem
            ## If we cannot create a snapshot of the filesystem, we have big probs.
            if ( &createSnapshot($backup_src) != 1) {
                ## display error and exit.
                $info .= "ERROR: Cannot create snapshots!!: $stat_msg\n";
                print LOGFILE $info;
                close (LOGFILE);
                exit 1;
            }

            #Everything went fine let's send the snapshot to the remote host
            &send_inc_snapshot($backup_src);

            ## Set the status info line for CASE 2.
            $info .= ($status != 0) ? "INCREMENTAL:FAIL:$stat_msg\n" : "INCREMENTAL:SUCCESS:CASE 2\n";
        }

        ## write logfile 
        print LOGFILE $info;

    } ## End of FOR-LOOP

    ## close log file.
    close(LOGFILE);

} ## End of main()

main();
