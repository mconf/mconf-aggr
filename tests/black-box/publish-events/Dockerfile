# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set environment variables
ENV R_INSTITUTION_GUID=
ENV HOOK_URL=
ENV DEBUG_URL=
ENV AUTH_TOKEN=
ENV DRY_RUN=1
ENV QUERY_LIMIT=
ENV START_DATE=
ENV END_DATE=
ENV DB_HOST=
ENV DB_NAME=
ENV DB_USER=
ENV DB_PASSWORD=

# Set the working directory to /script
WORKDIR /script

# Copy the current directory contents into the container at /script
COPY . /script

# Install the required packages
RUN pip install psycopg2-binary
RUN pip install requests

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Run the script when the container launches
CMD ["python", "send_publish_events.py"]