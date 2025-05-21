import json
import os
import requests
from bs4 import BeautifulSoup
from groq import Groq
from IPython.display import Markdown, display, update_display
import dotenv
import streamlit as st

dotenv.load_dotenv()

MODEL = "llama3-70b-8192"
groq = Groq(api_key=os.getenv("API_KEY"))

class Website:
    def __init__(self, url):
        self.url = url
        response = requests.get(url, headers=headers)
        self.body = response.content
        soup = BeautifulSoup(self.body, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"

        if soup.body:
            for irrelevant in soup.body(["script", "style", "img", "input"]):
                irrelevant.decompose()
            self.text = soup.body.get_text(separator="\n", strip=True)
        else:
            self.text = ""
        links = [link.get('href') for link in soup.find_all('a')]
        self.links = [link for link in links if link]

    def get_contents(self):
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"

def get_links_user_prompt(website):
    user_prompt = f"Here is the list of links on the website of {website.url} - "
    user_prompt += "please decide which of these are relevant web links for a database of news articles, \
                    respond with the full https URL in JSON format. \
                    Do not include Terms of Service, Privacy, Email Links, About Us, Contact Us, and links to other social media websites like Facebook and Instagram. \
                    Only include links that have a headline or a title \n"
    user_prompt += "Links (some might be relative links):\n"
    user_prompt += "\n".join(website.links)
    return user_prompt  

def get_links(url):
    website = Website(url)
    response = groq.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": link_system_prompt},
            {"role": "user", "content": get_links_user_prompt(website)}
        ],
        response_format={"type": "json_object"}
    )
    result = response.choices[0].message.content
    return json.loads(result)

def get_all_details(url):
    result = "Landing page:\n"
    result += Website(url).get_contents()
    links = get_links(url)
    print("Found links:", links)
    for link in links["links"]:
        result += f"\n\n{link['type']}\n"
        result += Website(link["url"]).get_contents()
    return result

def get_brochure_user_prompt(news_article, url):
    user_prompt = f"You are looking at a news article called: {news_article}\n"
    user_prompt += f"Here are the contents of its article and other relevant pages; use this information to build a short summary of the news article, and whether or not it is reliable and trustworthy and void of government bias in markdown.\n"
    user_prompt += get_all_details(url)
    user_prompt = user_prompt[:5_000]  # Truncate if more than 5,000 characters
    return user_prompt

def stream_brochure(company_name, url):
    stream = groq.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": get_brochure_user_prompt(company_name, url)}
          ],
        stream=True
    )

    response = ""
    placeholder = st.empty()
    for chunk in stream:
        delta = chunk.choices[0].delta.content or ""
        response += delta
        clean_response = response.replace("```", "").replace("markdown", "")
        placeholder.markdown(clean_response)

    return response

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

link_system_prompt = "You are provided with a list of links found on a webpage. \
You are able to decide which of the links would be most relevant to include in a database of news articles, \
the type of news article is determined by the main topic of discussion of the news article.\
The desired link to add is a link that contains the title at the end of it. \n"
link_system_prompt += "You should respond in JSON as in this example:"
link_system_prompt += """
{
    "links": [
        {"type": "topic1", "url": "https://full.url/goes/here/"},
        {"type": "topic2", "url": "https://full.url/goes/here/"},
        {"type": "topic3", "url": "https://full.url/goes/here/"},
        {"type": "topic4", "url": "https://full.url/goes/here/"},
    ]
}
"""
with open("system_prompt.txt", "rt") as infile:
    system_prompt = "".join(infile.readlines())
    print(system_prompt)

CNA = Website("https://www.channelnewsasia.com/")
TODAY = Website("https://www.todayonline.com/")
STRAITSTIMES = Website("https://www.straitstimes.com/")
INDEPENDENT = Website("https://theindependent.sg/")

MOTHERSHIP = Website("https://mothership.sg/")
STOMP = Website("https://stomp.straitstimes.com/")
RICE = Website("https://www.ricemedia.co/")
JOM = Website("https://www.jom.media/")