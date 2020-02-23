FROM python:3
LABEL Name=liftjl-server Version=0.1.0 Author="Joshua Loehr"

RUN mkdir -p /home/docker/workspace/liftjl
WORKDIR /home/docker/workspace/liftjl

ENV FLASK_APP server
ENV FLASK_ENV development
EXPOSE 5000

COPY requirements.txt requirements.txt
RUN python3 -m pip install -r requirements.txt

COPY . .

RUN  ssh-keygen -m PEM -t rsa -b 4096 -f ~/.ssh/liftjl_rsa -q -N ""

ENV APP_SETTINGS "server.config.DevelopmentConfig"
# ENV POSTGRES_PASSWORD password

CMD ["./run.sh"]
