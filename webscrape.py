import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import urllib.parse

def get_package_url(package_name):
    formatted_package_name = package_name.replace(" ", "+")
    search_url = f"https://www.google.com/search?q=site:mvnrepository.com+{formatted_package_name}"
    headers = {"User-Agent": "Chrome/58.0.3029.110"}
    print("Search URL:", search_url)
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        print(f"HTTP Status Code: {response.status_code}")
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            search_results = soup.find('div', class_='egMi0 kCrYT')
            if search_results:
               url = search_results.find('a')['href'].split('?q=')[1].split('&')[0]
               print("Package URL:", url)
               return url
            else:
               print("Search results not found")
    except requests.exceptions.RequestException as e:
        print(f"Error searching for package URL: {e}")

    return None

def get_latest_version(package_name):
    url = get_package_url(package_name)
    if not url:
        return "URL not found", None

    headers = {
        "User-Agent": "Chrome/58.0.3029.110"
    }

    for _ in range(10):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                break
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            time.sleep(10)
    else:
        print("Failed to fetch data after 10 retries")
        return "Error fetching data", url

    print(f"HTTP Status Code: {response.status_code}")

    soup = BeautifulSoup(response.content, 'html.parser')
    
    latest_version_element = soup.find('a', class_='vbtn release')
    if not latest_version_element:
        latest_version_element = soup.find('a', class_='vbtn alpha')
        
    if latest_version_element:
        latest_version = latest_version_element.text.strip()
        return latest_version, url
    else:
        return "Version not found", url

def process_packages(input_file):
    # Read input packages from Excel file
    df = pd.read_excel(input_file)

    # Create an empty list to store the results
    results = []

    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        package_name = row['package_name']
        current_version = row['current_version']

        # Get the latest version and URL for the package
        latest_version, url = get_latest_version(package_name)

        # Append the results to the list
        results.append({
            "package_name": package_name,
            "current_version": current_version,
            "latest_version": latest_version,
            "URL": url
        })

    # Create a DataFrame from the results
    result_df = pd.DataFrame(results)

    # Generate the output file name based on the input file name
    # output_file = input_file.replace(".xlsx", "_output.xlsx")

    # Write the results to the output Excel file
    result_df.to_excel(input_file, index=False)

    print(f"Results saved to {input_file}")

def main():

    process_packages("opensource.xlsx")

if __name__ == "__main__":
    main()
