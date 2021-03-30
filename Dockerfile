# use debian as base image
# FROM debian:latest
FROM python:3.8.3-buster as builder

# get list of installable packets and install wget
RUN apt-get update && \
apt-get -y install \
'wget'

# download snap installer version 7.0
RUN wget http://step.esa.int/downloads/7.0/installers/esa-snap_sentinel_unix_7_0.sh

#change file execution rights for snap installer
RUN chmod +x esa-snap_sentinel_unix_7_0.sh

# install snap with gpt
RUN ./esa-snap_sentinel_unix_7_0.sh -q

# link gpt so it can be used systemwide
RUN ln -s /usr/local/snap/bin/gpt /usr/bin/gpt

# set entrypoint
# ENTRYPOINT ["/usr/local/snap/bin/gpt"]
# CMD ["-h"]

RUN apt-get -y install gdal-bin python-gdal
RUN apt-get -y install libgdal-dev
RUN apt-get -y install python-numpy


# Update C env vars so compiler can find gdal
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
RUN pip3 install numpy
RUN pip3 install GDAL==2.4.2

# set gpt max memory to 4GB
RUN sed -i -e 's/-Xmx2G/-Xmx6G/g' /usr/local/snap/bin/gpt.vmoptions

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY cloud_storage.json /cloud_storage.json

COPY sherlock_snap /sherlock_snap

CMD ["python", "-m", "sentinel_1.main"]
