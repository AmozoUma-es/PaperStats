
# PaperStats

PaperStats is a Python script to obtain scientific article metrics from CrossRef and Google Scholar using SerpAPI. The script takes a CSV file with article information and generates a new CSV with additional metrics.

## Requirements

- Python 3.6 or higher
- SerpAPI API key

## Installation

1. Clone this repository or download the files.

2. Install the dependencies using `pip`:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Obtain an API key from SerpAPI by creating an account at [SerpAPI](https://serpapi.com/).

2. Create a `.env` file in the root of your project directory and add your API key:

   ```plaintext
   SERPAPI_KEY=YOUR_SERPAPI_API_KEY
   ```

## CSV Input Structure

The input CSV file should have the following structure with columns `title`, `author`, and `publication`:

```csv
title,author,publication
"Title of the first article","First Author","Journal Name"
"Title of the second article","Second Author","Journal Name"
"Title of the third article","Third Author","Journal Name"
```

## Usage

Run the script by passing the input CSV file and the output CSV file as arguments:

```bash
python script.py <input_file.csv> <output_file.csv>
```

For example:

```bash
python script.py articles.csv articles_with_metrics.csv
```

## Example

If you have an `articles.csv` file with the following content:

```csv
title,author,publication
"Title of the first article","First Author","Journal Name"
"Title of the second article","Second Author","Journal Name"
"Title of the third article","Third Author","Journal Name"
```

And you run the following command:

```bash
python script.py articles.csv articles_with_metrics.csv
```

You will get an `articles_with_metrics.csv` file with additional metrics obtained from CrossRef and Google Scholar.

## Notes

- Ensure you have an internet connection, as the script makes requests to external APIs.
- If requests to CrossRef or SerpAPI fail, errors will be handled and the script will continue processing the next articles.
