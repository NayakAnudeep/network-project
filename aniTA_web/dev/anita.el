(defun anita-up ()
  "Start aniTA web app via docker-compose up."
  (interactive)
  (let ((buffer (make-comint "aniTA-web" "docker-compose" nil "up")))
    (pop-to-buffer buffer)))

(defun arango-up ()
  "Start just the Arango DB service with docker-compose."
  (interactive)
  (let ((buffer (make-comint "arangodb" "docker-compose" nil "up" "arangodb")))
    (pop-to-buffer buffer)))

;; (defun anita-local-up ()
;;   "Start aniTA app locally (but use docker for Arango DB)."
;;   (interactive)
;;   (let ((buffer (make-comint "arangodb" "docker-compose" nil "up" "arangodb")))
;;     (pop-to-buffer buffer))
;;   (let* ((path-to-manage-file (expand-file-name "manage.py" (concat (vc-root-dir) "aniTA_web")))
;;          (buffer (make-comint "aniTA-web-local" "python3" nil path-to-manage-file "runserver")))
;;     (pop-to-buffer buffer)))

(provide 'anita)
