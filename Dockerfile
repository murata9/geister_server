FROM ubuntu:18.04

RUN apt-get update && apt-get install -y python3 python3-pip

COPY server/requirements.txt /usr/src/app/requirements.txt
RUN python3 -m pip install --no-cache-dir -r /usr/src/app/requirements.txt

COPY server/run.py /usr/src/app

EXPOSE 5000

# CMD ["python3", "/usr/src/app/run.py"]
CMD ["ls", "/usr/src/app/"]
