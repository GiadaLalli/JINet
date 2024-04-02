main <- function (rows, cols, iterations) {
  symbols <- c("░", "▒", "▓", "█")

  str <- gsub(
    pattern = "<br>",
    replacement = "",
    x = paste(sample(symbols, rows * cols, TRUE), collapse = ""),
    fixed = TRUE
  )
  dat <- matrix(data = strsplit(str, "")[[1]], nrow = rows, ncol = cols, byrow = TRUE)

  for (i in 1:iterations) {
    r <- sample(2:(rows - 1), 1)
    c <- sample(2:(cols - 1), 1)

    h <- sample(-1:1, 1)
    v <- sample(-1:1, 1)

    dat[r + v, c + h] <- dat[r, c]
  }

  str <- ""
  for (i in 1:rows) {
    row <- paste(dat[i,], collapse = "")
    str <- paste(str, row, sep = "<br>")
  }
  paste(str, "<br>", sep = "")
}