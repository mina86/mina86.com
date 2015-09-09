use strict;
use warnings;

use File::Basename;
use MIME::Base64;


sub readFile {
	my ($filename) = @_;
	open my $fd, '<', $filename or die "$filename: $!\n";
	local $/ = undef;
	my $data = <$fd>;
	close $fd;
	$data;
}


my %mimetypes = (
	png => 'image/png',
	svg => 'image/svg+xml',
);


sub encodeBase64 {
	my ($mime, $data) = @_;
	$data = encode_base64($data);
	$data =~ s/\s+//g;
	"data:$mime;base64,$data";
};


sub encodeString {
	my ($mime, $data, $q) = @_;
	$data =~ s/\n/\\n/g;
	$data =~ s/$q/\\$q/g;
	"${q}data:$mime,$data$q";
};


sub insertData {
	my ($basename, @files) = @_;
	for (@files) {
		if ($basename ne basename $_) {
			next;
		}

		my $mime = (/\.([^.\/]*)/ ? $mimetypes{$1} : undef);
		if (!$mime) {
			print STDERR "$_: unknown MIME type\n";
			$mime = '';
		}

		my $data = readFile $_;
		my @encodings;

		push @encodings, encodeBase64 $mime, $data;

		$data =~ s/^\s+|\s+$//g;
		$data =~ s/([\0-\x1f\x80-\xff%#])/sprintf('%%%02x', ord($1))/ge;

		push @encodings, encodeString $mime, $data, '"';
		push @encodings, encodeString $mime, $data, "'";

		@encodings = sort { length $a <=> length $b; } @encodings;

		return $encodings[0];
	}
	die "Could not find <$basename>\n";
}


sub main {
	my $data = do { local $/; <STDIN> };
	$data =~ s/DATA<([^<>]+)>/insertData($1, @_)/ge;
	print $data;
}


main @ARGV;
