import pandas as pd
import requests
import os
import sys
from serpapi import GoogleSearch
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Read API key from environment variable
api_key = os.getenv('SERPAPI_KEY')
if not api_key:
    raise ValueError("No API key found in environment variable 'SERPAPI_KEY'.")

# CrossRef base URL
crossref_url = "https://api.crossref.org/works"

# Function to search DOI of an article using CrossRef
def search_doi(title, author, publication):
    """
    Search for the DOI of an article using CrossRef API.

    Args:
        title (str): The title of the article.
        author (str): The author of the article.
        publication (str): The publication/journal name of the article.

    Returns:
        str: DOI of the article if found, None otherwise.
    """
    params = {
        'query.bibliographic': title,
        'query.author': author,
        'query.container-title': publication,
        'rows': 1
    }
    try:
        response = requests.get(crossref_url, params=params, timeout=10)
        response.raise_for_status()
        if response.json()['message']['items']:
            item = response.json()['message']['items'][0]
            return item.get('DOI', None)
    except requests.RequestException as e:
        print(f"Error searching DOI: {e}")
    return None

# Function to get metrics of an article using its DOI from CrossRef
def get_metrics(doi):
    """
    Get metrics of an article using its DOI from CrossRef.

    Args:
        doi (str): The DOI of the article.

    Returns:
        dict: Dictionary with article metrics from CrossRef.
    """
    url = f"https://api.crossref.org/works/{doi}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        message = data['message']
        metrics = {
            'doi': doi,
            'crossref_title': message.get('title', [''])[0],
            'crossref_cited_by_count': int(message.get('is-referenced-by-count', 0)),
            'crossref_published_year': int(message['published-print']['date-parts'][0][0]) if 'published-print' in message else None,
            'crossref_journal': message['container-title'][0].replace('\n', ' ') if 'container-title' in message else '',
            'crossref_authors': ', '.join(
                [f"{author.get('given', '')} {author.get('family', '')}".strip() for author in message.get('author', [])]
            ),
            'crossref_publisher': message.get('publisher', '').replace('\n', ' ')
        }
        return metrics
    except requests.RequestException as e:
        print(f"Error getting metrics from CrossRef: {e}")
    return {
        'doi': doi,
        'crossref_title': None,
        'crossref_cited_by_count': None,
        'crossref_published_year': None,
        'crossref_journal': None,
        'crossref_authors': None,
        'crossref_publisher': None
    }

# Function to search information on Google Scholar using SerpAPI
def search_scholar(title, author, publication):
    """
    Search for information on Google Scholar using SerpAPI.

    Args:
        title (str): The title of the article.
        author (str): The author of the article.
        publication (str): The publication/journal name of the article.

    Returns:
        dict: Dictionary with article metrics from Google Scholar.
    """
    params = {
        "engine": "google_scholar",
        "q": f"{title} {author} {publication}",
        "api_key": api_key
    }
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        if "organic_results" in results and results["organic_results"]:
            article = results["organic_results"][0]
            year = article.get('publication_info', {}).get('year')
            metrics = {
                'scholar_title': article.get('title'),
                'scholar_authors': ', '.join(author['name'] for author in article.get('publication_info', {}).get('authors', [])),
                'scholar_journal': article.get('publication_info', {}).get('journal'),
                'scholar_cited_by_count': int(article.get('inline_links', {}).get('cited_by', {}).get('total', 0)),
                'scholar_publisher': article.get('publication_info', {}).get('publisher'),
                'scholar_published_year': int(year) if year else None
            }
            return metrics
    except requests.RequestException as e:
        print(f"Error searching Google Scholar: {e}")
    return None

def main(input_file, output_file):
    # Read the input CSV file
    df = pd.read_csv(input_file)

    # Create a list to store the metrics
    metrics_list = []

    # Iterate over the articles in the DataFrame
    for _, row in df.iterrows():
        doi = search_doi(row['title'], row['author'], row['publication'])
        crossref_metrics = get_metrics(doi) if doi else {}

        scholar_metrics = search_scholar(row['title'], row['author'], row['publication'])
        
        combined_metrics = {
            'original_title': row['title'],
            'original_author': row['author'],
            'original_publication': row['publication'],
        }

        if scholar_metrics:
            combined_metrics.update({
                'scholar_title': scholar_metrics.get('scholar_title'),
                'scholar_authors': scholar_metrics.get('scholar_authors'),
                'scholar_journal': scholar_metrics.get('scholar_journal'),
                'scholar_cited_by_count': scholar_metrics.get('scholar_cited_by_count'),
                'scholar_publisher': scholar_metrics.get('scholar_publisher'),
                'scholar_published_year': scholar_metrics.get('scholar_published_year'),
            })

        combined_metrics.update({
            'doi': crossref_metrics.get('doi'),
            'crossref_title': crossref_metrics.get('crossref_title'),
            'crossref_cited_by_count': crossref_metrics.get('crossref_cited_by_count'),
            'crossref_published_year': crossref_metrics.get('crossref_published_year'),
            'crossref_journal': crossref_metrics.get('crossref_journal'),
            'crossref_authors': crossref_metrics.get('crossref_authors'),
            'crossref_publisher': crossref_metrics.get('crossref_publisher'),
        })

        metrics_list.append(combined_metrics)

    # Create a new DataFrame with the metrics, ensuring the column order
    columns = [
        'original_title', 'original_author', 'original_publication',
        'scholar_title', 'scholar_authors', 'scholar_journal', 'scholar_cited_by_count', 'scholar_publisher', 'scholar_published_year',
        'doi', 'crossref_title', 'crossref_cited_by_count', 'crossref_published_year', 'crossref_journal', 'crossref_authors', 'crossref_publisher'
    ]
    
    metrics_df = pd.DataFrame(metrics_list, columns=columns)

    # Save the DataFrame with the metrics to a new CSV file
    metrics_df.to_csv(output_file, index=False)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_file> <output_file>")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    main(input_file, output_file)
