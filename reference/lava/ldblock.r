load.breaks = function(prefix) {read.table(paste0(prefix, ".breaks"), header=T)}

#bounds are inclusive, ie. should include SNPs with BP equal to the boundary points
#size currently reflects just the number of SNPs per block after the MAF filtering applied
make.blocks = function(breaks) {
  N = dim(breaks)[1]
  blocks = data.frame(
    start=breaks$POSITION[-N],
    stop=breaks$POSITION[-1]-1,
    size.filt=breaks$INDEX_FILT[-1] - breaks$INDEX_FILT[-N],
    size.all=breaks$INDEX_ALL[-1] - breaks$INDEX_ALL[-N],
    stringsAsFactors=F
  )
  return(blocks)
}


#only meant to be applied to a complete, loaded breaks data.frame once
#min.size is for filtering on the number of SNPs per block after the MAF filtering, min.size.all is on SNPs per block total
filter.breaks = function(breaks, max.blocks=NULL, max.metric=1, min.size=0, min.size.all=0) {
  tree = build.tree(breaks)
  discard = breaks$RANK[breaks$METRIC_MIN > max.metric]

  checked = rep(F, length(tree))  
  for (n in 1:length(checked)) {
    if (!checked[n]) {
      curr = tree[[n]]
      if (!is.null(curr$break.rank)) {
        children = tree[curr$children]
        if (!check.nodesize(children[[1]], min.size.all, min.size) || !check.nodesize(children[[2]], min.size.all, min.size)) discard = c(discard, curr$break.rank)
        if (curr$break.rank %in% discard) {
          cascade = curr$children
          while (length(cascade) > 0) {
            checked[cascade[1]] = T
            curr = tree[[cascade[1]]]; cascade = cascade[-1]
            if (!is.null(curr$break.rank)) {
              discard = c(discard, curr$break.rank)
              cascade = c(cascade, curr$children)
            }
          }
        }
      }
    }
  }
  
  breaks = breaks[!(breaks$RANK %in% discard),]
  if (!is.null(max.blocks) && dim(breaks)[1] - 1 > max.blocks) {
    ranks = sort(breaks$RANK[breaks$RANK>0])
    breaks = breaks[breaks$RANK < ranks[max.blocks],]    
  }

  return(breaks)
}






####################
# helper functions #
####################

#create binary tree of blocks successively split into smaller blocks
#storing BP range as inclusive for end point, not inclusive for index and filtered index
build.tree = function(breaks) {
  bounds = breaks[breaks$RANK==0,] #should be two
  breaks = breaks[breaks$RANK > 0,]
  breaks = breaks[order(breaks$RANK),]

  tree = list(make.node(1, bounds$POSITION, bounds$INDEX_ALL, bounds$INDEX_FILT, TRUE)); 
  for (i in 1:dim(breaks)[1]) {
    curr.pos = breaks$POSITION[i] 
    split.id = find.node(tree, 1, curr.pos)
    if (is.null(split.id)) stop("NULL id")
    parent = tree[[split.id]]
    
    child.ids = length(tree) + 1:2
    curr.index = breaks$INDEX_ALL[i]; curr.filt = breaks$INDEX_FILT[i]
    tree[[child.ids[1]]] = make.node(child.ids[1], c(parent$position[1], curr.pos), c(parent$index[1], curr.index), c(parent$index.filt[1], curr.filt), TRUE)
    tree[[child.ids[2]]] = make.node(child.ids[1], c(curr.pos, parent$position[2]), c(curr.index, parent$index[2]), c(curr.filt, parent$index.filt[2]), TRUE)
    
    tree[[split.id]]$children = child.ids    
    tree[[split.id]]$break.rank = breaks$RANK[i]
  }
  return(tree)
}

make.node = function(id, position, index, index.filt, shift.end) {
  if (shift.end) {position[2] = position[2] - 1}
  list(id=id, position=position, index=index, index.filt=index.filt, break.rank=NULL, children=NULL)
}
check.nodesize = function(node, index.size, filt.size) {return( (node$index[2] - node$index[1]) >= index.size && (node$index.filt[2] - node$index.filt[1]) >= filt.size )}
in.node = function(node, position) {return(position >= node$position[1] && position <= node$position[2])}
find.node = function(tree, node.id, position) {
  children = tree[[node.id]]$children
  if (!is.null(children)) {
    for (i in 1:length(children)) {if (in.node(tree[[children[i]]], position)) return(find.node(tree, children[i], position))}  
    return(NULL)
  } else {
    return(node.id)
  }
}



