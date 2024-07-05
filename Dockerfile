FROM python:3.10-slim

# Install necessary packages
RUN apt-get update && apt-get -y install curl unzip git

# Set work directory to /tmp for initial installations
WORKDIR /tmp

# Define build arguments for AWS CLI and SAM CLI URLs
ARG AWSCLI_URL="https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip"
ARG AWS_SAMCLI_URL="https://github.com/aws/aws-sam-cli/releases/latest/download/aws-sam-cli-linux-x86_64.zip"

# Install AWS CLI
RUN curl "$AWSCLI_URL" -o "awscli.zip" \
    && unzip awscli.zip \
    && ./aws/install \
    && rm -rf aws*

# Install AWS SAM CLI
RUN curl -L "$AWS_SAMCLI_URL" -o "aws-sam.zip" \
    && unzip aws-sam.zip -d aws \
    && ./aws/install \
    && rm -rf aws*

# Set the timezone
ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Copy the requirements.txt file into the image
COPY layers/guia-libs/requirements.txt /tmp/requirements.txt

# Update pip and install Python dependencies
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

# Create a non-root user with the same UID and GID as the local user
ARG USER_ID=1000
ARG GROUP_ID=1000
RUN groupadd -g $GROUP_ID myuser \
    && useradd -u $USER_ID -g $GROUP_ID -m myuser \
    && chown -R myuser:myuser /home/myuser

USER myuser
WORKDIR /home/myuser
