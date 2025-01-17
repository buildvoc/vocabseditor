FROM python:3.8-buster


RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install nginx vim postgresql-common libpq-dev python3-gdal -y
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

COPY nginx.default /etc/nginx/sites-available/default

# copy source and install dependencies
RUN mkdir -p /opt/app
RUN mkdir -p /opt/app/vocabseditor
COPY requirements.txt start-server.sh /opt/app/
RUN pip install -r /opt/app/requirements.txt --no-cache-dir && pip install gunicorn --no-cache-dir
COPY . /opt/app/vocabseditor/
WORKDIR /opt/app
RUN chown -R www-data:www-data /opt/app

# start server
EXPOSE 80
STOPSIGNAL SIGTERM
CMD ["/opt/app/start-server.sh"]