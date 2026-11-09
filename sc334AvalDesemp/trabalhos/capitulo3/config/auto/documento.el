;; -*- lexical-binding: t; -*-

(TeX-add-style-hook
 "documento"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-class-options
                     '(("report" "12pt" "openright" "oneside" "a4paper" "english" "brazil")))
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("lmodern" "") ("tcolorbox" "most") ("fontenc" "T1") ("inputenc" "utf8") ("babel" "brazil") ("comment" "") ("natbib" "colon") ("lipsum" "") ("ctable" "") ("multirow" "") ("array" "") ("float" "") ("longtable" "") ("xcolor" "") ("colortbl" "") ("booktabs" "") ("graphicx" "") ("subfig" "") ("caption" "") ("epstopdf" "") ("amsmath" "") ("nomencl" "") ("hyperref" "") ("cleveref" "") ("indentfirst" "") ("color" "") ("microtype" "") ("lastpage" "") ("multicol" "") ("titlesec" "")))
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "path")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "url")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "nolinkurl")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "hyperbaseurl")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "hyperimage")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "href")
   (add-to-list 'LaTeX-verbatim-macros-with-delims-local "path")
   (TeX-run-style-hooks
    "latex2e"
    "report"
    "rep12"
    "lmodern"
    "tcolorbox"
    "fontenc"
    "inputenc"
    "babel"
    "comment"
    "natbib"
    "lipsum"
    "ctable"
    "multirow"
    "array"
    "float"
    "longtable"
    "xcolor"
    "colortbl"
    "booktabs"
    "graphicx"
    "subfig"
    "caption"
    "epstopdf"
    "amsmath"
    "nomencl"
    "hyperref"
    "cleveref"
    "indentfirst"
    "color"
    "microtype"
    "lastpage"
    "multicol"
    "titlesec")
   (TeX-add-symbols
    "newline"
    "preambulo")
   (LaTeX-add-array-newcolumntypes
    "L"
    "C"
    "R"))
 :latex)

