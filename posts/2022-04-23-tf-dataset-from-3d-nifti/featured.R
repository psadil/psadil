
library(flametree)

# pick some colours
shades <- c(
  "deepskyblue", 
  "darkolivegreen", 
  "gold3",
  "red3")

# data structure defining the trees
d <- flametree_grow(
  time = 6, 
  trees = 2, 
  seed = 365,
  split = 3)

# draw the plot
d |> 
  flametree_plot(
    background = "gainsboro",
    palette = shades, 
    style = "minimal"
  )

ggplot2::ggsave("featured.png", device=ragg::agg_png())
