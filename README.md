# Air Quality Data Pipeline

## Project Overview
Given the ongoing wildfires in Canada in the summer of 2023, it has become increasingly important for Canadians to monitor the local air quality and ensure conditions are safe outdoors.
Specifically, there has been a significant increase in the PM2.5 pollutant as a result of the fires. As a student at the University of Waterloo in Kitchener, Ontario, I wanted to deliver insights about the area's PM2.5 levels to help fellow citizens stay informed about potentially hazardous conditions.
Essential insights include real-time updates on pollutant levels,  an understanding of their historical trends, and reliable forecasts for the upcoming day.

The above motivates this project, where I have created a data pipeline which regularly obtains, transforms, stores, forecasts, and visualizes live air quality data to deliver valuable health information to Kitchener residents.
## Architecture

![aq-pipeline](https://github.com/aniqp/air-quality-pipeline/assets/89875233/e83e8d5f-ca07-47c3-bf5e-c193161a91d3)

1. **Workflow Orchestration**: Airflow is built from a docker-compose file on an EC2 instance through GitHub Actions. It is responsible for scheduling and executing jobs throughout the pipeline.

2. **Data Ingestion**: An Airflow DAG runs hourly to retrieve the latest PM2.5 data from the OpenAQ API in JSON format.

3. **Data Processing and Validation**: The data processing and validation tasks are executed sequentially. If the data is exactly one hour later than the most recent entry in the database, it is directly inserted. However, if the time difference exceeds one hour, an additional API call is made to backfill the data, ensuring that the latest information is retrieved, even if it was not available during the initial API call.

4. **Data Storage**: Processed data is stored in the ```kitchener_pm25``` table of a MySQL RDS instance.

5. **Forecasting**: An fbprophet model that is trained and hyperparameter tuned on data from the start of the summer (i.e., time of sudden increase in PM2.5 values) is used to predict the air quality over the next 24 hours. Forecasts are made by a separate DAG and are stored in the ```kitchener_pm25_forecasts``` table of the RDS instance.

6. **Data Visualization**: Looker Studio's MySQL connector is used to obtain the relevant data from the created tables and views.
   
     *Today's Air Quality*, showcasing PM2.5 measurements over the last 24 hours, forecasts for the current date, and important summary statistics.
  
  <img width="888" alt="image" src="https://github.com/aniqp/air-quality-pipeline/assets/89875233/9f1b1305-9ad6-483d-9c76-60208b899e4a">
  
  *Historical Air Quality*, demonstrating PM2.5 measurements across historical date ranges (hourly, weekly, YTD averages).
  
  <img width="888" alt="image" src="https://github.com/aniqp/air-quality-pipeline/assets/89875233/274e941b-228d-4d62-bbb5-410266820226">

## Forecasting Model Considerations

I chose to use the fbprophet forecasting model over other traditional methods like ARIMA (AutoRegressive Integrated Moving Average) and SARIMA (Seasonal AutoRegressive Integrated Moving Average) due to its simplicity, flexibility, and ability to handle seasonal and non-linear data patterns.

First, fbprophet incorporates seasonality and holidays as additive components, making it well-suited for capturing periodic trends in air quality data, such as daily and weekly variations. Second, it automatically detects changepoints in the data, allowing it to adapt to sudden changes in pollutant levels, which is crucial during wildfire events that can significantly impact air quality in a short period.

Another key advantage of fbprophet is its ease of implementation and interpretation. It provides intuitive diagnostics and visualizations that help in understanding model performance and identifying potential areas for improvement. This is particularly valuable when communicating forecasting results to stakeholders who may not have a strong background in time series analysis.

Lastly, one of the challenges in time series forecasting is dealing with missing data points, which can occur due to various reasons such as sensor failures, data collection gaps, or other issues. Traditional forecasting methods like SARIMA/ARIMA usually require imputing or interpolating missing values manually, which can introduce inaccuracies and uncertainty in the forecasting process. In contrast, fbprophet is designed to handle missing data gracefully. It automatically accounts for missing data points during the modeling process by imputating them with estimations following the identified trend/seasonality, allowing it to provide more accurate forecasts. By incorporating missing data as a part of the modeling process, fbprophet can better capture the underlying patterns and trends in the time series, leading to more reliable predictions.

Overall, the combination of fbprophet's built-in seasonality handling. and user-friendly features made it a suitable choice for accurate and interpretable air quality forecasting, aligning well with the project's objective of delivering reliable insights to Kitchener residents.

## Future Project Goals and Next Steps
1. Collecting data for more cities/types of pollutants and visualizing them
2. Exploring real-time data streaming tools such as Kafka, which would help with availability and scalability of data retrieval.
