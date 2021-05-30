source("renv/activate.R")
options(
  blogdown.author = "Patrick Sadil", 
  blogdown.hugo.args = '--minify',
  blogdown.hugo.version = "0.73.0")
if (Sys.getenv("GITHUB_ACTION") == ""){
  options(
    servr.daemon = TRUE,
    blogdown.files_filter = blogdown::filter_md5sum,
    blogdown.initial_files.open = FALSE)
} 
