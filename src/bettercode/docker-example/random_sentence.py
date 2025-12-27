#!/usr/bin/env python3
"""
A simple script that generates and prints a random sentence using wonderwords.
"""

from wonderwords import RandomSentence

def main():
    # Create a RandomSentence object
    sentence_generator = RandomSentence()
    
    # Generate a random sentence
    random_sentence = sentence_generator.sentence()
    
    # Print the sentence
    print(f"Random sentence: {random_sentence}")

if __name__ == "__main__":
    main()