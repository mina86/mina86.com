#!/usr/bin/perl -w

use strict;

$::VERSION = "1.0";
%::IRSSI = (
    authors     => 'Michal Nazarewicz',
    contact     => 'mina86@tlen.pl',
    name        => 'ls-cm',
    description => 'Translates "ls" typed by user to /n command',
    license     => 'Public Domain'
);

use Irssi;

Irssi::signal_add("send text", sub {
	if ($_[0] eq 'ls') {
		Irssi::signal_stop();
		$_[2]->command("n");
	}
});
