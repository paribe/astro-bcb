Overview
========


# Using Airflow call API and write PostgreSQL project create by ASTRO


Welcome to Astronomer! This project was generated after you ran 'astro dev init' using the Astronomer CLI. This readme describes the contents of the project, as well as how to run Apache Airflow on your local machine.

Project Contents
================

Your Astro project contains the following files and folders:

- dags: This folder contains the Python files for your Airflow DAGs. By default, this directory includes one example DAG:
    - `example_astronauts`: This DAG shows a simple ETL pipeline example that queries the list of astronauts currently in space from the Open Notify API and prints a statement for each astronaut. The DAG uses the TaskFlow API to define tasks in Python, and dynamic task mapping to dynamically print a statement for each astronaut. For more on how this DAG works, see our [Getting started tutorial](https://www.astronomer.io/docs/learn/get-started-with-airflow).
- Dockerfile: This file contains a versioned Astro Runtime Docker image that provides a differentiated Airflow experience. If you want to execute other commands or overrides at runtime, specify them here.
- include: This folder contains any additional files that you want to include as part of your project. It is empty by default.
- packages.txt: Install OS-level packages needed for your project by adding them to this file. It is empty by default.
- requirements.txt: Install Python packages needed for your project by adding them to this file. It is empty by default.
- plugins: Add custom or community plugins for your project to this file. It is empty by default.
- airflow_settings.yaml: Use this local-only file to specify Airflow Connections, Variables, and Pools instead of entering them in the Airflow UI as you develop DAGs in this project.

Deploy Your Project Locally
===========================

1. Start Airflow on your local machine by running 'astro dev start'.

This command will spin up 4 Docker containers on your machine, each for a different Airflow component:

- Postgres: Airflow's Metadata Database
- Webserver: The Airflow component responsible for rendering the Airflow UI
- Scheduler: The Airflow component responsible for monitoring and triggering tasks
- Triggerer: The Airflow component responsible for triggering deferred tasks

2. Verify that all 4 Docker containers were created by running 'docker ps'.

Note: Running 'astro dev start' will start your project with the Airflow Webserver exposed at port 8080 and Postgres exposed at port 5432. If you already have either of those ports allocated, you can either [stop your existing Docker containers or change the port](https://www.astronomer.io/docs/astro/cli/troubleshoot-locally#ports-are-not-available-for-my-local-airflow-webserver).

3. Access the Airflow UI for your local Airflow project. To do so, go to http://localhost:8080/ and log in with 'admin' for both your Username and Password.

You should also be able to access your Postgres Database at 'localhost:5432/postgres'.

Deploy Your Project to Astronomer
=================================

If you have an Astronomer account, pushing code to a Deployment on Astronomer is simple. For deploying instructions, refer to Astronomer documentation: https://www.astronomer.io/docs/astro/deploy-code/

Contact
=======

The Astronomer CLI is maintained with love by the Astronomer team. To report a bug or suggest a change, reach out to our support.

# Error accessing PostGreSQL database via AIRFLOW

The error message you are receiving indicates that Airflow cannot resolve the hostname "host.docker.internal" to an address. This can happen for a few reasons, especially in the context of Docker. Let's explore some possible solutions:

Check the Connection in Docker If you are running Airflow in a Docker container and PostgreSQL on your host machine, the name host.docker.internal should work to connect to the host. However, this only works if:
You are using Docker on Windows or macOS. For Linux users, host.docker.internal may not be available. For Linux users, a workaround is to use the host machine's IP address or hostname. How to check the Host IP on Linux: Find your host machine's IP:

bash Copy code ip addr show docker0 Look for a line that starts with inet, which should look like inet 172.17.0.1.

Use this IP address as the host in your Airflow connection configuration.

Airflow Connection Configuration Make sure that your Airflow connection configuration is correct. Below is an example of the configuration that you should use:
Connection Id: postgres_astro Connection Type: Postgres Host: host.docker.internal (or the IP you got if you are on Linux) Database: astro Login: postgres Password: (your PostgreSQL password) Port: 5432 Extra: (can be left empty) 3. Verify the Connection in Airflow After making the changes, test the connection in Airflow:

Go to the Connections section in Airflow. Select the postgres_astro connection. Click Test to verify that the connection is successful. 4. Verify the Airflow and PostgreSQL Provider Version Make sure that you are using the correct version of Airflow and the PostgreSQL provider. If you are still using PostgresOperator, consider upgrading to SQLExecuteQueryOperator, as indicated in the deprecation warning message.

Direct Connection If you are still experiencing issues, as a temporary workaround, you can try running Airflow outside of Docker, directly on your machine, to see if the connection works normally. This way, you can confirm whether the issue is related to Docker or your Airflow configuration.

Summary of Possible Actions Try using the host machine's IP instead of host.docker.internal if you are on Linux. Check that the credentials and database name are correct. Test the connection in the Airflow interface. Consider upgrading to SQLExecuteQueryOperator and the required dependencies. If you continue to experience issues, please provide any other error messages that may appear!