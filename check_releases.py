import requests
import json
import os
from urllib.parse import urlparse
from datetime import datetime
import pytz


def get_latest_release_info(github_user, repo_name):
    api_url = f"https://api.github.com/repos/{github_user}/{repo_name}/releases/latest"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        return data.get('tag_name'), data.get('published_at')
    return None, None

def parse_github_url(url):
    path = urlparse(url).path
    parts = path.strip('/').split('/')
    if len(parts) >= 2:
        return parts[0], parts[1]
    return None, None

def read_repos_from_file(file_path):
    if not os.path.exists(file_path):
        print(f"The file '{file_path}' does not exist. Please create it and add GitHub repository URLs into it.")
        return []
    with open(file_path, 'r') as file:
        return [line.strip() for line in file]

def load_cached_data(cache_folder, user, repo):
    cache_path = os.path.join(cache_folder, user, f'{repo}.json')
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as file:
            return json.load(file)
    return {}

def save_cache_data(cache_folder, user, repo, data):
    user_folder = os.path.join(cache_folder, user)
    os.makedirs(user_folder, exist_ok=True)
    cache_path = os.path.join(user_folder, f'{repo}.json')
    with open(cache_path, 'w') as file:
        json.dump(data, file, indent=4)

# format date to a more readable format
# "2023-10-06T13:39:06Z"  to X hours ago or Y days ago or Z months ago 
def date_format(date_string):
    now = datetime.now(pytz.UTC)
    date = datetime.fromisoformat(date_string[:-1])
    #date = date.astimezone(pytz.UTC)
    date = date.replace(tzinfo=pytz.UTC)  # Set timezone to UTC
    diff = now - date
    if diff.days > 30:
        return f"{diff.days//30} months ago"
    elif diff.days > 0:
        return f"{diff.days} days ago"
    else:
        return f"{diff.seconds//3600} hours ago"


def main():
    repo_file = 'repositories.txt'  # Replace with your file path
    cache_folder = 'cache'           # Main cache folder
    # print header
    header = f"| repo: | Latest Release:  | date:  |"
    print("-" * len(header))
    print(header)

    for url in read_repos_from_file(repo_file):
        #print(url)
        user, repo = parse_github_url(url)
        #print(f"Checking {user}/{name} ")
       
        if user and repo:
            cached_data = load_cached_data(cache_folder, user, repo)
            tag, date = get_latest_release_info(user, repo)
            if tag:
                # print it inside a terminal in tabular format
                response =f"| repo: {user}/{repo} | Latest Release: {tag} | date: {date_format(date)} |"
                print("-" * len(response))
                print(response)
                if cached_data.get('tag') != tag:
                    print(f"Update found for {user}/{repo}: {tag}")
                    print(f"{url}")
                save_cache_data(cache_folder, user, repo, {'tag': tag, 'date': date})

if __name__ == "__main__":
    main()
