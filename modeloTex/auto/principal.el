;; -*- lexical-binding: t; -*-

(TeX-add-style-hook
 "principal"
 (lambda ()
   (TeX-run-style-hooks
    "config/documento"
    "config/pretextual")
   (TeX-add-symbols
    "autor"
    "disciplina"
    "professor"))
 :latex)

