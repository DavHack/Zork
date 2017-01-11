FROM ubuntu
RUN apt-get -y update
RUN apt-get -y install python3 python3-pip python3-dev git
RUN pip3 install --upgrade pip
RUN pip3 install flask
RUN mkdir /zorkws
# Add here copy server
WORKDIR /zorkws
EXPOSE 80
