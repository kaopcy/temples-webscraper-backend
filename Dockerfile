FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

# to avoid unnessesary copying file we have to trick docker with these command
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

# this line used to run uvicorn server 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]