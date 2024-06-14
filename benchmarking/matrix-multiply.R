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


multiply_matrix <- function(size) {
  x <- matrix(rnorm(size^2), ncol = size)
  y <- matrix(rnorm(size^2), ncol = size)
  z <- x %*% y
  return(z)
}

main <- function(discard) {
  results <- bench::press(
    n = c(100, 200, 500, 800),
    {
      bench::mark(
        multiply_matrix(n),
        iterations=100
      )
    }
  )
  
  table <- data.table::data.table(
    time100 = results$time[[1]],
    time200 = results$time[[2]],
    time500 = results$time[[3]],
    time800 = results$time[[4]]
  )

  filename <- paste0("R-matrix-multiply-", R.version$platform, ".csv")
  data.table::fwrite(table, filename)

  filename
}


# Run with: $ OPENBLAS_NUM_THREADS=1 Rscript ./matrix-multiply.R
if (R.version$os == "linux-gnu") {
  main()
}