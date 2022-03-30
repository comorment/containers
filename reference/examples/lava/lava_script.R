# command line arguments, specifying input/output file names and phenotype subset
arg = commandArgs(T); ref.prefix = arg[1]; loc.file = arg[2]; info.file = arg[3]; sample.overlap.file = arg[4]; phenos = unlist(strsplit(arg[5],";")); out.fname = arg[6]

### Load package
library(LAVA)

### Read in data
loci = read.loci(loc.file); n.loc = nrow(loci)
input = process.input(info.file, sample.overlap.file, ref.prefix, phenos)

print(paste("Starting LAVA analysis for",n.loc,"loci"))
progress = ceiling(quantile(1:n.loc, seq(.05,1,.05)))   # (if you want to print the progress)

### Analyse
u=b=list()
for (i in 1:n.loc) {
	        if (i %in% progress) print(paste("..",names(progress[which(progress==i)])))     # (printing progress)
        locus = try(process.locus(loci[i,], input), silent=T)                                          # process locus
        if (class(locus)=="try-error") { next }
	        
	        # It is possible that the locus cannot be defined for various reasons (e.g. too few SNPs), so the !is.null(locus) check is necessary before calling the analysis functions.
	        if (!is.null(locus)) {
			                # extract some general locus info for the output
			                loc.info = data.frame(locus = locus$id, chr = locus$chr, start = locus$start, stop = locus$stop, n.snps = locus$n.snps, n.pcs = locus$K)
	                
	                # run the univariate and bivariate tests
	                loc.out = run.univ.bivar(locus, univ.thresh=0.05)
			                u[[i]] = cbind(loc.info, loc.out$univ)
			                if(!is.null(loc.out$bivar)) b[[i]] = cbind(loc.info, loc.out$bivar)
					        }
}

# save the output
write.table(do.call(rbind,u), paste0(out.fname,".univ.lava"), row.names=F,quote=F,col.names=T)
write.table(do.call(rbind,b), paste0(out.fname,".bivar.lava"), row.names=F,quote=F,col.names=T)

print(paste0("Done! Analysis output written to ",out.fname,".*.lava"))

