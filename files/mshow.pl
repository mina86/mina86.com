##
## Shows what song is being playd in MPD
## Copyright 2005,2006 by Michal Nazarewicz (mina86/AT/mina86.com)
##
## Provides an /mshow command which displays current song being played
## in MPD and provides an option to automatically respond to someone's
## else's "is listening to" action.  Just trun auto_mshow on and if
## one's action matches auto_mshow_regexp the script will
## automagically run /mshow command unless it was already run no more
## then auto_mshow_delay seconds ago.
##

use strict;
use IO::Socket;
use Text::Iconv;
use Irssi;
use Irssi::Irc;
use vars qw($VERSION %IRSSI $ICONV);


##
## Irssi stuff
##
$VERSION = "0.2";
%IRSSI = (
	author		=> 'mina86',
	contact		=> 'mina86@mina86.com',
	name		=> 'mshow',
	description	=> 'Provides /mshow command which displays current song',
	license		=> 'GPL',
	changed		=> '2005/08/11'
	);


##
## Returns song name
##
sub mshow_get_song {
	# Connect
	my $socket = IO::Socket::INET->new(
		Proto    => 'tcp',
		PeerPort => Irssi::settings_get_int('mpd_port'),
		PeerAddr => Irssi::settings_get_str('mpd_host'),
		timeout  => 5);
	if (!$socket) {
		return 0;
	}

	# Check state (maybe paused/stopped)
	my $play = 0;
	print($socket "status\n");
	while (defined($_ = <$socket>) && !/^(OK$|ACK)/) {
		if (/^\s*state\s*:\s*play\s*$/) {
			$play = 1;
		}
	}
	if (!$play) {
		print($socket "close\n");
		close($socket);
		return 0;
	}

	# Get current song
	print($socket "currentsong\n");
	my %data;
	while (defined($_ = <$socket>) && !/^(OK$|ACK)/) {
		if (/^\s*([^:]+)\s*:\s+(.+)\s*$/) {
			$data{lc($1)} = $2;
		}
	}
	print($socket "close\n");
	close($socket);

	# Prepare song
	my $song = '';
	if (!$data{'artist'} && !$data{'album'} && !$data{'title'}) {
		$song = substr($data{'file'}, rindex($data{'file'}, '/') + 1);
	} elsif ($data{'artist'}) {
		$song = $data{'artist'} .
			($data{'album'} ? ' <' . $data{'album'} . '> ' : ' - ') .
			($data{'track'} ? $data{'track'} . '. ' : '') .
			($data{'title'} ? $data{'title'} : 'Unknown title');
	} else {
		$song = ($data{'album'} ? ' <' . $data{'album'} . '> ' : '') .
			($data{'track'} ? $data{'track'} . '. ' : '') .
			($data{'title'} ? $data{'title'} : 'Unknown title');
	}

	# Iconv
	my($from, $to, $iconv);
	$from = Irssi::settings_get_str('mshow_iconv_from');
	$to   = Irssi::settings_get_str('mshow_iconv_to'  );
	if ($from && $to && $from ne $to) {
		$iconv = Text::Iconv->new($from, $to);
		$song = $iconv->convert($song);
	}

	return $song;
}


##
## Auto show song in reply to someone's `/me is listening`
##
my $auto_show_time = 0;
sub auto_mshow_action {
	if (!Irssi::settings_get_bool('auto_mshow')
		|| (time() - $auto_show_time <
			Irssi::settings_get_int('auto_mshow_delay'))) {
		return;
	}

	my $regexp = Irssi::settings_get_str('auto_mshow_regexp');
	if (!$regexp || $_[1] !~ /$regexp/i) {
		return;
	}

	my $cmd = mshow_get_song();
	if (!$cmd) {
		return;
	}

	$auto_show_time = time();
	$_[0]->command('/action ' . $_[4] . ' ' .
				   Irssi::settings_get_str('mshow_action') . ' ' . $cmd);
}



##
## /mshow command
##
sub cmd_mshow {
	my $cmd = mshow_get_song();
	if ($cmd) {
		$cmd = '/me ' . Irssi::settings_get_str('mshow_action') . ' ' . $cmd;
		Irssi::active_win()->command($cmd);
		$auto_show_time = time();
	}
}


##
#
## Bind command and set config
##
Irssi::command_bind('mshow','cmd_mshow');
Irssi::signal_add("message irc action", "auto_mshow_action");

Irssi::settings_add_str ('mpd', 'mpd_host',          'localhost' );
Irssi::settings_add_int ('mpd', 'mpd_port',          6600        );

Irssi::settings_add_str ('mpd', 'mshow_iconv_from',  'utf8'      );
Irssi::settings_add_str ('mpd', 'mshow_iconv_to',    'iso-8859-1');
Irssi::settings_add_str ('mpd', 'mshow_action',      'is listening to');

Irssi::settings_add_bool('mpd', 'auto_mshow',        0            );
Irssi::settings_add_int ('mpd', 'auto_mshow_delay',  600          );
Irssi::settings_add_str ('mpd', 'auto_mshow_regexp', 'is listening|\.mp3$');
