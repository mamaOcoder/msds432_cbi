# Chicago Business Intelligence for Strategic Planning
MSDS 432 Final Project Phase 4
Leslie Stovall 

This repo contains the code for implementing the back-end and front-end design for the Chicago Business Intelligence for Strategic Planning project. This README provides design information for both the back-end and front-end. The back-end design is largley unchanged from phase 3.


## Project Design
### Microservices:
This project uses a microservices approach. A microservice is defined as a tiny and independent software process that runs on its own deployment schedule and can be updated independently. Two rules: 
- Microservices within an application should be loosely-coupled, meaning that connections between services are minimal and they don't share information unless absolutely neccessary. 
- Code within a microservice should be highly cohesive, meaning all code belongs together and contributes to solve the problem that is the service's ares of responsibility. 

Using these principles, I organized my microservice application in the following way: 

1. Go program to collect, clean and write data from the City of Chicago Data portal to a data lake. Within this program, I created a microservice for each table within the data lake. This ensures that is a change to one of the tables, whether it be in the original City of Chicago Data Portal or a needed processing step, will not affect the processing of the other tables. For additional information on the structure of the Go applications, see the Program Documentation subsection.

2. PostgreSQL is used as the database engine for my data lake microservice. 

3. Python code to build forecast model for traffic patterns utilizing the taxi trips for the different zip codes. The visualizations are presented in a Streamlit application.

### Front-end:
The front-end application provides visualizations for forecasting traffic patterns for the different Chicago zip codes using the taxi trip dataset. For my implementation, I decided to use [Prophet](https://facebook.github.io/prophet/docs/quick_start.html#python-api) for forecasting the time series data and [Streamlit](https://streamlit.io) for the web application. Streamlit is Python library that makes it easy to create interactive web applications. It easily integrates with Python visualization libraries, such as Plotly, making development and deployment much simpler.

### Program Documentation
#### Back-end Go Packages/Scripts
- main: The main package consists of the main.go file that runs the program. It starts by building the Community Area and Zip Code lookups that are used throughout the program and then ensures that the PostgreSQL database is created. Finally, it concurrently calls the build methods for the remaining microservices.

- common: The common package contains code that used across the program.
  - methods.go: Contains functions that can be used across the program.
  - structs.go: Contains struct definitions that are used across the program.
  - pg_methods.go: Contains commands for connecting to PostgreSQL database that are used across microservices.
  
- cazip: The cazip package contains code for building the community area and zip code lookups.
  - ca_zip_struct.go: Contains struct definitions for the package.
  - get_lookup.go: Contains code to build the lookups.
    - [caLookup](https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Boundaries-Community-Areas-current-/cauq-8yn6)
    - [zipLookup](https://data.cityofchicago.org/Facilities-Geographic-Boundaries/Chicago-Zip-Code-and-Neighborhood-Map/mapn-ahfc#Layer0)

- transportation: The transportation package contains the code to collect, clean and write data for the taxi trips.
  - taxi_structs.go: Contains struct definitions for the transportation microservice.
  - build_taxi_pipeline.go: Contains the code for building the transportation microservice. URLs are built based on the base URLs for the [taxi trip data](https://data.cityofchicago.org/Transportation/Taxi-Trips-2024-/ajtu-isnz/about_data) and the [tnp trip data](https://data.cityofchicago.org/Transportation/Transportation-Network-Providers-Trips-2023-/n26f-ihde/about_data) and the number of records to pull. The program concurrently calls APIs for the URLs and generates a data stream to clean and write the data to PSQL data table.
  - get_taxi_data.go: Contains the function to query the APIs.
  - clean_taxi_data.go: Contains the function to clean the stream of taxi data.
  - pg_taxi.go: Contains commands for creating and writing to taxi_trips table.

- building_permits: The building_permits package contains the code to collect, clean and write data for the [building permits](https://www.chicago.gov/city/en/depts/bldgs/dataset/building_permits.html) issued by the Department of Buildings in the City of Chicago.
  - permit_structs.go: Contains struct definitions for the building permits microservice.
  - build_permits_pipeline.go: Contains the code for building the building permits microservice. The code concurrently calls the APIs for the URLs and generates a data stream to clean and write the data to its PSQL data table.
  - get_permits_data.go: Contains the function to query the APIs.
  - clean_permit_data.go: Contains the function to clean the stream of building permit data.
  - pg_permits.go: Contains commands for creating and writing to building_permits table.

- covid: The covid package contains the code to collect, clean and write data for the [COVID-19](https://data.cityofchicago.org/Health-Human-Services/COVID-19-Cases-Tests-and-Deaths-by-ZIP-Code/yhhz-zm2v/about_data) data.
  - covid_structs.go: Contains struct definitions for the covid19 microservice.
  - build_covid_pipeline.go: Contains the code for building the COVID-19 microservice. The code concurrently calls the APIs for the URLs and generates a data stream to clean and write the data to its PSQL data table.
  - get_covid_data.go: Contains the function to query the APIs.
  - clean_covid_data.go: Contains the function to clean the stream of covid data. When testing, we found that some of the coordinates fell outside the lookups. Therefore we needed to perform Google Geocoder reverse lookups. In order to limit the number of calls, another lookup is created based on the results of reverse lookup and saved to a zip_ca_lookup.jl file.
  - pg_covid.go: Contains commands for creating and writing to covid19_cases table.
  
- ccvi: The ccvi package contains the code to collect, clean and write data for the [CCVI](https://data.cityofchicago.org/Health-Human-Services/Chicago-COVID-19-Community-Vulnerability-Index-CCV/xhc6-88s9/about_data) data.
  - ccvi_structs.go: Contains struct definitions for the ccvi microservice.
  - build_ccvi_pipeline.go: Contains the code for building the CCVI microservice. Note that this dataset is historic and only contains 135 records (one for each community area and zip code), therefore only a single URL/API call is needed (no concurrency). The code converts the response into a stream of data to concurrently clean and write the data to its PSQL data table.
  - get_ccvi_data.go: Contains the function to query the API.
  - clean_ccvi_data.go: Contains the function to clean the stream of ccvi data. This dataset already contains a single entry for each community area and zip code, therefore there is no need to do lookups.
  - pg_ccvi.go: Contains commands for creating and writing to ccvi table.
  
-unemployment: The unemployment package contains the code to collect, clean and write data for the [unemployment and poverty level](https://data.cityofchicago.org/Health-Human-Services/Public-Health-Statistics-Selected-public-health-in/iqnk-2tcu/about_data) data.
  - unemployment_structs.go: Contains struct definitions for the unemployment microservice.
  - build_unemployment_pipeline.go: Contains the code for building the unemployment microservice. Note that this dataset is historic and only contains 77 records (one for each community area), therefore only a single URL/API call is needed (no concurrency). The code converts the response into a stream of data to concurrently clean and write the data to its PSQL data table.
  - get_unemployment_data.go: Contains the function to query the API.
  - clean_unemployment_data.go: Contains the function to clean the stream of unemployment data. This dataset does not contain any coordinates, so the community area is solely used to determine the zip code. This means that a list of zip codes is often associated with a community area. 
  - pg_unemployment.go: Contains commands for creating and writing to unemployment table.

- Dockerfile: This file contains the information for building the Go microservices.
  
#### Front-end Scripts
- eda.py: This Python script was written to perform some basic exploratory data analysis of the taxi trip dataset. It is not used for this frontend visualizations, but was beneficial for understanding the data trends and could be easily added.  

- frontend.py: This contains the code for building the frontend. It pulls the data from the database, builds the forecast model and visualizations, and builds the streamlit app.  

- Dockerfile: This file contains the information for building the microservice.

## Setup/Run
### Create GCP Project and PostgreSQL database
1. Install the Google Cloud CLI on your local machine.
2. Create a new project on your Google Cloud console.
3. Enable Geocoder API for project and update Backend/Dockerfile with API Key.
4. From the command/terminal window, execute the command:  
    *gcloud init*
5. Create database instance of PostgreSQL on GCP. Execute the command:  
    *gcloud sql instances create cbipostgres --database-version=POSTGRES_14 --cpu=2 --memory=7680MB --region=us-central*
6. Create SQL users on the database instance. Execute the command:  
    *gcloud sql users set-password postgres --instance=cbipostgres --password=root*
7. Create chicago_business_intelligence database. Execute the command:  
    *gcloud sql databases create chicago_business_intelligence --instance=cbipostgres*
8. *Note: this approach did not work. For now, just removing postgis dependencies.* Add the postgis extension. Execute the commands:  
    *gcloud sql connect cbipostgres --user=postgres --quiet*  
    *CREATE EXTENSION IF NOT EXISTS postgis;*  
9. Add the PostgreSQL instance connection name into Go code for host name.  
10. Update cloudbuild.yaml file with project name.


### Continuous Deployment
1. Create GitHub repository for CBI source code.
2. Enable Cloud Build API for project.
3. Create a trigger and connect GitHub repository.

### Go-microservice and Pg-admin
1. Enable Cloud Run API for project.
2. Enable IAM permissions. *Note this will likely take a lot of additional work and trouble-shooting*

## View Results
1. Push source code to GitHub repo. This will trigger a new build to run.
2. Go to Cloud Run and verify services are up and running.
3. Click on each service to view log and get URL links.
