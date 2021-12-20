FROM ubuntu:20.04

# Create some base directories
RUN mkdir /code

COPY requirements.txt /requirements.txt

# Set TZ-data environment
ENV TZ=Europa/Amsterdam

# Install base utils
RUN DEBIAN_FRONTEND="noninteractive" \
 && apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get -y install --no-install-recommends tzdata netcat python3 python3-dev python3-pip python3-crypto npm build-essential \
 && pip3 install -r /requirements.txt

# Add source
COPY . /code/
RUN chmod +x /code/init.sh

# Compile vue
RUN cd /code/vue_web_code \
 && npm install \
 && npm run build

# Entrypoint for this docker
RUN chmod +x /code/run.py
WORKDIR /code
ENTRYPOINT /code/init.sh
EXPOSE 7890
