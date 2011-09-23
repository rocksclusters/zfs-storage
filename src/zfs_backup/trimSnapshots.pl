#!/usr/bin/perl -w
####
## Edmond Negado
## Date: 1/1/2009
## Description: This file trims the snapshots which exceed the number of
##              max snapshots specified in the global section.
##              When the snapshots are maintained and trimmed, this eases
##              search queries when calling zfs list ...
####

## 2009-02-08 - Added grep $fs@ in getSnapshots() to fix snapshot listing.
## 2009-02-26 - Added full filesystem snapshot lookup and trim snap removal.

use strict;
## Globals Editable ###########################################################

## debug variable, set to 1 to output debug info.
my $debug = 0;

## max number of days from current day to keep
my $MAXSNAPS = 35;

## End of Globals #############################################################


###############################################################################
## Function: indexArray()
## This function returns the index of the given element in the array.
## ex: $index = indexArray($value, @array);
## Returns index, or -1 if fail.
###############################################################################
sub indexArray {
    1 while $_[0] ne pop;
    @_-1;
}


###############################################################################
## Function: getSnapshots
###############################################################################
sub getSnapshots {

    ## get the zfs filesystem parameter
    my $fs = shift or die ("getLastSnapshot(): No zfs filesystem specified.");
    use Time::Local;

    ## create a local hash to store the zfs snap names and time values
    my %snapHashTemp = ();

    ## init month names for month aquisition for time calculation
    my @monthnames = (qw(Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec)); 

    ## get the snapshots from the given zfs filesystem
    my @zfsSnaplist = `zfs list -H -r -t snapshot -o name,creation $fs | grep $fs@`;

    ## parse though the list and collect the time stamps
    foreach my $snapshot (@zfsSnaplist) {
 
        ## split the zfs name and creation time.
        my ($zfs, $wday, $mon, $mday, $time, $yr ) = split(/\s+/, $snapshot);
        ## get the hour and minute from the time on the zfs creation date
        my ($hour, $min) = split(":", $time);
        ## get the year difference from the zfs creation date.
        my $year = $yr - 1900;
        ## get the month by number from the month name from the zfs creation date.
        my $month = indexArray($mon, @monthnames);

        ## calculate the time in epoch secs for the current snapshot
        ## ex: timelocal($sec,$min,$hour,$mday,$mon,$year);
        my $epocSec = timelocal(0,$min, $hour, $mday, $month, $year);

        ## add the zfs snap and epoc times into hash
        $snapHashTemp{ $zfs } = $epocSec;

        if ($debug) {
            print "epoc sec is: $epocSec\n";
            print "zfs snapshot is: $zfs\n";
            print "wday is: $wday\n";
            print "mon is: $mon\n";
            print "day is: $mday\n";
            print "time is: $time\n";
            print "year is: $yr\n";

            print "hour is: $hour\n";
            print "minute is: $min\n";
            print "year - 1900 is: $year\n";
            print "month index is: $month\n";
        }
    } ## end of for-loop
    ## sort the snap hash by time: newest to oldest.
    my @snapList = ();

    ## This loop sorts the zfs snaps from oldest to newest.
    foreach my $key (sort { $snapHashTemp{$a} <=> $snapHashTemp{$b}  } (keys(%snapHashTemp))) {
        ## add the sorted key-zfs snap to a 2d array
        push(@snapList, [$key, $snapHashTemp{$key}]);
    }

    if ($debug) {
        foreach my $row (@snapList) {
            print "\ttime: $row->[1] \t snapshot: $row->[0] \n";
        }
    }
    return @snapList;
}


###############################################################################
## Sub: trimSnapshots
## Description: This function trims the current zfs filesystems snapshots, and
## keeps the snapshots no more than  MAXSNAPS snaps in size.
###############################################################################
sub trimSnapshots {

    ## get the passed in args
    my $fs = shift or die("trimSnapshots(): No zfs filesystem specified.");

    ## temp array to store the 'to be removed' snapshots
    my @toBeRemovedList = ();

    ## collect the snapshots from the local system. (where the list is
    ## from oldest to newest; ie pop() will remove the oldest snapshot)
    my @snapList = &getSnapshots($fs);

    @snapList = reverse(@snapList);

    ## get the count of the snapshots
    my $snapSize = @snapList;

    ## trim the snapList if bigger than max allowed snapshots
    ## by popping it out from the snapList.
    while ($snapSize > $MAXSNAPS) {
        ## this pops the oldest snap off the array.
        push(@toBeRemovedList, pop(@snapList));
        ## update the size of the array
        $snapSize = @snapList;
    }

    ## loop through all the snapshots to be removed.
    foreach my $row (@toBeRemovedList) {
        ## print out the snapshot to be destroyed
        print "zfs destroy $row->[0] \n";
        print "time: $row->[1]\t\t$row->[0]\n" if $debug;
        ## place sys call here and test 
   #trim55     my $retVal =  system("zfs destroy $row->[0]");

    }
} ## End of trimSnapshots()



###############################################################################
## function: main()
## This function calls the script to execute filesystem lookup
## and trim snapshots.
###############################################################################
sub main {

    ## collect all the zfs filesystems for trimming.
    my @filesystems = `zfs list -H -r -t filesystem -o name`;

    ## loop through all the zfs filesystems and trim to MAX allowed snapshots.
    foreach my $zfsfilesystem (@filesystems) {
        ## clean out any whitespace
        chomp ($zfsfilesystem);
        ## trim out excess snapshots up to MAX allowed number of snapshots.
        &trimSnapshots($zfsfilesystem);
    }
} ## End of main function.

# call main function to execute sub functions.

main();


