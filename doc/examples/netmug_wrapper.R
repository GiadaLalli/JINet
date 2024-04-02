
# install dependencies
webr::install("SmCCNet")
webr::install("dynamicTreeCut")
webr::install("PMA")

requireNamespace("PMA", quietly = TRUE)

# download the R script for netMUG
download.file("https://raw.githubusercontent.com/ZuqiLi/netMUG/main/R/netMUG.R", "netmug.R")
source("netmug.R")


##################### Vendored functions from SmCCNet 0.99.0 ########################

getMultiOmicsModules <- function(Abar, P1, CutHeight = 1-.1^10, PlotTree = TRUE){

    hc <- stats::hclust(stats::as.dist(1 - Abar))
    if(PlotTree){graphics::plot(hc)}
    cut.merge <- hc$merge[hc$height < CutHeight, ]
    lower.leaves <- sort(-cut.merge[cut.merge<0])

    grpID <- stats::cutree(hc, h = CutHeight)
    id <- grpID[lower.leaves]
    M <- lapply(seq_len(length(unique(id))), function(x){
        M.x <- lower.leaves[which(id == unique(id)[x])]
        return(M.x)
    })

    multiOmicsModule <- lapply(M, function(s){
        s.min <- min(s)
        s.max <- max(s)
        if(s.min <= P1 & s.max > P1)return(s)
    })

    if(length(multiOmicsModule) > 1){
        nullSet <- which(vapply(multiOmicsModule, is.null, logical(1)))
        if(length(nullSet) > 0){
            multiOmicsModule <- multiOmicsModule[-nullSet]
        }
    }

    return(multiOmicsModule)
}

getAbar <- function(Ws, P1 = NULL, FeatureLabel = NULL){
    

    if(is.null(dim(Ws))){
        Abar <- Matrix::Matrix(abs(Ws) %o% abs(Ws), sparse = TRUE)
    }else{
        b <- nrow(Ws)
        Abar <- matrix(0, nrow = b, ncol = b)
        for(ind in seq_len(ncol(Ws))){
            w <- abs(Ws[ , ind])
            A <- Matrix::Matrix(w %o% w, sparse = TRUE)
            Abar <- Abar + A
        }
    }

    diag(Abar) <- 0
    Abar <- Abar/max(Abar)

    if(is.null(colnames(Abar))){
        if(is.null(FeatureLabel)){
            if(is.null(P1)){
                stop("Need to provide FeatureLabel or the number of features 
                    for the first data type P1.")
            }else{
                p <- ncol(Abar)
                FeatureLabel <- c(paste0("TypeI_", seq_len(P1)), 
                                  paste0("TypeII_", seq_len(p-P1)))
            }
        }
        colnames(Abar) <- rownames(Abar) <- FeatureLabel
    }

    return(Abar)
}

getCCAout <- function(X1, X2, Trait, Lambda1, Lambda2, CCcoef = NULL,
                      NoTrait = FALSE, FilterByTrait = FALSE, trace = FALSE){
  # Compute CCA weights.
  #
  # X1: An n by p1 mRNA expression matrix.
  # X2: An n by p2 miRNA expression matrix.
  # Trait: An n by k trait data for the same samples (k >=1).
  # Lambda1, Lambda2: LASSO pentalty parameters, need to be between 0 and 1.
  # CCcoef: A 3 by 1 vector indicating weights for each pairwise canonical
  #   correlation.
  # NoTrait: Logical. Whether trait information is provided.
  # FilterByTrait: Logical. Whether only the features with highest correlation
  #   to Trait will be assigned nonzero weights. The top 80% features are reserved.
  # trace: Logical. Whether to display CCA algorithm trace.

  if(abs(Lambda1 - 0.5) > 0.5){
      stop("Invalid penalty parameter. Lambda1 needs to be between zero and
           one.")}
  if(abs(Lambda2 - 0.5) > 0.5){
      stop("Invalid penalty parameter. Lambda2 needs to be between zero and
           one.")}
  if(min(Lambda1, Lambda2) == 0){
      stop("Invalid penalty parameter. Both Lambda1 and Lambda2 has to be
           greater than 0.")
  }

  k <- ncol(Trait)    
  if(NoTrait | is.null(k)){
      out <- PMA::CCA(X1, X2, typex = "standard", typez = "standard", 
                      penaltyx = Lambda1, penaltyz = Lambda2, K = 1, 
                      trace = trace)
  }else{
      if(FilterByTrait){
          if(k > 1){
              stop("'FilterByTrait == TRUE' only allows one trait at a time.")
          }else{
              out <- PMA::CCA(X1, X2, outcome = "quantitative", y = Trait,
                              typex = "standard", typez = "standard", 
                              penaltyx = Lambda1, penaltyz = Lambda2, K = 1, 
                              trace = trace)
          }
      }else{
          xlist <- list(x1 = X1, x2 = X2, y = scale(Trait))
          L1 <- max(1, sqrt(ncol(X1)) * Lambda1)
          L2 <- max(1, sqrt(ncol(X2)) * Lambda2)
          out <- myMultiCCA(xlist, penalty = c(L1, L2, sqrt(ncol(Trait))),
                            CCcoef = CCcoef, trace = trace)
          out$u <- out$ws[[1]]; out$v <- out$ws[[2]]
      }
  }

  return(out)
}


getRobustPseudoWeights <- function(X1, X2, Trait, Lambda1, Lambda2,
                                   s1 = 0.7, s2 = 0.7, NoTrait = FALSE, 
                                   FilterByTrait = FALSE, SubsamplingNum = 1000,
                                   CCcoef = NULL, trace = FALSE){

  if(min(s1, s2) == 0){
    stop("Subsampling proprotion needs to be greater than zero.")
  }else{
    if((abs(s1 - 0.5) > 0.5) | (abs(s2 - 0.5) > 0.5)){
      stop("Subsampling proportions can not exceed one.")}
  }

  if(abs(Lambda1 - 0.5) > 0.5 | Lambda1 == 0){
    stop("Invalid penalty parameter. Lambda1 needs to be between zero and one.")}
  if(abs(Lambda2 - 0.5) > 0.5 | Lambda2 == 0){
    stop("Invalid penalty parameter. Lambda2 needs to be between zero and one.")}

  p1 <- ncol(X1); p2 <- ncol(X2); p <- p1 + p2
  p1.sub <- ceiling(s1 * p1);   p2.sub <- ceiling(s2 * p2)
  X <- cbind(X1, X2)

  beta <- pbapply::pbsapply(seq_len(SubsamplingNum), function(x){
    # Subsample features
    samp1 <- sort(sample(seq_len(p1), p1.sub, replace = FALSE))
    samp2 <- sort(sample(seq_len(p2), p2.sub, replace = FALSE))

    x1.par <- scale(X1[ , samp1], center = TRUE, scale = TRUE)
    x2.par <- scale(X2[ , samp2], center = TRUE, scale = TRUE)

    out <- getCCAout(x1.par, x2.par, Trait, Lambda1, Lambda2,
                       NoTrait = NoTrait, FilterByTrait = FilterByTrait,
                       trace = trace, CCcoef = CCcoef)

    w <- rep(0, p)
    w[samp1] <- out$u
    w[samp2 + p1] <- out$v
    coeff.avg <- w

    return(coeff.avg)
  })

  return(beta)
}

#####################################################################################


netmug <- function(X, Y, Z, l1, l2, s1, s2) {
  res <- netMUG(read.table(X, header = F, sep = ","), read.table(Y, header = F, sep = ","), unlist(read.table(Z, header = F)), l1, l2, s1, s2)
  save(res, file = "output.Rdata")
  "output.Rdata"
}