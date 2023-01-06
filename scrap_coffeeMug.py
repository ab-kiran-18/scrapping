import re
import threading

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# global array to store all data
TOTAL_SCRAPED_DATA = []


def get_coffeemug_data(page_num: int):
    """
    getting scrapped data from each page number
    """
    link = f"https://coffeemug.ai/campaigns/startups-ajax-call/year/industry/2/city/?page={page_num}"
    page = requests.get(link)

    soup = BeautifulSoup(page.content, "html.parser")

    for ele in tqdm(soup.find_all(class_="user-matches columns active")):

        company = ele.find("div", class_="company-title").text.strip()
        company_domain = ele.find(class_="comp-subtitle").text.strip()
        founding_year = ele.find(title="Founding Year").text.strip()
        no_of_employees = ele.find(title="Employees").text.strip()
        no_of_employees = re.sub("\n", "", no_of_employees)
        company_linkedIn = ele.find("a", class_="linkedin")["href"]
        description = ele.find("div", class_="content").find("div", class_="pb-10")
        if not description is None:
            description = description.text.strip()
        else:
            description = "NA"
        Poc_block = ele.find_all("div", class_="subcard-info")
        for count in range(0, len(Poc_block)):
            Poc_data = Poc_block[count].find("div", class_="header-info")
            Poc_link = Poc_data.find("div", class_="header-title").find("a")["href"]

            Poc_page = requests.get(f"https://coffeemug.ai/" + Poc_link)
            Poc_soup = BeautifulSoup(Poc_page.content, "html.parser")

            Poc_name = Poc_soup.find("div", class_="header-title").text.strip()
            Poc_details = Poc_soup.find_all("div", class_="header-subtitle")
            Poc_designation = Poc_details[0].text.strip()
            Poc_designation = re.sub(" +", " ", Poc_designation)
            Poc_description = (
                Poc_soup.find(class_="recommendation-list")
                .find("div", class_="card-body")
                .find("div", class_="content")
                .find(["p", "div"], class_="pb-10")
            )
            if not Poc_description is None:
                Poc_description = Poc_description.text
            else:
                Poc_description = "NA"
            Poc_Location = Poc_details[1].text.strip()
            Poc_linkedIn = Poc_soup.find("div", class_="flex-card-header").find(
                "a", class_="linkedin"
            )["href"]

            each_lead_data = {
                "Company": company,
                "Company Domain": company_domain,
                "Founding Year": list(founding_year.split(" "))[0],
                "No of Employees": list(no_of_employees.split(" "))[0],
                "Company LinkedIn": company_linkedIn,
                "Company Description": description,
                "Person Name": Poc_name,
                "Person Designation": Poc_designation,
                "Personal Description": Poc_description,
                "Person Location": Poc_Location,
                "Person LinkedIn": Poc_linkedIn,
            }


if __name__ == "__main__":

    # using threading for decreasing the time complexity
    threads = []
    for page_num in range(1, 25):
        thread = threading.Thread(target=get_coffeemug_data, args=(page_num,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    # converting the data into dataframe
    df = pd.DataFrame(TOTAL_SCRAPED_DATA)

    # storing the data in excel sheet
    df.to_excel("CoffeemugScrappingData.xlsx")

#     print(f"company: {company}\ncompany_domain:{company_domain}\nfounding_year: {founding_year}\n" +
#     f"no_of_employees: {no_of_employees}\ncompany_linkedIn: {company_linkedIn}\ndescription:{description}\n" +
#     f"Poc_name: {Poc_name}\nPoc_designation: {Poc_designation}\nPoc_Location: {Poc_Location}\n" +
#     f"Poc_linkedIn: {Poc_linkedIn}")

# print("*"*100)
