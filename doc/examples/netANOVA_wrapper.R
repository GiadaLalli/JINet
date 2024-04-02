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

# download the R script for netANOVA main function
download.file("https://raw.githubusercontent.com/DianeDuroux/netANOVA/main/netANOVA.R", "netanova.R", method = "auto")
source("netanova.R")

#Main function
netanova <- function(Dist, t=5, method_clust="complete", MT=1, p_threshold=0.05, permutations=99, perturbation=0.2, seed=2021){
  Dist=as.matrix(fread(Dist))
  colnames(Dist)=seq(1, ncol(Dist))
  rownames(Dist)=seq(1, nrow(Dist))
  res <- netANOVA(Dist, t, method_clust, MT, p_threshold, permutations, perturbation, seed)
  save(res, file = "output_neANOVA.Rdata")
  "output_neANOVA.Rdata"
}

#Example
#netanova(Dist="/Users/diane/Documents/2024/Giada/output.txt", t=5)
