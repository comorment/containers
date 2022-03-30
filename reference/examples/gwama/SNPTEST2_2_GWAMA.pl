# Script for creating GWAMA input file from SNPTEST2 association results file. 
# Use the script: "perl SNPTEST2_2_GWAMA.pl <SNPTEST output file> <output GWAMA file> SE" for quantitative trait analysis
# Use the script: "perl SNPTEST2_2_GWAMA.pl <SNPTEST output file> <output GWAMA file> OR" for dichotomous analysis
# NB! Script uses BETA and SE values which are in last columns of file. If multiple analyse models were used then please edit this script

$inputfile = $ARGV[0];
$outputfile = $ARGV[1];
$scheme = uc($ARGV[2]);
$cMAF=$cMAC=$cN=$cPROPER=0;
for ($i=3; $i<scalar(@ARGV);$i++)
{
	@arg = split(/=/, $ARGV[$i]);
	if (uc($arg[0]) eq "N" && $arg[1]>0){print "N cut-off $arg[1]\n"; $cN=$arg[1];}
	if (uc($arg[0]) eq "MAC" && $arg[1]>0){print "MAC cut-off $arg[1]\n"; $cMAC=$arg[1];}
	if (uc($arg[0]) eq "MAF" && $arg[1]>0){print "MAF cut-off $arg[1]\n"; $cMAF=$arg[1];}
	if (uc($arg[0]) eq "PROPERINFO" && $arg[1]>0){print "PROPERINFO cut-off $arg[1]\n"; $cPROPER=$arg[1];}
}
if ($ARGV[0] eq "" || $ARGV[0] eq "-h" || $ARGV[0] eq "--help"){printhelp();exit;}
open F, "$inputfile" or die "Cannot file SNPTEST file. This must be first command line argument!\n";
if ($outputfile eq ""){die "Please enter the outputfile name as second command line argument!\n";}
open O, ">$outputfile" or die "Cannot open $outputfile for writing. Please check folder's access rights and disk quota!\n";
if ($scheme eq "OR")
{
	print "Using OR with CI output.\n";
	print O "MARKER\tEA\tNEA\tOR\tOR_95L\tOR_95U\tN\tEAF\tSTRAND\tIMPUTED\n";
}
else 
{
	print "Using BETA with SE output.\n";
	print O "MARKER\tEA\tNEA\tBETA\tSE\tN\tEAF\tSTRAND\tIMPUTED\n";
}
$i=0;
while(<F>)
{
	chomp;
	@data = split(/\s/);
	if ($i==0)	#header line
	{
		$locAA=$locAB=$locBB=0;
		for ($j=0;$j<scalar(@data); $j++)
		{
			if ($data[$j] eq "all_AA"){$locAA=$j;}
			if ($data[$j] eq "all_AB"){$locAB=$j;}
			if ($data[$j] eq "all_BB"){$locBB=$j;}
		}
	}
	else		#snp line
	{
		$marker = $data[1];
		$ea = $data[5];
		$nea = $data[4];
		$beta = $data[scalar(@data)-2];
		$se = $data[scalar(@data)-1];
		$proper = $data[scalar(@data)-3];
		$or = exp($beta);
		$or_95l = exp($beta - 1.96* $se);
		$or_95u = exp($beta + 1.96* $se);
		$n = $data[$locAA]+$data[$locAB]+$data[$locBB];
		if (($data[$locAA]+$data[$locAB]+$data[$locBB])>0){$eaf = ((2*$data[$locBB])+$data[$locAB])/(2*($data[$locAA]+$data[$locAB]+$data[$locBB]));}
		else {$eaf =0;}
		if ($eaf>0.5){$maf = 1-$eaf;}
		else {$maf=$eaf;}
		$strand = "+";
		if ($data[0] eq "---"){$imp=1;}else{$imp=0;}
		
		if ($cMAF > $maf || $cMAC>$maf*$n || $cN>$n || $cPROPER>$proper)
		{
		}
		else
		{
			if ($scheme eq "OR"){print O "$marker\t$ea\t$nea\t$or\t$or_95l\t$or_95u\t$n\t$eaf\t$strand\t$imp\n";}
			else {print O "$marker\t$ea\t$nea\t$beta\t$se\t$n\t$eaf\t$strand\t$imp\n";}
		}
	}
	$i++;
}


sub printhelp()
{
	print "Script for creating GWAMA input file from SNPTEST association results file.\n";
	print "Quantitative analysis:\n\tperl SNPTEST2_2_GWAMA.pl <SNPTEST output file> <output GWAMA file> SE\n";
	print "Case-control analysis:\n\tperl SNPTEST2_2_GWAMA.pl <SNPTEST output file> <output GWAMA file> OR\n";
	print "NB! Script uses BETA and SE values which are in last columns of file. If multiple analyse models were used then please edit this script.\n";
	print "NB! Script expects that all markers are from positive strand. If not, Strand column must be modified with correct strand information.\n";
	print "Data can be filtered according to minimum number of samples (N), minor allele frequency (MAF), and minimum number of allele count (MAC = MAF*N)\n";
	print "All cut-offs must be entered after mandatory 3 command line options shown above.\n";
	print "Example: N=100 MAF=0.01 MAC=10 PROPER=0.4, will remove markers with less than 100 individuals, MAF<1% and MAC<10 and properinfo<0.4\n";
	print "Don't leave any spaces into the equations.\n";
	print "Example command line:\n\tperl SNPTEST2_2_GWAMA.pl <SNPTEST output file> <output GWAMA file> SE MAF=0.01 MAC=10\n";
}
