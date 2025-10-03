import os
import requests


def download_file(url, download_dir):
    """
    Downloads a file from a URL into a specified directory.

    Args:
        url: The URL of the file to download.
        download_dir: The directory to save the file in.
    """
    # Ensure the download directory exists
    os.makedirs(download_dir, exist_ok=True)

    file_name = os.path.basename(url)
    file_path = os.path.join(download_dir, file_name)

    print(f"\n[+] Downloading: {file_name}")
    print(f"    From: {url}")

    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"    [✔] Successfully saved to: {file_path}")

    except requests.exceptions.RequestException as e:
        print(f"    [✘] Error downloading {file_name}: {e}")
