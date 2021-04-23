import requests
from pprint import pprint
from bs4 import BeautifulSoup
import pandas as pd
import time
import argparse

def getmetadata(accession):
    URL = 'https://www.rcsb.org/structure/'+accession
    
    start_time = time.time()
    page = requests.get(URL)
    print("Page fetching Time -> ",(time.time() - start_time))

    time_ = time.time()
    soup = BeautifulSoup(page.content, 'html.parser')
    print("BS Parsing Time -> ",(time.time() - time_))

    structure_title = soup.find(id='structureTitle').text.strip()
    # print(structure_title)

    deposited_released_date = soup.find(id='header_deposited-released-dates')
    # print(deposited_released_date.text.strip())
    deposited_released = deposited_released_date.text.strip().split(":")
    deposited_date = deposited_released[1].split("\xa0")[1].strip()
    released_date = deposited_released[2].split("\xa0")[1]

    # deposited_date = deposited_released[1].split("&nbsp")[1].strip()
    # released_date = deposited_released[2].split("&nbsp")[1]
    # print(deposited_date,released_date)
    emData_Map = soup.find(id="header_emdb")
    a_emData = emData_Map.find('a')
    emData_id = a_emData.text.strip()
    emData_link = a_emData['href']
    # print(a_emData_id)

    results = soup.find(id='primarycitation')
    paper_name = results.find('h4').text.strip()
    pubmedDOI = results.find('li', id="pubmedDOI")
    if pubmedDOI:
        a_paper_link = pubmedDOI.find('a')
        a_paper_link = a_paper_link['href']
        
    else:
        a_paper_link = "Not published yet"
    
    # print(paper_name)
    # print(a_paper_link)
    
    # print(a_paper_link['href'])

    # abstractText = results.find(id='abstractFull')
    # abstractText = abstractText.find('p')
    # print(abstractText.text.strip())

    return (structure_title,deposited_date,released_date,emData_id, emData_link, paper_name,a_paper_link)


def main():

    parser = argparse.ArgumentParser(description='PDB Structure Metadata Scrapper.')

    parser.add_argument('--input','-i',action='store', required=True)
    parser.add_argument('--output','-o', action='store',required=True)

    args = parser.parse_args()

    input_file = args.input
    output_file = args.output

    
    accession_list = []
    with open(input_file,"r") as fl:

        accession = fl.read()
        accession_list = accession.split(",")

    structure_titles = []
    deposited_dates = []
    released_dates = []
    emData_ids = []
    emData_links = []
    paper_names = []
    paper_links = []

    for idx,accession in enumerate(accession_list):
        print()
        print("Now working with -> ",accession, "Serial No. ->", (idx+1))
        (structure_title,deposited_date,released_date,emData_id, emData_link, paper_name,a_paper_link) = getmetadata(accession)
        print(structure_title,deposited_date,released_date,emData_id, emData_link, paper_name,a_paper_link)

        structure_titles.append(structure_title)
        deposited_dates.append(deposited_date)
        released_dates.append(released_date)
        emData_ids.append(emData_id)
        emData_links.append(emData_link)
        paper_names.append(paper_name)
        paper_links.append(a_paper_link)
    
    accession_till_now = accession_list
    columns = ["PDB Entry","Structure Title","Paper DOI","Paper Name","EMDB ID","EMDB Link","Deposited Date","Released Date"]
    df = pd.DataFrame(columns=columns)
    df["PDB Entry"]  = accession_till_now
    df["Structure Title"] = structure_titles
    df["Paper DOI"] = paper_links
    df["Paper Name"] = paper_names
    df["EMDB ID"] = emData_ids
    df["EMDB Link"] = emData_links
    df["Released Date"] = released_dates
    df["Deposited Date"] = deposited_dates
    
    df.to_excel(output_file+".xlsx",index=False)

if __name__ == "__main__":
    main()