# sssb
Script to scrape SSSB's website and send email notifications when new listings are posted

## Docker Image

A docker image built for `linux/amd64`, `linux/arm64`, and `linux/arm/v7` is available on Docker Hub at [andre15silva/sssb:latest](https://hub.docker.com/layers/andre15silva/sssb/latest/images/sha256-993b5102c4529ebf3600233b52eeae1ef5507ccca40d071583086b0d79605f8a?context=repo)

## Docker Compose

An example `docker-compose` configuration:

```yml
version: "3"

services:
  sssb:
    container_name: sssb
    image: andre15silva/sssb:latest
    environment:
      SMTP_SERVER: 'YOUR_SMTP_SERVER'
      SMTP_PORT: YOUR_SMTP_PORT
      SMTP_USERNAME: 'YOUR_USERNAME'
      SMTP_PASSWORD: 'YOUR_PASSWORD'
      EMAIL_FROM: 'FROM_EMAIL'
      EMAIL_TO: 'TO_EMAIL'
      EMAIL_SUBJECT: 'New Student Apartment/Studio Available'
      EXCLUDE_TYPES: '["Corridor room"]'
      EXCLUDE_AREAS: '["Flemingsberg"]'
      TIME_INTERVAL: 300 # 5 minutes
    volumes:
      - './runtime:/sssb'
    restart: unless-stopped
