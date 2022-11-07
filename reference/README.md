This folder containers publicly available reference, derived from different resources as documented below.

* [hapgen](hapgen) folder contains artificially generated genotypes in ``plink`` format for N=10k individuals and M=149454 SNPs,
  with reasonably realistic LD structure representing chromosome 21 in EUR population
  (chr21 is choosen because it is the shortest chromosome in human genome); the data was generated using [HapGen2 software](https://mathgen.stats.ox.ac.uk/genetics_software/hapgen/hapgen2.html).

* [pleiofdr/9545380_ref](pleiofdr/9545380_ref) folder contains reference data for pleioFDR analysis.
  
* [pleiofdr/demo_data](pleiofdr/demo_data) folder contains a demo dataset for pleioFDR analysis, constrained to a very few SNPs so that the analysis
  runs very fast. You can not use this reference for real analysis - it's only a playground to see if pleioFDR runs well on your machine.
  This data includes ``CTG_COG_2018_DEMO.mat`` and ``SSGAC_EDU_2016_DEMO.mat`` from these publications:
  * https://ctg.cncr.nl/software/summary_statistics , Summary statistics for intelligence, wave 2 from Jeanne Savage et al., 2018
  * https://www.thessgac.org/data , Lee et al. (2018). Gene discovery and polygenic prediction from a 1.1-million-person GWAS of educational attainment. Nature Genetics, 50(8), 1112-1121. doi: 10.1038/s41588-018-0147-3
  
