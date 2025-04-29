FROM jenkins/jenkins:lts

USER root

RUN apt-get update && \
  apt-get install -y docker.io curl jq && \
  usermod -aG docker jenkins && \
  mkdir -p /usr/local/lib/docker/cli-plugins && \
  curl -SL https://github.com/docker/compose/releases/download/v2.27.1/docker-compose-linux-x86_64 -o /usr/local/lib/docker/cli-plugins/docker-compose && \
  chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

USER jenkins
