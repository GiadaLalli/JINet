if (R.version$platform == "wasm32-unknown-emscripten") {
  webr::install("bench")
  webr::install("data.table")
} else {
  if (!require("bench")) {
    install.packages("bench")
  }
  if (!require("data.table")) {
    install.packages("data.table")
  }
}

library(bench)
library(data.table)


coin_flips <- function(number) {
  outcomes <- sample(c("H", "T"), number, replace = TRUE)
  sum(outcomes == "H")
}

main <- function(discard) {
  results <- bench::press(
    n = c(10^4, 10^5, 10^6, 10^7),
    {
      bench::mark(
        coin_flips(n),
        iterations=100
      )
    }
  )
  
  table <- data.table::data.table(
    time10000 = results$time[[1]],
    time100000 = results$time[[2]],
    time1000000 = results$time[[3]],
    time10000000 = results$time[[4]]
  )

  filename <- paste0("R-coin_flips-", R.version$platform, ".csv")
  data.table::fwrite(table, filename)

  filename
}


# Run with: $ OPENBLAS_NUM_THREADS=1 Rscript ./sort.R
if (R.version$os == "linux-gnu") {
  main()
}