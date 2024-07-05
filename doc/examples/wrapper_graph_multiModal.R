#Install libraries
if (R.version$platform == "wasm32-unknown-emscripten") {
  webr::install("igraph")
  webr::install("reshape2")
  #webr::install("limma")
  webr::install("data.table")
  webr::install("dplyr")
  webr::install("stringr")
  webr::install("Hmisc")
  webr::install("NetworkDistance")
  webr::install("kernlab")
} else {
  if (!require("igraph")) {
    install.packages("igraph")
  }
  if (!require("reshape2")) {
    install.packages("reshape2")
  }
  # if (!require("limma")) {
  #   install.packages("limma")
  # }
  if (!require("data.table")) {
    install.packages("data.table")
  }
  if (!require("dplyr")) {
    install.packages("dplyr")
  }
  if (!require("stringr")) {
    install.packages("stringr")
  }
  if (!require("Hmisc")) {
    install.packages("Hmisc")
  }
  if (!require("NetworkDistance")) {
    install.packages("NetworkDistance")
  }
  if (!require("kernlab")) {
    install.packages("kernlab")
  }
}
set.seed(2024)

######################### graph_multimodal_integration.R #################################

library(igraph)
library(reshape2)
# library(limma)
library(data.table)
library(dplyr)
library(stringr)
library(Hmisc)
library(NetworkDistance)
library(kernlab)
set.seed(2022)

graph_multiModal=function(path_train, path_test, nsel_nodes=0.3, cor_edges=0.3, meth="edd", sim=F, C_svm=10){
  
  ##################
  # Initialization #
  ##################
  
  sim_node_train=list()
  sim_node_test=list()
  sim_edge_train=list()
  sim_edge_test=list()
  nodes_selected=list()
  edges_selected=list()
  
  ###############
  # Import data #
  ###############
  
  if(sim==F){
    for(nb_modalities in 1:length(path_train)){
      #Load the data
      y_train_test=list()
      exp_train_test=list()
      nb_samples=c()
      for(train_test in 1:2){ #for train and test
        path=list(path_train, path_test)
        path=path[[train_test]]
        data=fread(path[nb_modalities])
        #Format
        if ("outcome" %in% colnames(data)) {
          y=data.frame(rownames(data), data$outcome)
          colnames(y)=c("sample", "outcome")
          y$outcome=as.factor(y$outcome)
          exp=data.frame(t(data[,2:ncol(data)]))
        } else {
          y=data.frame(rownames(data), NA)
          colnames(y)=c("sample", "outcome")
          y$outcome=as.factor(y$outcome)
          exp=data.frame(t(data))
        }
        colnames(exp)=y$sample
        y_train_test[[train_test]]=y
        exp_train_test[[train_test]]=exp
      }
      nb_samples_train=nrow(y_train_test[[1]])
      nb_samples_test=nrow(y_train_test[[2]])
      exp=exp_train_test[[1]] #train
      exp_test=exp_train_test[[2]] #test
      exp_tot <- do.call(cbind, exp_train_test)
      y_tot <- do.call(rbind, y_train_test)
      y_train=y_tot[1:nb_samples_train,]
      
      #####################
      # Feature selection #
      #####################
      #select the k most variably expressed nodes in the train set
      cvar <- apply(as.array(as.matrix(exp)), 1, sd)
      dat <- cbind(cvar, exp)
      dat <- dat[order(dat[,1], decreasing=T),]
      nsel=floor(nsel_nodes*nrow(exp))
      featuresToKeep=rownames(dat[1:nsel,])
      dat <- as.matrix(dat[featuresToKeep, -1])
      nodes_selected[[nb_modalities]]=featuresToKeep
      
      #outcome-specific networks to select edges that have large absolute differences in their co-expression levels between each pair of scores
      group=list()
      for(i in 1:length(levels(y_train$outcome))){
        group[[i]]=which(as.character(y_train$outcome)==levels(y_train$outcome)[i])
      }
      names(group)=levels(y_train$outcome)
      pairs=combn(levels(y_train$outcome), 2)

      if(is.null(dim(pairs))){ # if we compare 2 groups
        len=1
      } else { len=ncol(pairs) } # if more than 2 groups
      
      tosel=c()
      for(i in 1:len){
        if(len==1){ # if we compare 2 groups
          group1=pairs[1]
          group2=pairs[2]
        } else { # if more than 2 groups
          group1=pairs[1,i]
          group2=pairs[2,i]
        }
        group1=group[group1]
        group2=group[group2]
        netyes <- cor(t(dat[,group1[[1]]]))
        netno <- cor(t(dat[,group2[[1]]]))
        netdiff <- netyes-netno
        cormat2 <- rep(1:nsel, each=nsel) #convert adjacency matrices to edgelists
        cormat1 <- rep(1:nsel,nsel)
        el <- cbind(cormat1, cormat2, c(netdiff))
        melted <- reshape2::melt(upper.tri(netdiff)) #As this is a symmetric adjacency matrix, we takeconvert the upper triangle of the co-expression adjacency matrix into an edge list.
        melted <- melted[which(melted$value),]
        values <- netdiff[which(upper.tri(netdiff))]
        melted <- cbind(melted[,1:2], values)
        genes <- row.names(netdiff)
        melted[,1] <- genes[melted[,1]]
        melted[,2] <- genes[melted[,2]]
        row.names(melted) <- paste(melted[,1], melted[,2], sep=";")
        tosub <- melted
        tosel <- c(tosel, row.names(tosub[which(abs(tosub[,3])>cor_edges),])) #elect edges that have a difference in Pearson R correlation coefficient of at least 0.5
      }
      tosel=unique(tosel)
      edges_selected[[nb_modalities]]=tosel
      
      #################################
      # Similarity matrix: Node level #
      #################################
      #Spearman correlation
      dat_tot <- as.matrix(exp_tot[featuresToKeep, ])
      Knode=rcorr(as.matrix(dat_tot), type  = "spearman")
      Knode=Knode$r
      sim_node_train[[nb_modalities]]=Knode[1:nb_samples_train,1:nb_samples_train]
      sim_node_test[[nb_modalities]]=Knode[(nb_samples_train+1):nrow(Knode),1:nb_samples_train]
      
      #################################
      # Similarity matrix: Edge level #
      #################################
      #Individual network data modality: compute edge weights with the node product
      dat_tot=t(dat_tot)
      data=matrix(nrow=nrow(dat_tot))
      for(i in 1:length(tosel)){ #for each selected variable pair
        edge=str_split_fixed(tosel[i], ";",2)
        tmp=dat_tot[,which(colnames(dat_tot) %in% edge)]
        data=cbind(data, tmp[,1]*tmp[,2])
      }
      data=data[,-1]
      colnames(data)=tosel
      
      #Create 2 separated columns for the variable names
      edges=as.data.frame(str_split_fixed(colnames(data), ";",2))
      colnames(edges)=c("gene1","gene2")
      data=t(data)
      data=cbind(edges, data)
      
      #Convert input to the correct format for ANOVA
      data_all=list()
      el=as.matrix(data[,c(1,2,3)]) 
      lab=names(table(el[,1:2])) #extract the existing node IDs
      for(i in 3:ncol(data)){
        el=as.matrix(data[,c(1,2,i)])
        mat=matrix(0,nrow=length(lab),ncol=length(lab),dimnames=list(lab,lab)) #create a matrix of 0s with the node IDs as rows and columns
        mat[el[,1:2]] <-as.numeric(el[,3])
        mat[el[,2:1]] <- as.numeric(el[,3])
        data_all[[i-2]]=mat
      }
      
      #Similarity matrix: edd
      if(meth=="edd"){
        d=nd.edd(data_all)$D
      }
      d=as.matrix(d)
      Kedge=as.matrix(1/(1+d))
      colnames(Kedge)=y_tot$sample
      rownames(Kedge)=y_tot$sample
      sim_edge_train[[nb_modalities]]=Kedge[1:nb_samples_train,1:nb_samples_train]
      sim_edge_test[[nb_modalities]]=Kedge[(nb_samples_train+1):nrow(Kedge),1:nb_samples_train]
    }
    
    ############################
    # Intermediate integration #
    ############################
    #Average
    X_train=list()
    X_test=list()
    for(i in 1:length(path_train)){
      X_train[[i]]=sim_node_train[[i]]
      X_test[[i]]=sim_node_test[[i]]
    }
    for(i in 1:length(path_train)){
      X_train[[i+length(path_train)]]=sim_edge_train[[i]]
      X_test[[i+length(path_train)]]=sim_edge_test[[i]]
    }
    
    Y_train <- do.call(cbind, X_train)
    Y_test <- do.call(cbind, X_test)
    Y_train <- array(Y_train, dim=c(dim(X_train[[1]]), length(X_train)))
    Y_test <- array(Y_test, dim=c(dim(X_test[[1]]), length(X_test)))
    K_train=apply(Y_train, c(1, 2), mean, na.rm = TRUE)
    K_test=apply(Y_test, c(1, 2), mean, na.rm = TRUE)
    
  } else{ #if similarity matrices are already computed
    X_train=list()
    X_test=list()
    for(i in 1:length(path_train)){ #load the somilarity matrices
      X_train[[i]]=fread(path_train[i])
      X_test[[i]]=fread(path_test[i])
    }
    
    #Average
    Y_train <- do.call(cbind, X_train)
    Y_test <- do.call(cbind, X_test)
    Y_train <- array(Y_train, dim=c(dim(X_train[[1]]), length(X_train)))
    Y_test <- array(Y_test, dim=c(dim(X_test[[1]]), length(X_test)))
    K_train=apply(Y_train, c(1, 2), mean, na.rm = TRUE)
    K_test=apply(Y_test, c(1, 2), mean, na.rm = TRUE)
  }
  
  #######
  # SVM #
  #######

  ## train SVM
  classifier <- ksvm(as.kernelMatrix(K_train), y_tot$outcome[1:nrow(K_train)], type="C-svc", kernel = "matrix", scaling = FALSE, C = C_svm) 
  
  #performance on the test set 
  ypredTest <- predict(classifier, as.kernelMatrix(K_test[,SVindex(classifier), drop = FALSE]))
  #CMTest= table(ypredTest , y_tot[(nrow(K_train)+1):nrow(y_tot), "outcome"])
  #accuracyTest=sum(diag(CMTest))/sum(CMTest)
  
  ##################
  # Export results #
  ##################
  nodes_selected=do.call(cbind, nodes_selected)
  colnames(nodes_selected)=paste("data_modality_", seq(1, length(path_train)), sep="")
  edges_selected=do.call(cbind, edges_selected)
  colnames(edges_selected)=paste("data_modality_", seq(1, length(path_train)), sep="")
  res=list(predicted_group_label=ypredTest,
           nodes_selected=nodes_selected, 
           edges_selected=edges_selected,
           SVM_model=classifier,
           similarity_matrix_train=K_train,
           similarity_matrix_test=K_test)
  save(res, file = "output_graph_multiModality_Integration.Rdata")
}

####################################################################################

#Main function
main <- function(nsel_nodes, cor_edges, C, path_train1, path_train2, path_test1, path_test2){
     path_train = c(path_train1, path_train2)
     path_test = c(path_test1, path_test2)
     graph_multiModal(path_train, path_test, nsel_nodes, cor_edges, meth="edd", sim=F, C)
     "output_graph_multiModality_Integration.Rdata"
}

#Example
# nsel_nodes=0.5 
# cor_edges=0.5
# meth="edd" 
# path_train1=c('data_modality1_train.txt',
#               'data_modality2_train.txt')
# path_test1=c('data_modality1_new.txt',
#              'data_modality2_new.txt')
# C_svm=10
# 
# graph_multiModal(path_train1, path_test1, nsel_nodes=0.3, cor_edges=0.3, meth="edd", C_svm)
