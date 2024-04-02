# install dependencies
webr::install("data.table")
webr::install("tibble")
webr::install("dplyr")
webr::install("purrr")

# download the R script for MBMDRc
download.file("https://raw.githubusercontent.com/FedericoMelograna/MBMDRc_R/main/Code/MBMDRc_script.R", "MBMDRc_script.R")
source("MBMDRc_script.R")


Wrapper_MBMDRc = function(p_threshold, is_0_considered, data_path, result_path, model, output, data, d_level){
  d_level = as.numeric(d_level)
  if (d_level == 1){
    Calc_MBMDR_1d(p_threshold, is_0_considered, data_path, result_path, model, output, data)
    print("MBMDRc-1d successfully run")
  } else if (d_level == 2) {
    Calc_MBMDR_2d(p_threshold, is_0_considered, data_path, result_path, model, output, data)
    print("MBMDRc-2d successfully run")
  }
}