# Script for creating GWAMA input file from PLINK association results file. 
# The allele frequency file must also be used for generating GWAMA file.
# Use the script: perl PLINK2GWAMA.pl <PLINK assoc file> <PLINK frq file> <output GWAMA file>
# NB! If PLINK association file contains data of covariate effects or multiple models then please remove unnecessary rows prior using this script

$inputassoc = $ARGV[0];
$inputfrq = $ARGV[1];
if($inputfrq !~ /frq$/){die "Please enter PLINK frq file. File extension must be frq"};
$outputfile = $ARGV[2];
open F1, "$inputassoc" or die "Cannot file PLINK assoc file. This must be first command line argument!\n";
open F2, "$inputfrq" or die "Cannot file PLINK frq file. This must be second command line argument!\n";
if ($outputfile eq ""){die "Please enter the outputfile name as third command line argument!\n";}
open O, ">$outputfile" or die "Cannot open $outputfile for writing. Please check folder's access rights and disk quota!\n";
while(<F2>)
{
	chomp;
	@data = split(/\s+/);
	if ($i>0)
	{
		$snp_ref{$data[2]}=$i;
		$snp_ea[$i] = $data[3];
		$snp_nea[$i] = $data[4];
		$snp_eaf[$i] = $data[5];
		$snp_n[$i] = $data[6]/2;	
	}
	$i++;
}
$i=0;

while(<F1>)
{
	chomp;
	@data = split(/\s+/);
	if ($i==0) 		# header line 
	{
		$locSNP=$locBETA=$locSE=$locOR=$locCIL=$locCIU=-1;
		for ($j=0;$j<scalar(@data);$j++)
		{
			if ($data[$j] eq "SNP"){$locSNP=$j;}
			if ($data[$j] eq "BETA"){$locBETA=$j;}
			if ($data[$j] eq "SE"){$locSE=$j;}
			if ($data[$j] eq "OR"){$locOR=$j;}
			if ($data[$j] eq "L95"){$locCIL=$j;}
			if ($data[$j] eq "U95"){$locCIU=$j;}
		}

		if ($locOR>-1)
		{
 			print "Using OR with CI output.\n";
 			print O "MARKER\tEA\tNEA\tOR\tOR_95L\tOR_95U\tN\tEAF\tSTRAND\n";
		}
		else
		{
 			print "Using BETA with SE output.\n";
 			print O "MARKER\tEA\tNEA\tBETA\tSE\tN\tEAF\tSTRAND\n";
		}


	}
 	if ($i>0) #snp line
 	{
  		$marker = $data[2];
		$loc = $snp_ref{$marker};
		if ($loc>0)
		{
			$ea = $snp_ea[$loc];
			$nea = $snp_nea[$loc];
			if ($locBETA>-1){$beta = $data[$locBETA];}
			if ($locSE>-1){$se = $data[$locSE];}
  			if ($locOR>-1){$or = $data[$locOR];}
  			if ($locCIL>-1){$or_95l = $data[$locCIL];}
  			if ($locCIU>-1){$or_95u = $data[$locCIU];}
  			$n = $snp_n[$loc];
  			$eaf = $snp_eaf[$loc];
  			$strand = "+";
  			if ($locOR>-1){print O "$marker\t$ea\t$nea\t$or\t$or_95l\t$or_95u\t$n\t$eaf\t$strand\n";}
  			else {print O "$marker\t$ea\t$nea\t$beta\t$se\t$n\t$eaf\t$strand\n";}
		}
 }
 $i++;
}
