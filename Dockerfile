FROM python:3.11.3-alpine

# Setup working directory
ADD . /sssb
WORKDIR /sssb

# Install dependencies
RUN apk add --no-cache chromium-chromedriver
RUN pip --no-cache-dir install -r requirements.txt

# Run script
CMD ["python", "sssb.py"]
