#Quantile-quantile plot script for GWAMA
#Written by Joshua C Randall & Reedik Magi
for (e in commandArgs(trailingOnly=TRUE)) 
{
  ta = strsplit(e,"=",fixed=TRUE)
  if(!is.null(ta[[1]][2])) 
  {
    assign(ta[[1]][1],ta[[1]][2])
  } else {
    assign(ta[[1]][1],TRUE)
  }
}

if(!exists("input")) 
{
  input <- paste("gwama.out")
}

if(!exists("out")) {
  out <- paste(input,".qq.png",sep="")
}
data<-read.table(input,stringsAsFactors=FALSE,header=TRUE,sep = "\t")
png(out,height=600,width=600)
obspval <- sort(data$p.value)
logobspval <- -(log10(obspval))
exppval <- c(1:length(obspval))
logexppval <- -(log10( (exppval-0.5)/length(exppval)))
obsmax <- trunc(max(logobspval))+1
expmax <- trunc(max(logexppval))+1
plot(c(0,expmax), c(0,expmax), col="gray", lwd=1, type="l", xlab="Expected -log10 P-value", ylab="Observed -log10 P-value", xlim=c(0,expmax), ylim=c(0,obsmax), las=1, xaxs="i", yaxs="i", bty="l")
points(logexppval, logobspval, pch=23, cex=.4, bg="black")
dev.off()


