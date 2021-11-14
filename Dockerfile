#Step 2: Docker for Application Packaging: Build a Dockerfile with instructions to package the TechTrends application. 
#The Dockerfile should contain the following steps:

#Using a Python base image in version 2.7
FROM python:2.7

#Setting metadata to docker image
LABEL maintainer="Rohit Bhardwaj"

#Creating & setting up a working directory
WORKDIR /app

#Copying files to working directory
COPY /techtrends /app

#Installing packages defined in the requirements.txt file
RUN pip install -r requirements.txt

#Ensuring that the database is initialized with the pre-defined posts in the init_db.py file
RUN python init_db.py

#Exposing the application port to 3111
EXPOSE 3111

#Executing the application at the container start
CMD [ "python", "app.py" ]