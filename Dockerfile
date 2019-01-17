FROM 21buttons/lambda-builder

COPY Pipfile Pipfile.lock $APP_DIR/

WORKDIR $APP_DIR

RUN pipenv install --deploy \
	&& cp -r .venv/lib/python3.6/site-packages/. $APP_DIR_BUILD

WORKDIR /var/task

CMD make artifact
