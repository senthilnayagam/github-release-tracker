import requests
import json
import os
from urllib.parse import urlparse, parse_qs

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

def main():
    repo_file = 'repositories.txt'  # Replace with your file path
    cache_folder = 'cache'           # Main cache folder

    for url in read_repos_from_file(repo_file):
        user, name = parse_github_url(url)
        if user and name:
            cached_data = load_cached_data(cache_folder, user, name)
            tag, date = get_latest_release_info(user, name)
            if tag:
                print(f"{user}/{name} Latest Release: {tag} at {date}")
                if cached_data.get('tag') != tag:
                    print(f"Update found for {user}/{name}: {tag}")
                save_cache_data(cache_folder, user, name, {'tag': tag, 'date': date})

if __name__ == "__main__":
    main()