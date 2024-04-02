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

# download the R script for netANOVA initialization function
download.file("https://raw.githubusercontent.com/DianeDuroux/netANOVA/main/netANOVA.R", "netanova.R", method = "auto")
source("netanova.R")

#Main function
netanovaPreprocessing <- function(path, meth){
  list_of_files=unzip(path, list = TRUE)$Name
  list_of_files <- list_of_files[grep("\\.csv$|\\.txt$", list_of_files)]
  data <- list()
  for (file in list_of_files) {   # Iterate over each CSV file and load it
    data[[file]] <- fread(unzip(path, files = file))     # Read the CSV file and append to the data list
  }
  data <- lapply(data, function(x) as.matrix(x))
  res <- initialization(data, meth)[[3]]
  fwrite(data.frame(res), file = "output.txt")
  "output.txt"
}

#Example
#netanovaPreprocessing(path="/Users/diane/Documents/2024/Giada/data.zip", meth="edd")
