FROM python
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD python src/app.pyd