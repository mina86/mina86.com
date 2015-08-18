use strict;
use warnings;
use File::Basename;
use File::MimeInfo;
use MIME::Base64;

sub readFile {
	my ($filename) = @_;
	open my $fd, '<', $filename or die "$filename: $!\n";
	local $/ = undef;
	my $data = <$fd>;
	close $fd;
	$data;
}


sub insertData {
	my ($basename, @files) = @_;
	for (@files) {
		if ($basename ne basename $_) {
			next;
		}
		my $mime = mimetype $_;
		my $data = readFile $_;
		my $data64 = encode_base64($data);
		$data64 =~ s/\s+//g;
		$data =~ s/^\s+|\s+$//g;
		$data =~ s/([\0-\x1f\x80-\xff'#])/sprintf('%%%02x', ord($1))/ge;
		if (7 + length $data64 < length $data) {
			return "data:$mime;base64,$data64";
		} else {
			return "data:$mime,$data";
		}
	}
	die "Could not find <$basename>\n";
}


sub main {
	my $data = do { local $/; <STDIN> };
	$data =~ s/DATA<([^<>]+)>/insertData($1, @_)/ge;
	print $data;
}


main @ARGV;
