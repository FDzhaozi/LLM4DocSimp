import os

import csv
import json
import re

from Utiles.preprocess import chinese_character_count, extract_urls, get_webpage_content


def extract_news_articles(file_path: str, category: str, num_articles: int, export_path: str) -> None:
    """
    Extract news articles from a specific category that meet certain criteria.

    Parameters:
    file_path (str): The path to the directory containing news categories.
    category (str): The name of the news category to extract articles from.
    num_articles (int): The number of articles to extract.
    export_path (str): The path to export the extracted articles.
    """
    # Ensure export directory exists
    export_path = os.path.join(export_path, category)
    if not os.path.exists(export_path):
        os.makedirs(export_path)
    finished_num = 0
    # Walk through the directory to find the specified category
    for root, dirs, files in os.walk(file_path):
        if root.endswith(category):
            # Filter and process the files in the specified category
            for file_name in files:
                if file_name.endswith('.txt'):
                    file_path = os.path.join(root, file_name)
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        char_count = chinese_character_count(content)
                        if 600 < char_count < 1500:
                            print(f"passage {file_name} has {char_count} characters")
                            # Export the article if it meets the criteria
                            export_file_path = os.path.join(export_path, file_name)
                            with open(export_file_path, 'w', encoding='utf-8') as export_file:
                                export_file.write(content)
                            num_articles -= 1
                            finished_num += 1
                            if num_articles == 0:
                                break
            if num_articles == 0:
                break
    print(f"Finished extracting {finished_num} articles from the {category} category.")


def extract_wiki_doc(file_path: str, export_path: str) -> None:
    """
    Extracts articles from JSON files in various folders that meet certain criteria.

    Parameters:
    file_path (str): The path to the directory containing folders with JSON files.
    export_path (str): The path to export the extracted articles as a CSV file.
    """
    # Initialize a list to store the extracted articles
    extracted_articles = []
    ext_num = 0
    # Walk through the directory to find JSON files
    for root, dirs, files in os.walk(file_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                jsons = content.split("\n")
                data = "[\n"
                for json_str in jsons:
                    data += json_str + "," + "\n"
                # remove the last comma
                data = data[:-2] + "\n]"
                print(f"data is {data}")
                data = json.loads(data)
                print(f"Extracting articles from {file_name}...")
                print(f"type of data is {type(data)}")
                for entry in data:
                    text = entry.get('text', '')
                    # 将title和text合并
                    text = entry.get('title', '') + "\n" + text
                    char_count = chinese_character_count(text)
                    if 600 < char_count < 1500:
                        # Add the entry to the list if it meets the criteria
                        extracted_articles.append(text)

    # Export the extracted articles to a CSV file
    with open(export_path, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile)
        for article in extracted_articles:
            csv_writer.writerow([article])
            ext_num += 1
    print(f"Finished extracting {ext_num} articles from the Wikipedia dataset.")


def extract_highSchool_reading(raw_str: str):
    urls = extract_urls(raw_str)
    docs = []
    for url in urls:
        print(f"Extracting content from {url}...")
        web_content = get_webpage_content(url)
        print(f"web_content is {web_content}")
        # Use regex to extract the article text
        pattern = r'\(adsbygoogle = window\.adsbygoogle \|\| \[\]\)\.push\(\{\}\);(.*?)\(adsbygoogle = window\.adsbygoogle \|\| \[\]\)\.push\(\{\}\);'
        match = re.search(pattern, web_content, re.DOTALL)
        if match:
            web_content = match.group(1).strip()
        else:
            web_content = "No matching content found."

        article_text = re.sub(r'<.*?>', '', web_content).strip()

        # Clean up any excessive whitespace or newlines
        extracted_content = re.sub(r'\s*\n\s*', '\n', article_text)

        if extracted_content != "No match found":
            print(f"Extracted content: {extracted_content}")
            docs.append(extracted_content)
    return docs if docs else "No match found"
