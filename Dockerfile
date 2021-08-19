# Get selenium and base image
# This is a setup for docker environment, you can use it to build your own instance 
# To build the image simply run: "docker build . -t synackapi"
# This will result on a docker image on your system under the name synackapi 
# To run the docker image use: "docker run -d --name synackapi --dns 8.8.8.8 --rm -v ~/.synack:/root/.synack synackapi"
# The above will run the docker in the background and it will simply poll and register all new targets
# To run the mission bot you can execute "docker run --name synackapi -ti --dns 8.8.8.8 --rm -v ~/.synack:/root/.synack synackapi python3 bot.py" 
# Or from inside the running docker simply connect to it using : "docker exec -ti synackapi /bin/bash", and run python3 bot.py from there.
FROM selenium/standalone-firefox

USER root
RUN apt update
RUN apt-get install python3-pip -y
RUN apt-get install python3-distutils -y
RUN python3 -m pip install selenium

RUN mkdir /root/.synack
# set the working directory in the container
WORKDIR /synackAPI

ENV HOME=/root

RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.29.1/geckodriver-v0.29.1-linux64.tar.gz
RUN tar xzf geckodriver-v0.29.1-linux64.tar.gz && mv geckodriver /usr/bin/

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY ./ .

# command to run on container start
CMD [ "python3", "/synackAPI/polling.py" ]
