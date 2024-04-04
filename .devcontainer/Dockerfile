FROM mcr.microsoft.com/devcontainers/python:1-3.8-bookworm
RUN sudo apt-get update && sudo apt-get -y upgrade
RUN wget https://download.oracle.com/java/21/latest/jdk-21_linux-x64_bin.deb
RUN sudo dpkg -i jdk-21_linux-x64_bin.deb
RUN wget https://archive.apache.org/dist/maven/maven-3/3.8.2/binaries/apache-maven-3.8.2-bin.tar.gz
RUN tar -xvzf apache-maven-3.8.2-bin.tar.gz
RUN mv apache-maven-3.8.2 /opt/maven-3.8.2
ENV MAVEN_HOME /opt/maven-3.8.2
ENV PATH $MAVEN_HOME/bin:$PATH