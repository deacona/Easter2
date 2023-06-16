FROM tensorflow/tensorflow:2.12.0-jupyter

RUN apt-get update && apt-get install -y python3-opencv

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

CMD /bin/bash