# install dependencies
webr::install("GeneCycle")
webr::install("huge")
webr::install("combinat")
webr::install("NetworkDistance")
webr::install("graphkernels")
webr::install("progress")
webr::install("stringr")
webr::install("tidyr")
webr::install("KRLS")
webr::install("stats")
webr::install("anocva")
webr::install("data.table")

library("data.table")
library(GeneCycle)
library(huge)
library(combinat)
library(NetworkDistance)
library(graphkernels)
library(progress)
library(stringr)
library(tidyr)
library(KRLS)
library(stats)
library(anocva)

#Define a distance measure
dist_sim=function(G1,G2,maxNodes=NA, meth=NA, mode="undirected"){
  if(meth=="edd"){ #Edge Difference Distance
    d=nd.edd(list(G1,G2))$D
    s=1/(1+d)
  }
  else if(meth=="gdd"){ #Graph Diffusion Distance (via graph Laplacian exponential kernel matrices)
    d=nd.gdd(list(G1,G2))$D
    s=1/(1+d)
  }
  else if(meth=="hamming"){ #hamming
    d=nd.hamming(list(G1,G2))$D
    s=1/(1+d)
  }
  else if(meth=="rbf"){ #Gaussian RBF kernel between vertex label histograms
    G1=graph_from_adjacency_matrix(G1, mode=mode)
    V(G1)$name <- V(G1)
    G2=graph_from_adjacency_matrix(G2, mode=mode)
    V(G2)$name <- V(G2)
    s11=CalculateVertexHistGaussKernel(list(G1,G1), .1)[1,2]
    s=CalculateVertexHistGaussKernel(list(G1,G2), .1)[1,2]
    s22=CalculateVertexHistGaussKernel(list(G2,G2), .1)[1,2]
    d=sqrt(s11-2*s+s22)
  }
  else if(meth=="shortestPathKernel"){ #Linear kernel between edge label histograms
    G1=graph_from_adjacency_matrix(G1, mode=mode)
    V(G1)$name <- V(G1)
    G2=graph_from_adjacency_matrix(G2, mode=mode)
    V(G2)$name <- V(G2)
    s11=CalculateShortestPathKernel(list(G1,G1))[1,2]
    s=CalculateShortestPathKernel(list(G1,G2))[1,2]
    s22=CalculateShortestPathKernel(list(G2,G2))[1,2]
    d=sqrt(s11-2*s+s22)
  }
  else if(meth=="randomWalkKernel"){ #k-step random walk kernel
    G1=graph_from_adjacency_matrix(G1, mode=mode)
    V(G1)$name <- V(G1)
    G2=graph_from_adjacency_matrix(G2, mode=mode)
    V(G2)$name <- V(G2)
    s11=CalculateKStepRandomWalkKernel(list(G1,G1), rep(1, 2))[1,2]
    s=CalculateKStepRandomWalkKernel(list(G1,G2), rep(1, 2))[1,2]
    s22=CalculateKStepRandomWalkKernel(list(G2,G2), rep(1, 2))[1,2]
    d=sqrt(s11-2*s+s22)
  }
  else if(meth=="WLkernel"){ #Weisfeiler-Lehman subtree kernel
    G1=graph_from_adjacency_matrix(G1, mode=mode)
    V(G1)$name <- V(G1)
    G2=graph_from_adjacency_matrix(G2, mode=mode)
    V(G2)$name <- V(G2)
    s11=CalculateWLKernel(list(G1,G1), 5)[1,2]
    s=CalculateWLKernel(list(G1,G2), 5)[1,2]
    s22=CalculateWLKernel(list(G2,G2), 5)[1,2]
    d=sqrt(s11-2*s+s22)
  }  else if(meth=="deltaCon"){
    #Fab 
    g1 <- as(G1, "sparseMatrix") #Construct sparse adjacent matrix
    g2 <- as(G2, "sparseMatrix") #Construct sparse adjacent matrix
    inv1 <- inverse_lbp(g1, maxNodes) * (.p - 0.5) # Naive FaBP
    inv2 <- inverse_lbp(g2, maxNodes) * (.p - 0.5) # Naive FaBP  }
    #Matusita
    d <- sqrt(sum( (sqrt(inv1) - sqrt(inv2))^2 ))
    s=1/(1+d)
  } else if(meth=="GTOM"){
    GTOM_diss1=TOMkdist1(G1,maxNodes)
    GTOM_diss2=TOMkdist1(G2,maxNodes)
    GTOM_sim1=1-GTOM_diss1 #convert dissimilarity measure to similarity measure
    GTOM_sim2=1-GTOM_diss2
    #Matusita
    d <- sqrt(sum( (sqrt(GTOM_sim1) - sqrt(GTOM_sim2))^2 ))
    s=1/(1+d)
  } else if(meth=="randomWalkKernelKNC"){
    G=G1
    format=list()
    for(i in 1:(length(G))){
      tmp_data=G[[i]]
      format[[i]]=graph_from_adjacency_matrix(tmp_data, mode = mode, weighted = T,) 
    }
    par=c(0,0.01,0.01^2, 0.01^3)
    s <- k_RW(G=format, par=par) 
    s=data.frame(s)
    d=matrix(ncol=nrow(s), nrow=nrow(s))
    for(i in 1:nrow(s)){
      for(j in 1:nrow(s)){
        if(j>=i){
          d[i,j]=sqrt(s[i,i]-2*s[i,j]+s[j,j])
        }
      }
    }
    d[lower.tri(d)] = t(d)[lower.tri(d)]
    d=as.matrix(d)
    colnames(d)=seq(1, nrow(d))
    rownames(d)=colnames(d)
    return(list(d,s))
  } else if(meth=="gaussian"){
    data=as.matrix(t(cbind(c(G1), c(G2))))
    simMatrix=gausskernel(X=data,sigma=1000)
    simMatrix=data.frame(simMatrix)
    s11=simMatrix[1,1]
    s=simMatrix[1,2]
    s22=simMatrix[2,2]
    d=sqrt(s11-2*s+s22)
  }
  return(c(d,s))
}

format=function(mat, nbNet){
  mat[lower.tri(mat)] = t(mat)[lower.tri(mat)]
  rownames(mat)=seq(1, nbNet, 1)
  colnames(mat)=seq(1, nbNet, 1)
  return(mat)
}

initialization=function(G, meth, mode="undirected"){
  nbNet=length(G) #number of networks
  names(G) <- seq(1:nbNet)
  
  maxNodes=0 #Derice the maximum number of nodes
  for(i in 1:length(G)){
    maxNodes=max(maxNodes, ncol(G[[i]]))
  }
  
  length_net=c() #compute size of each network
  for(i in 1:length(G)){
    length_net=c(length_net, length(G[[i]]))
  }
  if(var(length_net) == 0){ #if all networks have the same size
    G_vect_adj_tot=list() 
    for (i in 1:length(G)) {   #Create vectorized adjacency matrices for ANOVA
      G_vect_adj_tot[[i]]=sm2vec(G[[i]]) 
    }
    G_vect_adj_tot=do.call(cbind, G_vect_adj_tot)
    colnames(G_vect_adj_tot)=seq(1:ncol(G_vect_adj_tot))
  } else {
    G_vect_adj_tot=NA
  }
  if(meth=="randomWalkKernelKNC"){
    tmp=dist_sim(G1=G, G2=NULL, meth=meth, mode=mode)
    dist_tot=tmp[[1]]
    S_tot=tmp[[2]]
  } else {
    
    # Similarity/distance matrix between graphs
    S_tot=matrix(ncol=nbNet, nrow=nbNet) #S_tot is the similarity matrix
    dist_tot=matrix(ncol=nbNet, nrow=nbNet) #dist_tot is the distance matrix
    #print("Computation of the similarity matrix")
    for(i in 1:nbNet){
      #print(paste("Progression: ", round((i/7)*100) ,"%", sep=""))
      for(j in 1:nbNet){
        if(j>=i){
          tmp=dist_sim(G[[i]], G[[j]], meth=meth, maxNodes, mode=mode)
          dist_tot[i,j]=tmp[1]
          S_tot[i,j]=tmp[2]
        }
      }
    }
    S_tot=format(S_tot, nbNet)
    dist_tot=format(dist_tot, nbNet)
  }
  return(list(G_vect_adj_tot, S_tot, dist_tot))
}


#Normalize funciton for Spectral clustering
normalize <- function(x, na.rm = TRUE) {
  return(x/max(x))
}

netANOVA=function(Dist, t=NULL, method_clust="complete", MT=1, p_threshold=0.05, permutations=99, perturbation=0.2, seed=2021){ #t=threshold, minimum group size, perturbation=percentage of the distance matrix pertubated (the smaller the value, the more stringent it is) 
  set.seed(seed)
  
  if(is.null(t)){
    print("Please choose a minimum number of networks per group")
    return()
  }
  
  if(method_clust=="SpectralClustering"){
    rname=rownames(Dist)
    Dist=sapply(as.data.frame(Dist), function(x) normalize(x))/2
    rownames(Dist)=rname
    colnames(Dist)=rname
  }
  
  original_distance=Dist
  #Create membership output
  membership=data.frame(seq(1, nrow(Dist)), NA)
  colnames(membership)=c("net", "mb")
  outlier="o"
  
  #Run netANOVA algorithm
  output=global(Dist, t, method_clust, MT, membership, outlier, p_threshold, permutations, perturbation, original_distance)
  
  if(length(output)>4){ #if at least 2 groups detected
    
    #Assign groups to networks: only consider an outlier group when smaller groups are detected as significantly different on the right or the left of the outlier
    membership=data.frame(output[which(names(output)%in%c("mb"))]) #gather group ids
    membership <- sapply(membership, as.character)
    membership[is.na(membership)] <- "" #remove NA
    membership=data.frame(membership)
    membership=membership %>% unite('merged', ncol(membership):1, remove=F, sep="") #concatenate the group ids
    membership$net=as.integer(rownames(membership))
    membership=membership[,c("net", "merged")]
    
    #if there is not outlier groups only, assign labels to groups
    outlierOnly=(gsub('o', '', membership$merged))
    outlierOnly[outlierOnly==""]<-NA
    
    if(all(is.na(outlierOnly))==F){
      #Create outlier groups
      groups=data.frame(levels(as.factor(membership$merged)))
      colnames(groups)="groups"
      groups$nbOf_o <- str_count(groups$groups, "o")
      groups=groups[order(-groups$nbOf_o),] #start with the groups with the most "o"
      groups=as.character(groups$groups)
      
      new_groups=groups #Create the "old" to "new" group mapping after assessing if a group can be considered as an outlier group
      for(i in new_groups){ #for each group id
        if((substr(i, 1, 1)!="o") & (substr(i, nchar(i), nchar(i))=="o")){ #if it is an outlier group (ie the group ends with en "o") but not at the top of the dendrogram (ie not start with o)
          tmp_new_groups=new_groups[!new_groups %in% i] #remove the investigated outlier group from the list
          pattern=str_remove(i, "o") #identify the previous group (ie pattern before the "o")
          id=which(substr(tmp_new_groups, 1, nchar(pattern)) == pattern) #identify new_groups starting with this pattern
          if(all(nchar(substr(tmp_new_groups[id], nchar(pattern)+1, nchar(tmp_new_groups[id])))==0)){ #if no significant group after the outlier group
            new_groups[new_groups %in% i]=str_remove(i, "o") #remove the investigated outlier group
          }
        }
      }
      
      #replace group id letters by numbers for readability
      group_id=data.frame(levels(as.factor(new_groups)), seq(1, length(levels(as.factor(new_groups))))) 
      colnames(group_id)=c("new_groups", "group_id")
      mapping=data.frame(groups, new_groups)
      mapping=merge(mapping, group_id, by="new_groups")
      colnames(mapping)=c("new_groups", "merged", "group_id")
      
      #final clusters
      membership=merge(membership, mapping, by="merged")
      membership=membership[,c("net", "group_id")]
      membership=membership[order(membership$net),]
      
      #Remove the group membership from the second part of the output (stastistics and pvalues)
      output[which(names(output)%in%c("net", "mb"))]<-NULL
      
      return(list(membership,output))
      
    }  else { membership=data.frame(seq(1, nrow(Dist)), rep(0, nrow(Dist))) #if no group detected
    colnames(membership)=c("net", "group_id")
    return(list(membership,output)) }
  } else { membership=data.frame(seq(1, nrow(Dist)), rep(0, nrow(Dist))) #if no group detected
  colnames(membership)=c("net", "group_id")
  return(list(membership,output)) }
}


global=function(Dist, t, method_clust, MT, membership, outlier, p_threshold, permutations, perturbation, original_distance){ 
  #Derive a similarity matrix and perform hierarchical clustering
  tmp_membership=membership
  groups=clustering(method_clust, Dist)
  groups$graph=rownames(groups)
  colnames(groups)=c("group", "graph")
  group1=as.factor(groups[groups$group==1,"graph"])
  group2=as.factor(groups[groups$group==2,"graph"])
  s1=length(group1)
  s2=length(group2)
  if(s1>t & s2>t){
    outlier="o" #re-initialize outlier: we only need mutliple "o" when there is a sequence a groups that are too small
    print("group 1 and group 2 are both large enough")
    Pval=multipleTesting_permANOVA(groups, group1, group2, s1, s2, MT, Dist, method_clust, permutations, perturbation, original_distance, t)
    if(Pval[[1]]>p_threshold){
      print("group 1 and group 2 are not significantly different")
      return(Pval[1:4])
    } else { 
      print("group 1 and group 2 are significantly different")
      tmp_membership[as.integer(as.character(group1)),"mb"] = "r" #Create group 1
      tmp_membership[as.integer(as.character(group2)),"mb"] = "l" #Create group 2
      g1=rename(Dist, group1)
      g2=rename(Dist, group2)
      
      return(c(global(g1[[1]], t, method_clust, Pval[[5]], membership, outlier, p_threshold, permutations, perturbation, original_distance),
               global(g2[[1]], t, method_clust, Pval[[5]], membership, outlier, p_threshold, permutations, perturbation, original_distance),
               Pval[1:4], tmp_membership))
    }
  }
  if(s1>t){
    print("group 2 is too small")
    tmp_membership[as.integer(as.character(group2)),"mb"] = outlier #Create group of outlier
    outlier=paste(outlier, "o", sep="")
    g1=rename(Dist, group1)
    return(c(global(g1[[1]], t, method_clust, MT, membership, outlier, p_threshold, permutations, perturbation, original_distance), tmp_membership))
  }
  if(s2>t){
    print("group 1 is too small")
    tmp_membership[as.integer(as.character(group1)),"mb"] = outlier #Create group of outlier
    outlier=paste(outlier, "o", sep="")
    g2=rename(Dist, group2)
    return(c(global(g2[[1]], t, method_clust, MT, membership, outlier, p_threshold, permutations, perturbation, original_distance), tmp_membership))
  }
  print("group 1 and group 2 are both too small")
  return()
}


#Clustering
#from G_vect_adj_tot or distance matrices
clustering=function(method_clust, Dist){ 
  print(method_clust)
  if(method_clust=="SpectralClustering"){
    groups = as.data.frame(spectralClustering(Dist,2)) # the final subtypes information
    colnames(groups)="group"
    rownames(groups)=rownames(Dist)
  } else {
    dend <- hclust(d=as.dist(Dist), method = method_clust)
    groups=as.data.frame(cutree(dend, k=2))
  }
  return(groups)
}

multipleTesting_permANOVA=function(groups, group1, group2, s1=s1, s2=s2, MT, Dist, method_clust, permutations, perturbation, original_distance, t){
  if(MT=="none"){
    Pval=permANOVA_network(groups, group1, group2, s1=s1, s2=s2, tmp_MT=1, Dist, method_clust, permutations, perturbation, original_distance, t)
    return(c(Pval, MT))
  } 
  if(MT=="Meinshausen") {
    Pval=permANOVA_network(groups, group1, group2, s1=s1, s2=s2, tmp_MT=MT, Dist, method_clust, permutations, perturbation, original_distance, t)
    return(c(Pval, MT))
  } else {
    Pval=permANOVA_network(groups, group1, group2, s1=s1, s2=s2, tmp_MT=MT, Dist, method_clust, permutations, perturbation, original_distance, t)
    MT=MT+1
    return(c(Pval, MT))
  }
}


#permANOVA for networks
permANOVA_network=function(groups, group1, group2, s1=s1, s2=s2, tmp_MT, Dist, method_clust, permutations, perturbation, original_distance, t){
  
  #Observed statistics
  groupSize=c(0,s1,s1+s2)
  distances=matrix(nrow=choose(max(groupSize),2), ncol=3)
  a=1
  for(i in 1:(max(groupSize)-1)){
    for(j in (i+1):max(groupSize)){
      distances[a,1]=as.numeric(c(as.character(group1), as.character(group2))[i])
      distances[a,2]=as.numeric(c(as.character(group1), as.character(group2))[j])
      distances[a,3]=original_distance[as.numeric(c(as.character(group1), as.character(group2)))[i],as.numeric(c(as.character(group1), as.character(group2)))[j]]^2
      a=a+1
    } 
  }
  colnames(distances)=c("graph1", "graph2", "distance")
  distances=data.frame(distances)
  SST=sum(distances$distance)/max(groupSize)
  
  ObservedStatistic=compute_stat_ANOVA(distances, SST, groups, sizeGroup1=s1, sizeGroup2=s2) 
  
  #null statistics
  null_distr=c()
  pb <- progress_bar$new(total = permutations)
  k=1
  while(k<permutations){  #create permutations
    triang=(as.matrix(Dist)[upper.tri(as.matrix(Dist), diag = FALSE)])
    id=sample(seq(1,length(triang)), size=floor(perturbation*length(triang))) #perturbation inputed by user (percentage of the distance matrix pertubated, default 0.1. the smaller the value, the more stringent it is.) 
    id=data.frame(id[1:(length(id)/2)], id[((length(id)/2)+1):length(id)])
    for(i in 1:nrow(id)){
      tmp1=triang[id[i,1]]
      tmp2=triang[id[i,2]]
      triang[id[i,1]]=tmp2
      triang[id[i,2]]=tmp1
    }
    tpm_perm=matrix(0,ncol=ncol(Dist), nrow=nrow(Dist))
    tpm_perm[upper.tri(tpm_perm, diag=FALSE)] <- triang
    tpm_perm[lower.tri(tpm_perm)] = t(tpm_perm)[lower.tri(tpm_perm)]
    diag(tpm_perm)=diag(as.matrix(Dist))
    
    #Clustering
    if(method_clust=="SpectralClustering"){
      perm_groups= data.frame(spectralClustering(tpm_perm,2)) # the final subtypes information
    } else {
      dend <- hclust(d=as.dist(tpm_perm), method = method_clust)
      perm_groups=as.data.frame(cutree(dend, k=2))
    }
    perm_groups$graph=rownames(perm_groups)
    colnames(perm_groups)=c("group", "graph")
    perm_group1=as.factor(perm_groups[perm_groups$group==1,"graph"])
    perm_group2=as.factor(perm_groups[perm_groups$group==2,"graph"])
    perm_s1=length(perm_group1)
    perm_s2=length(perm_group2)
    
    if(perm_s1>t & perm_s2>t){ #if the groups contain enough networks
      pb$tick()
      Sys.sleep(1 / 100)
      perm_groupSize=c(0,perm_s1,perm_s1+perm_s2)
      perm_distances=matrix(nrow=choose(max(perm_groupSize),2), ncol=3)
      a=1
      for(i in 1:(max(perm_groupSize)-1)){
        for(j in (i+1):max(perm_groupSize)){
          perm_distances[a,1]=as.numeric(c(as.character(perm_group1), as.character(perm_group2))[i])
          perm_distances[a,2]=as.numeric(c(as.character(perm_group1), as.character(perm_group2))[j])
          perm_distances[a,3]=tpm_perm[as.numeric(c(as.character(perm_group1), as.character(perm_group2)))[i],as.numeric(c(as.character(perm_group1), as.character(perm_group2)))[j]]^2
          a=a+1
        } 
      }
      colnames(perm_distances)=c("graph1", "graph2", "distance")
      perm_distances=data.frame(perm_distances)
      SST=sum(perm_distances$distance)/max(perm_groupSize)
      
      null_distr=c(null_distr, compute_stat_ANOVA(perm_distances, SST, perm_groups, sizeGroup1=perm_s1, sizeGroup2=perm_s2))
      k=k+1
    }  
  }
  
  
  #Compute the P-value
  null_distr=data.frame(null_distr)
  smaller_testStat=null_distr[abs(null_distr$null_distr)>=abs(ObservedStatistic),]
  Pvalue=(length(smaller_testStat)+1)/(nrow(null_distr)+1) #add +1 for non exact test because true cluster is not necessarily included in permutations
  
  #Correction for multiple testing
  if(is.numeric(tmp_MT)==T){ #if no correction or Bonferroni correction
    corrected_Pvalue=Pvalue*tmp_MT
  } else { #if correction from "Hierarchical testing of variable importance", Nicolai Meinshausen (2008)
    corrected_Pvalue=Pvalue*((ncol(original_distance)-1)/(max(groupSize)-1))
  }
  return(c(corrected_Pvalue, list(group1), list(group2), ObservedStatistic))
  #return(c(corrected_Pvalue, list(group1), list(group2), ObservedStatistic, null_distr))
}



#compute_stat_ANOVA
compute_stat_ANOVA <- function(distances, SST, groups,  sizeGroup1, sizeGroup2){
  
  colnames(distances)=c("graph", "graph2", "distance")
  distances=merge(distances, groups, by="graph")
  
  colnames(distances)=c("graph1", "graph", "distance", "group1")
  distances=merge(distances, groups, by="graph")
  distances=distances[,c(2,1,4,5,3)]
  colnames(distances)=c("graph1", "graph2", "group1", "group2","distance")
  
  distances_withinGroup1=distances[distances$group1==1 & distances$group2==1,]
  SSR_1=sum(distances_withinGroup1$distance)/length(unique(c(distances_withinGroup1$graph1, distances_withinGroup1$graph2)))
  distances_withinGroup2=distances[distances$group1==2 & distances$group2==2,]
  SSR_2=sum(distances_withinGroup2$distance)/length(unique(c(distances_withinGroup2$graph1, distances_withinGroup2$graph2)))
  SSR=SSR_1+SSR_2
  
  observed_statT=(((sizeGroup1+sizeGroup2)-2)/(2-1))*((SST-SSR)/SSR) #2 is for the number of clusters
}

rename=function(Dist, group){
  Dist1=Dist[as.character(group),as.character(group)]
  return(list(Dist1))
}



#Main function
netanova <- function(Dist, t=5, method_clust="complete", MT=1, p_threshold=0.05, permutations=99, perturbation=0.2, seed=2021){
  Dist=as.matrix(fread(Dist))
  if (any(is.na(Dist))) {
     stop("The distance matrix contains missing values. Please remove or impute them before running netANOVA.")
  }
  colnames(Dist)=seq(1, ncol(Dist))
  rownames(Dist)=seq(1, nrow(Dist))
  multiple_testing_num <- as.integer(MT)
  if (!is.na(multiple_testing_num)) {
     MT <- multiple_testing_num
  }
  res <- netANOVA(Dist, t, method_clust, MT, p_threshold, permutations, perturbation, seed)
  save(res, file = "output_neANOVA.Rdata")
  "output_neANOVA.Rdata"
}

#Example
#netanova(Dist="/Users/diane/Documents/2024/Giada/output.txt", t=5)
