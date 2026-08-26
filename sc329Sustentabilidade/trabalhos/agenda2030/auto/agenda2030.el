;; -*- lexical-binding: t; -*-

(TeX-add-style-hook
 "agenda2030"
 (lambda ()
   (TeX-run-style-hooks
    "config/documento"
    "config/pretextual")
   (TeX-add-symbols
    "autor"
    "disciplina"
    "professor"))
 :latex)

