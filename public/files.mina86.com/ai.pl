#!/usr/bin/perl -w

use strict;
use vars qw($VERSION %IRSSI);

$VERSION = "1.1";
%IRSSI = (
    authors     => 'Michal Nazarewicz',
    contact     => 'mina86@tlen.pl',
    name        => 'ai',
    description => 'Answers questions on channel',
    license     => 'GNU GPLv2 or later'
);

use Irssi;

sub message_public {
	my ($server, $msg, $nick, $address, $target) = @_;
	my ($ans, $mynick, $type);
	$mynick = $server->{'nick'};
	$type = Irssi::settings_get_int("ai_type");

	return unless ($type != 0 && $msg =~ /[a-zA-Z].*\?\s*$/ &&
				   ($type != 1 || $msg =~ /^$mynick(:|\s)/));

	if ($msg =~ /[aeiouAEIOU][^a-zA-Z]*$/) {
		$ans = 'Niet';
	} else {
		$ans = 'Da';
	}

	$server->command("MSG $target $nick: $ans   [auto reply]");
}

Irssi::signal_add("message public", "message_public");
Irssi::settings_add_int('misc', 'ai_type', 2);
# ai_type:
#  0 - disabled
#  1 - answers only  nick: ping
#  2 - answers  nick: ping  and global  ping
