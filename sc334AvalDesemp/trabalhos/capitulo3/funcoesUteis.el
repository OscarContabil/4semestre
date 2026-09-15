(defun latex-renumber-hierarchy ()
  "Renumera linhas de uma tabela LaTeX no formato hierárquico.
Procura linhas do tipo 'x... & Texto\\\\' e substitui por '1.1.2 & Texto\\\\'
de acordo com o número de 'x' no início."
  (interactive)
  (save-excursion
    (let ((counters (make-vector 10 0)))  ;; suporta até 10 níveis
      (while (re-search-forward "^\\(x+\\) *& *\\(.*\\)\\\\\\s-*$" nil t)
        (let* ((level (length (match-string 1))))
          ;; incrementa contador do nível
          (aset counters (1- level) (1+ (aref counters (1- level))))
          ;; zera níveis abaixo
          (dotimes (i (- (length counters) level))
            (aset counters (+ i level) 0))
          ;; monta numeração hierárquica
          (let ((num (mapconcat (lambda (n) (number-to-string n))
                                (seq-take counters level) ".")))
            ;; substitui linha
            (replace-match (concat num " & \\2\\\\") t)))))))
(defun latex-renumber-hierarchy-region (beg end)
  "Renumera linhas de uma tabela LaTeX de x/xx/xxx para numeração hierárquica.
Aplica-se à região selecionada (entre BEG e END)."
  (interactive "r")
  (save-excursion
    (goto-char beg)
    (let ((counters (make-vector 10 0)))
      (while (re-search-forward "^\\(x+\\) *& *\\(.*\\)\\\\\\s-*$" end t)
        (let* ((level (length (match-string 1))))
          ;; incrementa contador do nível
          (aset counters (1- level) (1+ (aref counters (1- level))))
          ;; zera níveis abaixo
          (dotimes (i (- (length counters) level))
            (aset counters (+ i level) 0))
          ;; monta numeração hierárquica
          (let ((num (mapconcat (lambda (n) (number-to-string n))
                                (seq-take counters level) ".")))
            (replace-match (concat num " & \\2\\\\") t)))))))

