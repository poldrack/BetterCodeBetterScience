# Docker Example - Random Sentence Generator

This example demonstrates how to create a Docker container that generates random sentences using the `wonderwords` Python package.

## Files

- `Dockerfile`: Defines the Docker image based on python:3.13.9
- `random_sentence.py`: Python script that generates and prints a random sentence
- `README.md`: This file

## Building the Docker Image

To build the Docker image, run the following command from this directory:

```bash
docker build -t random-sentence-generator .
```

## Running the Container

Once built, you can run the container with:

```bash
docker run random-sentence-generator
```

Each time you run the container, it will generate and print a new random sentence.

## Example Output

```
Random sentence: The quick brown fox jumps over the lazy dog.
```

Note: The actual output will vary as the sentence is randomly generated each time.