# Air Quality Data Pipeline

## Project Overview
Given the ongoing wildfires in Canada in the summer of 2023, it has become increasingly important for Canadians to monitor the local air quality and ensure conditions are safe outdoors.
Specifically, there has been a significant increase in the PM2.5 pollutant as a result of the fires. As a student at the University of Waterloo in Kitchener, Ontario, I wanted to deliver insights about the area's PM2.5 levels to help fellow citizens stay informed about potentially hazardous conditions.
Essential insights encompass real-time updates on pollutant levels, a comprehensive understanding of their historical trends, and reliable forecasts for the upcoming day.

The above motivates this project, where I have created a data pipeline which regularly obtains, transforms, stores, forecasts, and visualizes live air quality data to deliver valuable health information to Kitchener residents.
## Architecture

![aq-pipeline](https://github.com/aniqp/air-quality-pipeline/assets/89875233/e83e8d5f-ca07-47c3-bf5e-c193161a91d3)

1. **Workflow Orchestration**: Airflow is built from a docker-compose file on an EC2 instance through GitHub Actions. It is responsible for scheduling and executing jobs throughout the pipeline.

2. **Data Ingestion**: An Airflow DAG runs hourly to retrieve the latest PM2.5 data from the OpenAQ API in JSON format.

3. **Data Processing and Validation**: The data processing and validation tasks are executed sequentially. If the data is exactly one hour later than the most recent entry in the database, it is directly inserted. However, if the time difference exceeds one hour, an additional API call is made to backfill the data, ensuring that the latest information is retrieved, even if it was not available during the initial API call.

4. **Data Storage**: Processed data is stored in the ```kitchener_pm25``` table of a MySQL RDS instance.

5. **Forecasting**: An fbprophet model that is trained and hyperparameter tuned on data from the start of the summer (i.e., time of sudden increase in PM2.5 values) is used to predict the air quality over the next 24 hours. Forecasts are made by a separate DAG and are stored in the ```kitchener_pm25_forecasts``` table of the RDS instance.

6. **Data Visualization**: Looker Studio's MySQL connector is used to obtain the relevant data from the created tables and views.

```Today's Air Quality```, showcasing PM2.5 measurements over the last 24 hours, forecasts for the current date, and important summary statistics.
<img width="444" alt="image" src="https://github.com/aniqp/air-quality-pipeline/assets/89875233/9f1b1305-9ad6-483d-9c76-60208b899e4a">

```Historical Air Quality```, demonstrating PM2.5 measurements across historical date ranges (hourly, weekly, YTD averages)
<img width="446" alt="image" src="https://github.com/aniqp/air-quality-pipeline/assets/89875233/210d8f96-da07-4d0f-9789-683abe5e2dc0">




