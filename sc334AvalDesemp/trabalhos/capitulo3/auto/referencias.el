;; -*- lexical-binding: t; -*-

(TeX-add-style-hook
 "referencias"
 (lambda ()
   (LaTeX-add-bibitems
    "jackson_sorensen_relacoes_internacionais"
    "sergio2021"
    "cpc27"))
 '(or :bibtex :latex))

