#Manhattan plot script for GWAMA
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
  out <- paste(input,".manh.png",sep="")
}
data<-read.table(input,stringsAsFactors=FALSE,header=TRUE,sep = "\t",na.strings = "-9")
png(out,height=600,width=800)

obspval <- (data$p.value)
chr <- (data$chr)
pos <- (data$pos)
obsmax <- trunc(max(-log10(obspval)))+1

sort.ind <- order(chr, pos) 
chr <- chr[sort.ind]
pos <- pos[sort.ind]
obspval <- obspval[sort.ind]

x <- 1:22
x2<- 1:22

for (i in 1:22)
{
	 curchr=which(chr==i)
	 x[i] <- trunc((max(pos[curchr]))/100) +100000
	 x2[i] <- trunc((min(pos[curchr]))/100) -100000
}

x[1]=x[1]-x2[1]
x2[1]=0-x2[1]

for (i in 2:24)
{
	x[i] <- x[i-1]-x2[i]+x[i]
	x2[i] <- x[i-1]-x2[i]

}
locX = trunc(pos/100) + x2[chr]
locY = -log10(obspval)
col1=rgb(0,0,108,maxColorValue=255)
col2=rgb(100,149,237,maxColorValue=255)
col3=rgb(0,205,102,maxColorValue=255)
col4 <- ifelse (chr%%2==0, col1, col2)
curcol <- ifelse (obspval<5e-8, col3, col4) 
plot(locX,locY,pch=20,col=curcol,axes=F,ylab="-log10 p-value",xlab="",bty="n",ylim=c(0,obsmax),cex=0.8)
axis(2,las=1)
for (i in 1:22)
{
	labpos = (x[i] + x2[i]) / 2
	mtext(i,1,at=labpos,cex=0.8,line=0)
}
mtext("Chromosome",1,at=x[22]/2,cex=1,line=1)
dev.off()

