#!/usr/bin/perl

use CGI;
use URI::Escape;
$script_name = "search.cgi";
$script_version = "1.0.1";
$objects_cache = "/usr/local/nagios/var/objects.cache";
$status_dat = "/usr/local/nagios/var/status.dat";
$query = CGI::new();
$h = $query->param("host");
$s = $query->param("search");
# Avoid inputing specail characters that would crash the program
if ($h =~ /\`|\~|\@|\#|\%|\&|\:|\=|\"|\'|\;|\<|\>/){
	$h = "";
}

sub convert_time {
	my $time = shift;
	my $days = int($time / 86400);
	$time -= ($days * 86400);
	my $hours = int($time / 3600);
	$time -= ($hours * 3600);
	my $minutes = int($time / 60);
	my $seconds = $time % 60;

	$days = $days < 1 ? '' : $days .'d ';
	$hours = $hours < 1 ? '' : $hours .'h ';
	$minutes = $minutes < 1 ? '' : $minutes . 'm ';
	$time = $days . $hours . $minutes . $seconds . 's';

	return $time;
}

print "Content-type: text/html\n\n";

if ($s eq "host") {
	#if (!open (hosts,"grep -EA1 \"define[ ]+host[ ]+\" ".$objects_cache."| grep -Eo \"host_name.+\" |")){
	#	print  "Fail to create host list from $objects_cache: $!\n";
	#} else {
	#	while (<hosts>) {
	#		local ($c,$d) = split/\s/,$_;
	#		if ($c eq "host_name") {
	#			if ($d =~ /($h)/i) {
	#				push (@host_list, $d);
	#			}
	#		}
	#	}
	#}
	#close(hosts);

	if (!open (hosts,"grep -EA2 \"define[ ]+host[ ]+\" ".$objects_cache."|grep -Eo \"(host_name|alias).+\"|perl -pe 's/^(host_name|alias)\\s+/\\1|/'|perl -pe 's/^(host_name.+[|])(host_name.+\n)\$/\\1alias|\n\\2/'|perl -pe 's/^(host_name.+)\n\$/\\1|/'|")){
		print  "Fail to create host list from $objects_cache: $!\n";
	} else {
		while (<hosts>) {
			local ($a,$c,$b,$d) = split/[|\n]/,$_;
			if ($a eq "host_name" && $b eq "alias") {
				if ($c =~ /($h)/i || $d =~ /($h)/i) {
					push (@host_list, $c);
				}
			}
		}
	}
	close(hosts);

	if (!open (status,"grep -EA15 \"hoststatus[ ]+\" ".$status_dat."|grep -Eo \"(host_name|current_state)=.+\"|perl -pe 's/^(host_name|current_state)=/\\1|/'|perl -pe 's/^(host_name.+)\n\$/\\1|/'|")){
		print  "Fail to create host status list from $status_dat: $!\n";
	} else {
		while (<status>) {
			$host_status = {};
			local ($a,$c,$b,$d) = split/[|\n]/,$_;
			if ($a eq "host_name" && $b eq "current_state") {
				#if ($c =~ /($h)/i) {
				foreach $host (@host_list) {
					if ($host == $c) {
						$host_status{$c}=$d;
					}
				}
			}
		}
	}
	close(status);

	if (!open (status,"grep -EA25 \"hoststatus[ ]+\" ".$status_dat."|grep -Eo \"(host_name|last_check)=.+\"|perl -pe 's/^(host_name|last_check)=/\\1|/'|perl -pe 's/^(host_name.+)\n\$/\\1|/'|")){
		print  "Fail to create host last check list from $status_dat: $!\n";
	} else {
		while (<status>) {
			$host_lastcheck = {};
			local ($a,$c,$b,$d) = split/[|\n]/,$_;
			if ($a eq "host_name" && $b eq "last_check") {
				#if ($c =~ /($h)/i) {
				foreach $host (@host_list) {
					if ($host == $c) {
						local ($S,$M,$H,$d,$m,$Y) = localtime($d);
	    					$m += 1;
						$Y += 1900;
						$host_lastcheck{$c} = sprintf("%02d-%02d-%04d %02d:%02d:%02d", $m,$d,$Y, $H,$M,$S);
					}
				}
			}
		}
	}
	close(status);

	if (!open (status,"grep -EA25 \"hoststatus[ ]+\" ".$status_dat."|grep -Eo \"(host_name|plugin_output)=.+\"|perl -pe 's/^(host_name|plugin_output)=/\\1|/'|perl -pe 's/^(host_name.+)\n\$/\\1|/'|")){
		print  "Fail to create host plugin output list from $status_dat: $!\n";
	} else {
		while (<status>) {
			$host_output = {};
			local ($a,$c,$b,$d) = split/[|\n]/,$_;
			if ($a eq "host_name" && $b eq "plugin_output") {
				#if ($c =~ /($h)/i) {
				foreach $host (@host_list) {
					if ($host == $c) {
						$host_output{$c} = $d;
					}
				}
			}
		}
	}
	close(status);

	if (!open (status,"grep -EA30 \"hoststatus[ ]+\" ".$status_dat."|grep -Eo \"(host_name|last_state_change)=.+\"|perl -pe 's/^(host_name|last_state_change)=/\\1|/'|perl -pe 's/^(host_name.+)\n\$/\\1|/'|")){
		print  "Fail to create host last change list from $status_dat: $!\n";
	} else {
		while (<status>) {
			$host_lastchange = {};
			local ($k1,$v1,$k2,$v2) = split/[|\n]/,$_;
			if ($k1 eq "host_name" && $k2 eq "last_state_change") {
				#if ($v1 =~ /($h)/i) {
				foreach $host (@host_list) {
					if ($host == $v1) {
						local $duration = convert_time(time - $v2);
						$host_lastchange{$v1} = $duration;
					}
				}
			}
		}
	}
	close(status);

	if (!open (status,"grep -EA30 \"hoststatus[ ]+\" ".$status_dat."|grep -Eo \"(host_name|current_attempt|max_attempts)=.+\"|perl -pe 's/^(host_name|current_attempt|max_attempts)=/\\1|/'|perl -pe 's/^(current_attempt.+)\n\$/\\1|/'|perl -pe 's/^(host_name.+)\n\$/\\1|/'|")){
		print  "Fail to create host attempt list from $status_dat: $!\n";
	} else {
		while (<status>) {
			$host_attempt = {};
			local ($k1,$v1,$k2,$v2,$k3,$v3) = split/[|\n]/,$_;
			if ($k1 eq "host_name" && $k2 eq "current_attempt" && $k3 eq "max_attempts") {
				#if ($v1 =~ /($h)/i) {
				foreach $host (@host_list) {
					if ($host == $v1) {
						$host_attempt{$v1} = $v2."/".$v3;
					}
				}
			}
		}
	}
	close(status);

	if (!open (status,"grep -EA30 \"define[ ]+host[ ]+\" ".$objects_cache."|grep -Eo \"(host_name\\s+|notes_url\\s+).+\"|perl -pe 's/^(host_name|notes_url)\\s+/\\1|/'|perl -pe 's/^(host_name.+)\n\$/\\1|/'|perl -pe 's/^(host_name.+[|])(host_name.+\n)\$/\\1notes_url|\n\\2/'|")){
		print  "Fail to create host notes list from $status_dat: $!\n";
	} else {
		while (<status>) {
			$host_notes = {};
			local ($k1,$v1,$k2,$v2) = split/[|\n]/,$_;
			if ($k1 eq "host_name" && $k2 eq "notes_url") {
				if ($v1 =~ /($h)/i) {
					$v2 =~ s/\$HOSTNAME\$/$v1/g;
					$host_notes{$v1} = $v2;
				}
			}
		}
	}
	close(status);

	if (!open (status,"grep -EA30 \"define[ ]+host[ ]+\" ".$objects_cache."|grep -Eo \"(host_name\\s+|action_url\\s+).+\"|perl -pe 's/^(host_name|action_url)\\s+/\\1|/'|perl -pe 's/^(host_name.+)\n\$/\\1|/'|perl -pe 's/^(host_name.+[|])(host_name.+\n)\$/\\1action_url|\n\\2/'|")){
		print  "Fail to create host action list from $status_dat: $!\n";
	} else {
		while (<status>) {
			$host_action = {};
			local ($k1,$v1,$k2,$v2) = split/[|\n]/,$_;
			if ($k1 eq "host_name" && $k2 eq "action_url") {
				if ($v1 =~ /($h)/i) {
					$v2 =~ s/\$HOSTNAME\$/$v1/g;
					$host_action{$v1} = $v2;
				}
			}
		}
	}
	close(status);
}

if ($s eq "service") {
	if (!open (services,"grep -EA2 \"define[ ]+service[ ]+\" ".$objects_cache."| grep -Eo \"(host_name|service_description).+\"|perl -pe 's/^(service_description)\\s+(.+)\$/\\1|\\2/'|perl -pe 's/^(host_name)\\s(.+)\$/\\1|\\2/'|perl -pe 's/^(host_name.+)\n\$/\\1|/'|")){
		print  "Fail to create service list from $objects_cache: $!\n";
	}
	else {
		while (<services>) {
			local ($a,$c,$b,$d) = split/[|\n]/,$_;
			if ($a eq "host_name" && $b eq "service_description") {
				if ($d =~ /($h)/i){   # i indicates case insensitive match
					push (@service_list, $c."|".$d);
				}
			}
		}
	}
	close(services);

	if (!open (status,"grep -EA15 \"servicestatus[ ]+\" ".$status_dat."|grep -Eo \"(host_name|service_description|current_state)=.+\"|perl -pe 's/^(host_name|service_description|current_state)=/\\1|/'|perl -pe 's/^(service_description.+)\n\$/\\1|/'|perl -pe 's/^(host_name.+)\n\$/\\1|/'|")){
		print  "Fail to create host status list from $status_dat: $!\n";
	} else {
		while (<status>) {
			$host_status = {};
			local ($a,$b,$c,$d,$e,$f) = split/[|\n]/,$_;
			if ($a eq "host_name" && $c eq "service_description" && $e eq "current_state") {
				if ($d =~ /($h)/i) {
					$service_status{$b.$d}=$f;
				}
			}
		}
	}
	close(status);

	if (!open (status,"grep -EA35 \"servicestatus[ ]+\" ".$status_dat."|grep -Eo \"(host_name|service_description|last_check)=.+\"|perl -pe 's/^(host_name|service_description|last_check)=/\\1|/'|perl -pe 's/^(service_description.+)\n\$/\\1|/'|perl -pe 's/^(host_name.+)\n\$/\\1|/'|")){
		print  "Fail to create service last check list from $status_dat: $!\n";
	} else {
		while (<status>) {
			$service_lastcheck = {};
			local ($k1,$v1,$k2,$v2,$k3,$v3) = split/[|\n]/,$_;
			if ($k1 eq "host_name" && $k2 eq "service_description" && $k3 eq "last_check") {
				if ($v2 =~ /($h)/i) {
					local ($S,$M,$H,$d,$m,$Y) = localtime($v3);
					$m += 1;
					$Y += 1900;
					$service_lastcheck{$v1.$v2} = sprintf("%02d-%02d-%04d %02d:%02d:%02d", $m,$d,$Y, $H,$M,$S);
				}
			}
		}
	}
	close(status);

	if (!open (status,"grep -EA30 \"servicestatus[ ]+\" ".$status_dat."|grep -Eo \"(host_name|service_description|plugin_output)=.+\"|perl -pe 's/^(host_name|service_description|plugin_output)=/\\1|/'|perl -pe 's/^(service_description.+)\n\$/\\1|/'|perl -pe 's/^(service_description.+[|])(host_name.+\n)\$/\\1plugin_output|\n\\2/'|perl -pe 's/^(host_name.+)\n\$/\\1|/'|")){
		print  "Fail to create service plugin output list from $status_dat: $!\n";
	} else {
		while (<status>) {
			$service_output = {};
			local ($k1,$v1,$k2,$v2,$k3,$v3) = split/[|\n]/,$_;
			if ($k1 eq "host_name" && $k2 eq "service_description" && $k3 eq "plugin_output") {
				if ($v2 =~ /($h)/i) {
					$service_output{$v1.$v2} = $v3;
				}
			}
		}
	}
	close(status);

	if (!open (status,"grep -EA25 \"servicestatus[ ]+\" ".$status_dat."|grep -Eo \"(host_name|service_description|last_state_change)=.+\"|perl -pe 's/^(host_name|service_description|last_state_change)=/\\1|/'|perl -pe 's/^(service_description.+)\n\$/\\1|/'|perl -pe 's/^(host_name.+)\n\$/\\1|/'|")){
		print  "Fail to create service last change list from $status_dat: $!\n";
	} else {
		while (<status>) {
			$service_lastchange = {};
			local ($k1,$v1,$k2,$v2,$k3,$v3) = split/[|\n]/,$_;
			if ($k1 eq "host_name" && $k2 eq "service_description" && $k3 eq "last_state_change") {
				if ($v2 =~ /($h)/i) {
					local $duration = convert_time(time - $v3);
					$service_lastchange{$v1.$v2} = $duration;
				}
			}
		}
	}
	close(status);

	if (!open (status,"grep -EA25 \"servicestatus[ ]+\" ".$status_dat."|grep -Eo \"(host_name|service_description|current_attempt|max_attempts)=.+\"|perl -pe 's/^(host_name|service_description|current_attempt|max_attempts)=/\\1|/'|perl -pe 's/^(current_attempt.+)\n\$/\\1|/'|perl -pe 's/^(service_description.+)\n\$/\\1|/'|perl -pe 's/^(host_name.+)\n\$/\\1|/'|")){
		print  "Fail to create service attempt list from $status_dat: $!\n";
	} else {
		while (<status>) {
			$service_attempt = {};
			local ($k1,$v1,$k2,$v2,$k3,$v3,$k4,$v4) = split/[|\n]/,$_;
			if ($k1 eq "host_name" && $k2 eq "service_description" && $k3 eq "current_attempt" && $k4 eq "max_attempts") {
				if ($v2 =~ /($h)/i) {
					$service_attempt{$v1.$v2} = $v3."/".$v4;
				}
			}
		}
	}
	close(status);


	if (!open (status,"grep -EA45 \"servicestatus[ ]+\" ".$status_dat."|grep -Eo \"(host_name|service_description|active_checks_enabled)=.+\"|perl -pe 's/^(host_name|service_description|active_checks_enabled)=/\\1|/'|perl -pe 's/^(service_description.+)\n\$/\\1|/'|perl -pe 's/^(host_name.+)\n\$/\\1|/'|")){
		print  "Fail to create service active check list from $status_dat: $!\n";
	} else {
		while (<status>) {
			$service_activecheck = {};
			local ($k1,$v1,$k2,$v2,$k3,$v3) = split/[|\n]/,$_;
			if ($k1 eq "host_name" && $k2 eq "service_description" && $k3 eq "active_checks_enabled") {
				if ($v2 =~ /($h)/i) {
					$service_activecheck{$v1.$v2} = $v3;
				}
			}
		}
	}
	close(status);

	if (!open (status,"grep -EA30 \"define[ ]+host[ ]+\" ".$objects_cache."|grep -Eo \"(host_name\\s+|notes_url\\s+).+\"|perl -pe 's/^(host_name|notes_url)\\s+/\\1|/'|perl -pe 's/^(host_name.+)\n\$/\\1|/'|")){
		print  "Fail to create host notes list from $status_dat: $!\n";
	} else {
		while (<status>) {
			$host_action = {};
			local ($k1,$v1,$k2,$v2) = split/[|\n]/,$_;
			if ($k1 eq "host_name" && $k2 eq "notes_url") {
				$v2 =~ s/\$HOSTNAME\$/$v1/g;
				$host_notes{$v1} = $v2;
			}
		}
	}
	close(status);

	if (!open (status,"grep -EA30 \"define[ ]+host[ ]+\" ".$objects_cache."|grep -Eo \"(host_name\\s+|action_url\\s+).+\"|perl -pe 's/^(host_name|action_url)\\s+/\\1|/'|perl -pe 's/^(host_name.+)\n\$/\\1|/'|")){
		print  "Fail to create host action list from $status_dat: $!\n";
	} else {
		while (<status>) {
			$host_action = {};
			local ($k1,$v1,$k2,$v2) = split/[|\n]/,$_;
			if ($k1 eq "host_name" && $k2 eq "action_url") {
				$v2 =~ s/\$HOSTNAME\$/$v1/g;
				$host_action{$v1} = $v2;
			}
		}
	}
	close(status);

	if (!open (status,"grep -EA32 \"define[ ]+service[ ]+\" ".$objects_cache."|grep -Eo \"(host_name\\s+|service_description\\s+|notes_url\\s+).+\"|perl -pe 's/^(host_name|service_description|notes_url)\\s+/\\1|/'|perl -pe 's/^(service_description.+)\n\$/\\1|/'|perl -pe 's/^(service_description.+[|])(host_name.+\n)\$/\\1notes_url|\n\\2/'|perl -pe 's/^(host_name.+)\n\$/\\1|/'|")){
		print  "Fail to create service notes list from $status_dat: $!\n";
	} else {
		while (<status>) {
			$service_notes = {};
			local ($k1,$v1,$k2,$v2,$k3,$v3) = split/[|\n]/,$_;
			if ($k1 eq "host_name" && $k2 eq "service_description" && $k3 eq "notes_url") {
				if ($v2 =~ /($h)/i) {
					$v3 =~ s/\$HOSTNAME\$/$v1/g;
					$v3 =~ s/\$SERVICEDESC\$/$v2/g;
					$service_notes{$v1.$v2} = $v3;
				}
			}
		}
	}
	close(status);

	if (!open (status,"grep -EA32 \"define[ ]+service[ ]+\" ".$objects_cache."|grep -Eo \"(host_name\\s+|service_description\\s+|action_url\\s+).+\"|perl -pe 's/^(host_name|service_description|action_url)\\s+/\\1|/'|perl -pe 's/^(service_description.+)\n\$/\\1|/'|perl -pe 's/^(service_description.+[|])(host_name.+\n)\$/\\1action_url|\n\\2/'|perl -pe 's/^(host_name.+)\n\$/\\1|/'|")){
		print  "Fail to create service action list from $status_dat: $!\n";
	} else {
		while (<status>) {
			$service_action = {};
			local ($k1,$v1,$k2,$v2,$k3,$v3) = split/[|\n]/,$_;
			if ($k1 eq "host_name" && $k2 eq "service_description" && $k3 eq "action_url") {
				if ($v2 =~ /($h)/i) {
					$v3 =~ s/\$HOSTNAME\$/$v1/g;
					$v3 =~ s/\$SERVICEDESC\$/$v2/g;
					$service_action{$v1.$v2} = $v3;
				}
			}
		}
	}
	close(status);
}

print "<html>\n";
print "<head><title>Search Results</title>\n";
print "<link rel='stylesheet' type='text/css' href='/nagios/stylesheets/common.css'>\n";
print "<link rel='stylesheet' type='text/css' href='/nagios/stylesheets/status.css'>\n";
print "</head><body>\n";
print "<table class='linkBox'>\n";
print "<tr><td class='linkBox'>\n";
print "<a href='status.cgi?hostgroup=all&style=detail'>View Service Status Detail For All Host Groups</a><br>\n";
print "<a href='status.cgi?hostgroup=all&style=overview'>View Status Overview For All Host Groups</a><br>\n";
print "<a href='status.cgi?hostgroup=all&style=summary'>View Status Summary For All Host Groups</a><br>\n";
print "<a href='status.cgi?hostgroup=all&style=grid'>View Status Grid For All Host Groups</a><br>\n";
print "</td></tr></table>\n";
print "<div align='center' class='statusTitle'>Nagios Search Results for $opt:</b> $h</div>";
print "<table border=0 width=100% class='status'>\n";

if ($s eq "host") {
	print "<tr><th align=left class='status'>Host</th><th align=left class='status'>Status</th><th align=left class='status'>Last Check</th><th align=left class='status'>Duration</th><th align=left class='status'>Attempt</th><th align=left class='status'>Status Information</th></tr>\n";
	$n = scalar(@host_list);
	foreach $host (@host_list){
		local $class_status = "statusPENDING";
		local $class_row = "statusEven";
		local $status = "";

		if ($host_status{$host} eq "0") {
			$class_status = "statusHOSTUP";
			$status = "UP";
		} elsif ($host_status{$host} eq "1") {
			$class_status = "statusHOSTDOWN";
			$status = "DOWN";
		} elsif ($host_status{$host} eq "2") {
			$class_status = "statusUNKNOWN";
			$status = "UNKNOWN";
		} else {
			$class_status = "statusPENDING";
			$status = "PENDING";
		}
		print "<tr>\n";
		print "<td class='$class_status'><table border=0 width='100%' cellpadding=0 cellspacing=0><tr>";
		print "<td align=left><table border=0 cellpadding=0 cellspacing=0><tr><td align=left valign=center class='$class_status'><a href=status.cgi?host=$host>$host</a></td></tr></table></td>";
		print "<td align=right><table border=0 cellpadding=0 cellspacing=0><tr>";
		if ($host_notes{$host} ne "") {
			print "<td align=center valign=center><a href='$host_notes{$host}' target='_blank'><img src='/nagios/images/notes.gif' border=0 width=20 height=20 alt='View Extra Host Notes' title='View Extra Host Notes'></a></td>";
		} else {
			print "<td></td>";
		}
		#print "<td align=center valign=center><a href='/nagios/cgi-bin/config.cgi?type=hosts&expand=$host' target='_blank'><img src='/nagios/images/notes.gif' border=0 width=20 height=20 alt='View Extra Host Notes' title='View Extra Host Notes'></a></td>";
		if ($host_action{$host} ne "") {
			print "<td align=center valign=center><a href='$host_action{$host}' target='_blank'><img src='/nagios/images/action.gif' border=0 width=20 height=20 alt='Perform Extra Host Actions' title='Perform Extra Host Actions'></a></td>";
		} else {
			print "<td></td>";
		}
		print "<td><a href='status.cgi?host=$host'><img src='/nagios/images/status2.gif' border=0 alt='View Service Details For This Host' title='View Service Details For This Host'></a></td>";
		print "</tr></table></td>";
		print "</tr></table></td>\n";
		print "<td class='$class_status'>$status</td>";
		print "<td class='$class_row'>$host_lastcheck{$host}</td>\n";
		print "<td class='$class_row'>$host_lastchange{$host}</td>\n";
		print "<td class='$class_row'>$host_attempt{$host}</td>\n";
		print "<td class='$class_row'>$host_output{$host}</td>\n";
		print "</tr>\n";
		if ($class_row eq "statusEven") {
			$class_row = "statusOdd";
		} else {
			$class_row = "statusEven";
		}
	}
}

if ($s eq "service") {
	print "<tr><th align=left class='status'>Host</th><th align=left class='status'>Service</th><th align=left class='status'>Status</th><th align=left class='status'>Last Check</th><th align=left class='status'>Duration</th><th align=left class='status'>Attempt</th><th align=left class='status'>Status Information</th></tr>\n";
	$n = scalar(@service_list);
	local $last_host = "";
	local $class_row = "statusEven";

	foreach $host_service (@service_list){
		local ($host,$service) = split/[|]/,$host_service;
		local $class_status = "statusPENDING";
		local $status = "";

		if ($service_activecheck{$host.$service} eq "0" && $service_output{$host.$service} eq "") {
			$class_status = "statusPENDING";
			$status = "PENDING";
			$service_output{$host.$service} = "Service is not scheduled to be checked...";
		} elsif ($service_status{$host.$service} eq "0") {
			$class_status = "statusOK";
			$status = "OK";
		} elsif ($service_status{$host.$service} eq "1") {
			$class_status = "statusWARNING";
			$class_row = "statusBGWARNING";
			$status = "WARNING";
		} elsif ($service_status{$host.$service} eq "2") {
			$class_status = "statusCRITICAL";
			$class_row = "statusBGCRITICAL";
			$status = "CRITICAL";
		} elsif ($service_status{$host.$service} eq "3") {
			$class_status = "statusUNKNOWN";
			$class_row = "statusBGUNKNOWN";
			$status = "CRITICAL";
		} else {
			$class_status = "statusPENDING";
			$status = "PENDING";
		}

		print "<tr>\n";
		if ($last_host ne $host) {
			print "<td class='statusEven'>\n<table border=0 width=100% cellpadding=0 cellspacing=0>\n<tr>\n";
			print "<td align=left>\n<table border=0 cellpadding=0 cellspacing=0><tr><td align=left valign=center class='statusEven'><a href=status.cgi?host=$host>$host</a></td></tr></table>\n</td>\n";
			print "<td align=right>\n<table border=0 cellpadding=0 cellspacing=0><tr>";
			if ($host_notes{$host} ne "") {
				print "<td align=center valign=center><a href='$host_notes{$host}' target='_blank'><img src='/nagios/images/notes.gif' border=0 width=20 height=20 alt='View Extra Host Notes' title='View Extra Host Notes'></a></td>";
			} else {
				print "<td></td>";
			}
			#print "<td align=center valign=center><a href='/nagios/cgi-bin/config.cgi?type=hosts&expand=$host' target='_blank'><img src='/nagios/images/notes.gif' border=0 width=20 height=20 alt='View Extra Host Notes' title='View Extra Host Notes'></a></td>";
			if ($host_action{$host} ne "") {
				print "<td align=center valign=center><a href='$host_action{$host}' target='_blank'><img src='/nagios/images/action.gif' border=0 width=20 height=20 alt='Perform Extra Host Actions' title='Perform Extra Host Actions'></a></td>";
			} else {
				print "<td></td>";
			}
			print "</tr></table>\n</td>\n";
			print "</tr>\n</table>\n</td>\n";
			$last_host = $host;
		} else {
			print "<td></td>\n";
		}
		print "<td class='$class_row'>\n<table border=0 width=100% cellpadding=0 cellspacing=0>\n<tr>\n";
		print "<td align=left>\n<table border=0 cellpadding=0 cellspacing=0><tr><td align=left valign=center class='$class_row' nowrap><a href=/nagios/cgi-bin/extinfo.cgi?type=2&host=$host&service=".uri_escape($service).">$service</a></td></tr></table>\n</td>\n";
		print "<td align=right class='$class_row'>\n<table border=0 cellpadding=0 cellspacing=0><tr>";
		if ($service_activecheck{$host.$service} eq "0") {
			print "<td align=center valign=center><img src='/nagios/images/passiveonly.gif' border=0 width=20 height=20 alt='Active checks of the service have been disabled - only passive checks are being accepted' title='Active checks of the service have been disabled - only passive checks are being accepted'></td>";
		}
		if ($service_notes{$host.$service} ne "") {
			print "<td align=center valign=center><a href='$service_notes{$host.$service}' target='_blank'><img src='/nagios/images/notes.gif' border=0 width=20 height=20 alt='View Extra Service Notes' title='View Extra Service Notes'></a></td>";
		}
		#print "<td align=center valign=center><a href='/nagios/cgi-bin/config.cgi?type=services&expand=$service' target='_blank'><img src='/nagios/images/notes.gif' border=0 width=20 height=20 alt='View Extra Service Notes' title='View Extra Service Notes'></a></td>";
		if ($service_action{$host.$service} ne "") {
			print "<td align=center valign=center><a href='$service_action{$host.$service}' target='_blank'><img src='/nagios/images/action.gif' border=0 width=20 height=20 alt='Perform Extra Service Actions' title='Perform Extra Service Actions'></a></td>";
		}
		print "</tr></table></td>\n";
		print "</tr>\n</table>\n</td>\n";
		print "<td class='$class_status' nowrap>$status</td>\n";
		print "<td class='$class_row' nowrap>$service_lastcheck{$host.$service}</td>\n";
		print "<td class='$class_row' nowrap>$service_lastchange{$host.$service}</td>\n";
		print "<td class='$class_row' nowrap>$service_attempt{$host.$service}</td>\n";
		print "<td class='$class_row'>$service_output{$host.$service}</td>\n";
		print "</tr>\n";
		if ($class_row eq "statusEven") {
			$class_row = "statusOdd";
		} else {
			$class_row = "statusEven";
		}
	}
}
print "</table>\n";
print "<div class='itemTotalsTitle'>$n Matching ".$s."(s) entries found.</div>";
print "</body></html>\n";
