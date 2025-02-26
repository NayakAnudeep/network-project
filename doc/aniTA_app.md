# Running the app:

```sh
cd CuBigDataProject2025/aniTA_web
docker-compose up
```

Visit `localhost:8000/app`

# Committing and Pushing Changes.

1.  Create a git branch for your changes.
2.  Commit.
3.  Push to github:
    
    ```sh
    git push --set-upstream origin <branch_name>
    ```
4.  Then go to github and select **create pull request**.

# Adding a Route (e.g. `localhost:8000/app/myroute`)

To create a new route, go to `aniTA_web/aniTA_app/views.py`, add a method which accepts a request (and perhaps a query parameter). Go to `aniTA_web/aniTA_app/urls.py` and update `urlpatterns` with the new path, as in the examples. Finally, you'll probably want to write out your html in a separate file, so go to `aniTA_web/aniTA_app/templates/aniTA_app/` and put your new html file in that directory. See the examples in views for how to return the rendered html.
