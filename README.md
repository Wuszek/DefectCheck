# defectCheck

### This is tool for specific project use. You might be able to convert it and use it on your own purpose.

It is designed to prepare list of closed defects, connected to automatic tests. This tool 
should help track defects, that should be detached from tests code, to keep it clean.

## Requirements 

Install requirements with:
```bash
python3 -m pip install -r requirements.txt
```

## Settings
Edit line 19 to set up choosen jira. It should end with `/browse/`, e.g.:
```bash
WEBSITE = "jira.atlassian.com/browse/"
```


## Test run 
I prepared fake `test.xlsx` file filled with desired defect information, and made script work with public Atlassian JIRA. To test script,
just clone repo and run:
```bash 
python3 main.py -i test.xlsx
```

## Docker test run 
I prepared Dockerfile to build image and run script inside prepared container. 

Download Dockerfile and run below commands (in the same dir, as Dockerfile) to 
build image and run it. Then use script as described below. 

Disclaimer: For now, there is no option for authentication, if your JIRA instance needs one
before scraping. Might be available in the future.

```bash 
docker build -t defectcheck .
docker run -it defectcheck
cd DefectCheck 
python3 main.py -i test.xlsx
```

## How does it work?
### Input:
As input, we provide Excel file with results of automatic tests. Each row contains 
of test name, result, defect name connected to specific test etc. 

`loadExcel` function is dropping required number of rows, and is taking only values from 
one specific column (defects names). Empty values and duplicates are removed. We get list of defects, 
composed of defect number and company jira url. 

### Defect check 
Having list of defects attached to automatic tests results, `checkClosed` function uses
Selenium to open each link and check if `Status` value is `Closed`. Also, it is checking if 
it is a `Bug`, `Task` or other type and it is saving `Name`. Result is being written
in terminal in form of:
```python
i/full      ERROR:  {type_d} https://{defect_link} is {defect_status}
i+1/full    INFO:   {type_d} https://{defect_link} is CLOSED! TITLE: {title} 
```
Also, function return list of closed defects with type, name and title.

### Generate .txt file raport
With given sorted list, function is saving it to .txt file raport. 

## How to use 
```python
usage: python3 main.py [-h -s] -i <file_path>

Description

required arguments:
  -i <path>  Provide path to excel file generated from website.com

helpful arguments:
  -s         Login to portal to store credentials
  -h         show this help message and exit

© 2022, wiktor.kobiela
```

### Setup 
Run `python3 main.py -s` to open your company `WEBSITE`. Now you have 30s to log in if required to scrap.

### Run 
Run `python3 main -i excel.xlsx` to check Excel file. Script will use user cookies, so it is 
required to run setup and login only once.