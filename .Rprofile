source("renv/activate.R")
# Sys.setenv(PATH=glue::glue("/usr/bin:/usr/local/bin:/opt/homebrew/bin:{Sys.getenv('PATH')}"))
options(
  blogdown.author = "Patrick Sadil", 
  blogdown.hugo.args = '--minify',
  blogdown.hugo.version = "0.83.1")
if (Sys.getenv("GITHUB_ACTION") == ""){
  options(
    servr.daemon = TRUE,
    blogdown.initial_files.open = FALSE,
    blogdown.knit.on_save = FALSE,
    blogdown.files_filter = function(files) { 
      files <- blogdown::filter_timestamp(files) 
      x <- NULL
      for (f in files) { 
        if (!length(grep('^draft: (yes|true)\\s*$', xfun::read_utf8(f)))) x = c(x, f) 
      } 
      x
    })
} else{
  builder <- function(files) { 
    files <- blogdown::filter_timestamp(files) 
    x <- NULL
    for (f in files) { 
      if (!length(grep('^draft: (yes|true)\\s*$', xfun::read_utf8(f)))) x = c(x, f) 
    } 
    x
  }
}
