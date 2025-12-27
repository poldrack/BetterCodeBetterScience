FROM python:3.13.9

# Set working directory
WORKDIR /app

# Install wonderwords package
RUN pip install wonderwords==2.2.0

# Copy the Python script into the image from the local directory
COPY random_sentence.py .

# Set the entrypoint to run our script
ENTRYPOINT ["python", "random_sentence.py"]