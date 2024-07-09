---


title: "HeuDiConv — flexible DICOM conversion into structured directory layouts"
authors: ["Yaroslav O. Halchenko", "Mathias Goncalves", "Satrajit Ghosh", "Pablo Velasco", "Matteo Visconti di Oleggio Castello", "Taylor Salo", "John T. Wodder", "Michael Hanke", "Patrick Sadil", "Krzysztof Jacek Gorgolewski", "Horea-Ioan Ioanas", "Chris Rorden", "Timothy J. Hendrickson", "Michael Dayan", "Sean Dae Houlihan", "James Kent", "Ted Strauss", "John Lee", "Isaac To", "Christopher J. Markiewicz", "Darren Lukas", "Ellyn R. Butler", "Todd Thompson", "Maite Termenon", "David V. Smith", "Austin Macdonald", "David N. Kennedy"]
date: 2024-07-03
doi: "https://doi.org/10.21105/joss.05839"

# Schedule page publish date (NOT publication's date).
publishDate: 2024-07-03T00:00:00Z

# Publication type.
# Legend: 0 = Uncategorized; 1 = Conference paper; 2 = Journal article;
# 3 = Preprint / Working Paper; 4 = Report; 5 = Book; 6 = Book section;
# 7 = Thesis; 8 = Patent
publication_types: ["2"]

# Publication name and optional abbreviated publication name.
publication: "Journal of Open Source Software"
publication_short: "JOSS"

abstract: "In order to support efficient processing, data must be formatted according to standards that are prevalent in the field and widely supported among actively developed analysis tools. The Brain Imaging Data Structure (BIDS) (Gorgolewski et al., 2016) is an open standard designed for computational accessibility, operator legibility, and a wide and easily extendable scope of modalities — and is consequently used by numerous analysis and processing tools as the preferred input format in many fields of neuroscience. HeuDiConv (Heuristic DICOM Converter) enables flexible and efficient conversion of spatially reconstructed neuroimaging data from the DICOM format (quasi-ubiquitous in biomedical image acquisition systems, particularly in clinical settings) to BIDS, as well as other file layouts. HeuDiConv provides a multi-stage operator input workflow (discovery, manual tuning, conversion) where a manual tuning step is optional and the entire conversion can thus be seamlessly integrated into a data processing pipeline. HeuDiConv is written in Python, and supports the DICOM specification for input parsing, and the BIDS specification for output construction. The support for these standards is extensive, and HeuDiConv can handle complex organization scenarios that arise for specific data types (e.g., multi-echo sequences, or single-band reference volumes). In addition to generating valid BIDS outputs, additional support is offered for custom output layouts. This is obtained via a set of built-in fully functional or example heuristics expressed as simple Python functions. Those heuristics could be taken as a template or as a base for developing custom heuristics, thus providing full flexibility and maintaining user accessibility. HeuDiConv further integrates with DataLad (Halchenko et al., 2021), and can automatically prepare hierarchies of DataLad datasets with optional obfuscation of sensitive data and metadata, including obfuscating patient visit timestamps in the git version control system. As a result, given its extensibility, large modality support, and integration with advanced data management technologies, HeuDiConv has become a mainstay in numerous neuroimaging workflows, and constitutes a powerful and highly adaptable tool of potential interest to large swathes of the neuroimaging community."

# Summary. An optional shortened abstract.
summary: ""

tags: []
categories: []
featured: false

# Custom links (optional).
#   Uncomment and edit lines below to show custom links.
# links:
# - name: Follow
#   url: https://twitter.com
#   icon_pack: fab
#   icon: twitter

url_pdf: https://www.theoj.org/joss-papers/joss.05839/10.21105.joss.05839.pdf
url_code: https://github.com/nipy/heudiconv
url_dataset: 
url_poster: 
url_project: https://joss.theoj.org/papers/10.21105/joss.05839
url_slides:
url_source:
url_video: 
url_preprint: 

# Featured image
# To use, add an image named `featured.jpg/png` to your page's folder. 
# Focal points: Smart, Center, TopLeft, Top, TopRight, Left, Right, BottomLeft, Bottom, BottomRight.
image:
  caption: ""
  focal_point: ""
  preview_only: false

# Associated Projects (optional).
#   Associate this publication with one or more of your projects.
#   Simply enter your project's folder or file name without extension.
#   E.g. `internal-project` references `content/project/internal-project/index.md`.
#   Otherwise, set `projects: []`.
projects: []

# Slides (optional).
#   Associate this publication with Markdown slides.
#   Simply enter your slide deck's filename without extension.
#   E.g. `slides: "example"` references `content/slides/example/index.md`.
#   Otherwise, set `slides: ""`.
slides: ""
---
