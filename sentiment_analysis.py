import ollama
import pandas as pd
import json
import csv
import re
import requests
import time
from twarc import Twarc2, expansions
import json
import random

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import nltk
from nltk.corpus import stopwords
import string


def sentiment_analysis(menuno,strin):
    # Start menu
    print("""
---- SENTIMENT ANALYSIS ----
#1 - Analyse manual inputs
#2 - Analyse dataset
#3 - Enter product/brand name
    """)
    # menu = int(input("Enter the function to use: "))
    menu = menuno

    # Initialize user input list
    user_inputs = []

    # Menu handling
    if menu == 1:
        for i in range(0,len(strin)):
            user_inputs.append([ i + 1 , strin[i][1] ])

    elif menu == 2:
        filepath = strin
        try:
            if filepath.endswith(".csv"):
                df = pd.read_csv(filepath)
            elif filepath.endswith(".json"):
                df = pd.read_json(filepath)
            else:
                raise ValueError("Invalid file format. Only .csv and .json are supported.")
            
            user_inputs = [[i + 1, row] for i, row in enumerate(df.iloc[:, 1].dropna())]
            print(f"Loaded {len(user_inputs)} records from dataset.")
        except Exception as e:
            print(f"Error loading dataset: {e}")
            exit()

    elif menu == 3:
        product = strin
        num = 25

        def find_reviews(product, num_reviews=10):

            heat = random.randint(1,2)

            if heat%2 == 0:
                revType = "positive"
            else:
                revType = "negative"

            prompt = f"""Generate {num_reviews} short, informal, anecdotal, and realistic Twitter-style user reviews about {product}.
            Each review should mimic real user experiences, opinions, and emotions. Mix positive, neutral, and negative sentiments.
            Keep each review within 250 characters, and include slang where appropriate.
            Do not use emoji at all for any review.
            Roughly 90% of the reviews should be {revType}.
            Do NOT include any numbering at the beginning of the reviews."""
            
            response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
            
            return response["message"]["content"].split("\n")

        def clean_review(review):
            """Removes leading numbers, extra quotes, and emojis from the review text."""
            review = re.sub(r'^\d+[\).\s"]+', '', review).strip()  # Remove leading numbers like '1.', '2) ', '3. "'
            
            # Emoji removal pattern
            emoji_pattern = re.compile(
                "["
                "\U0001F600-\U0001F64F"  # Emoticons
                "\U0001F300-\U0001F5FF"  # Symbols & pictographs
                "\U0001F680-\U0001F6FF"  # Transport & map symbols
                "\U0001F700-\U0001F77F"  # Alchemical symbols
                "\U0001F780-\U0001F7FF"  # Geometric shapes
                "\U0001F800-\U0001F8FF"  # Supplemental symbols
                "\U0001F900-\U0001F9FF"  # Supplemental symbols and pictographs
                "\U0001FA00-\U0001FA6F"  # Chess symbols, etc.
                "\U0001FA70-\U0001FAFF"  # More symbols
                "\U00002702-\U000027B0"  # Dingbats
                "\U000024C2-\U0001F251"  # Enclosed characters
                "]+", flags=re.UNICODE
            )

            review = emoji_pattern.sub('', review)  # Remove emojis
            return review.strip()

        def save_tweets(prd, n):
            reviews = find_reviews(prd, n)

            # Save to CSV
            output_file = "twitter_reviews.csv"
            with open(output_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["sl.no", "review"])

                for i, review in enumerate(reviews, start=1):
                    clean_text = clean_review(review)
                    if clean_text:  # Skip empty lines
                        writer.writerow([(i//2) + 1, clean_text])  # Fixed the numbering issue

            print("Saved tweets in twitter_reviews.csv")

        def get_tweets(p, n):
            save_tweets(p, n)
            filepath = "twitter_reviews.csv"
            try:
                df = pd.read_csv(filepath)

                # Extract the review column and clean it
                return [[i + 1, clean_review(review)] for i, review in enumerate(df.iloc[:, 1].dropna())]

            except Exception as e:
                print(f"Error: {e}")
                exit()

        user_inputs = get_tweets(product, num)

    elif menu == 4:
        link = input("Enter product link: ")

        def fetch_product_name_and_reviews(l):
            """Scrapes product name and reviews using Selenium from Amazon."""

            options = webdriver.ChromeOptions()
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

            driver.get(l)
            time.sleep(3)

            # Extract product name
            try:
                product_name = driver.find_element(By.ID, "productTitle").text.strip()
            except:
                print("Could not fetch product name.")
                product_name = "unknown_product"

            # Extract reviews
            reviews = driver.find_elements(By.CLASS_NAME, "review-text-content")  
            extracted_reviews = [[i+1, review.text.strip()] for i, review in enumerate(reviews)]
            
            driver.quit()
            return product_name, extracted_reviews

        # Call function
        product_name, user_inputs = fetch_product_name_and_reviews(link)

        def save_reviews_to_csv(reviews, filename):
            """Saves the extracted reviews to a CSV file."""
            
            filename = filename.lower().replace(" ", "_") + "_reviews.csv"

            with open(filename, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Review Number", "Review Text"])  # CSV Header

                cleaned_reviews = [[num, review.replace("\n", " ")] for num, review in reviews]
                writer.writerows(cleaned_reviews)

            print(f"Reviews saved to {filename}")

        save_reviews_to_csv(user_inputs, product_name)
    else:
        print("Invalid selection. Exiting...")
        exit()

    # LLM instructions
    instruction = """
    Respond with only the given format below, and nothing else.

    The given content is a list of lists, where each element contains a number as the first value, 
    and the second value is the text that needs to be sentiment analyzed.
    The result should be "Positive", "Negative", or "Neutral".
    Try using "Neutral" as little as possible.

    Also, mention the level of certainty from 0 to 1, with two decimal places (e.g., 0.34).
    For all reviews given, respond with only one result, which represents all the sentiments consolidated

    In the case where an invalid/empty list is provided, respond with "invalid data presented, please retry"

    **FORMAT START**
    Sentiment: [sentiment]  
    Certainty: [certainty]
    **FORMAT END**

    DO NOT INCLUDE THE START AND END IN YOUR RESPONSE
    Note : make sure the certainty number is above 70%
    The user prompts are:
    """

    full_prompt = f"{instruction}, {user_inputs}"

    # Handle response
    response = ollama.chat(model="llama3", messages=[{"role": "user", "content": full_prompt}])
    print("\nSentiment Analysis Result : ")
    print(response["message"]["content"])

    def generate_wordcloud(user_inputs):
        print("wordcloud created. Unable to view? check opened tabs!")

        # Extract all review texts
        text_data = " ".join([review[1] for review in user_inputs])

        # Define stopwords (common words to exclude)
        stop_words = set(stopwords.words("english")).union(STOPWORDS)

        colours = ''
        if "Positive" in response["message"]["content"]:
            colours = 'viridis'
        else:
            colours = 'autumn'
        # Generate word cloud
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color="white",
            stopwords=stop_words,
            colormap=colours,  # Change color scheme if needed
            max_words=100
        ).generate(text_data)

        # Display the word cloud
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation="bilinear")
        plt.axis("off")  # Hide axes
        plt.title("Word Cloud of Product Reviews", fontsize=14)

        plt.ion()
        plt.show(block=False)

    generate_wordcloud(user_inputs)

    return(response["message"]["content"])