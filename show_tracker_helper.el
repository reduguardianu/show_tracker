

(defun show-unwatched-episodes ()
  (save-excursion
    (fundamental-mode)
    (beginning-of-buffer)
    (setq number-of-lines (count-lines (point-min) (point-max)))
    (setq line-no 0)
    (setq unwatched (make-hash-table :test 'equal))
    (setq current-title nil)
    (setq episode-list '())
    (setq all-titles '())
    (while (< line-no (+ number-of-lines 1))
      (let (p1 p2 myLine)
        (setq p1 (line-beginning-position) )
        (setq p2 (line-end-position) )
        (setq line (buffer-substring-no-properties p1 p2))
        )
      (if (string-prefix-p "* " line)
          (progn
            (unless (or (eq nil current-title) (eq 0 (list-length episode-list)))
                (progn
                  (puthash current-title (reverse episode-list) unwatched)
                  (add-to-list 'all-titles current-title)
                  (setq episode-list '())
                  )
              )
            (setq current-title line)
           )
          )
      (if (and (string-prefix-p "*** " line) (string-match "UNWATCHED" line))
          (progn
            (add-to-list 'episode-list line)
            )
        )
      (setq line-no (+ line-no 1))
      (next-line)
      )
    )
  (org-mode)
  (if (get-buffer "*unwatched episodes*")
      (kill-buffer "*unwatched episodes*")
    )
  (switch-to-buffer-other-window (generate-new-buffer "*unwatched episodes*"))

  (dolist (title all-titles)
    (insert (concat title "
"))
    (setq episodes (gethash title unwatched))
    (dolist (line episodes)
      (insert (concat line "
"))
      )
    )
  (org-mode)
  (show-all)
  (list-length all-titles)
  )
