(defun anita-up ()
  "Start aniTA web app via docker-compose up."
  (interactive)
  (let ((buffer (make-comint "aniTA-web" "docker-compose" nil "up")))
    (pop-to-buffer buffer)))

(provide 'anita)
