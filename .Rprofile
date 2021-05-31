source("renv/activate.R")
options(
  blogdown.author = "Patrick Sadil", 
  blogdown.hugo.args = '--minify',
  blogdown.hugo.version = "0.83.1")
if (Sys.getenv("GITHUB_ACTION") == ""){
  options(
    servr.daemon = TRUE,
    blogdown.files_filter = blogdown::filter_md5sum,
    blogdown.initial_files.open = FALSE)
} else{
  builder <- function(files) { 
    files <- blogdown::filter_md5sum(files) 
    x <- NULL
    for (f in files) { 
      if (!length(grep('^draft: (yes|true)\\s*$', xfun::read_utf8(f)))) x = c(x, f) 
    } 
    x
  }
}
