FROM ubuntu:16.04
LABEL maintainer="Philipp Behmer - https://github.com/PhilippBehmer"


# System update and install tools
RUN apt-get update \
 && apt-get install git python-pip -y --no-install-recommends \
 && apt-get autoremove -y \
 && apt-get clean \
 && rm -rvf /var/lib/apt/lists/*

# Install Cl0neMast3r into /opt
WORKDIR /opt
RUN git clone https://github.com/Abdulraheem30042/Cl0neMast3r.git \
 && cd Cl0neMast3r \
 && pip install -r requirements.txt

# Create volume
VOLUME /opt

# Run Cl0neMast3r when the container is started
WORKDIR /opt/Cl0neMast3r
CMD ["/usr/bin/python","Cl0neMast3r.py"]
