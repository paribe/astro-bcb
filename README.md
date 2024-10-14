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

# Erro ao acessar Bando de Dados PostGreSQL pelo AIRFLOW
A mensagem de erro que você está recebendo indica que o Airflow não consegue resolver o nome do host "host.docker.internal" para um endereço. Isso pode acontecer por algumas razões, especialmente no contexto do Docker. Vamos explorar algumas soluções possíveis:

1. Verifique a Conexão no Docker
Se você estiver executando o Airflow em um container Docker e o PostgreSQL em sua máquina host, o nome host.docker.internal deve funcionar para conectar-se ao host. Contudo, isso só funciona se:

Você estiver usando o Docker no Windows ou macOS. Para usuários do Linux, host.docker.internal pode não estar disponível. Para usuários do Linux, uma solução é usar o endereço IP da máquina host ou o nome do host.
Como verificar o IP do Host no Linux:
Encontre o IP da sua máquina host:

bash
Copiar código
ip addr show docker0
Procure por uma linha que começa com inet, que deve se parecer com inet 172.17.0.1.

Use esse endereço IP como o host na sua configuração de conexão no Airflow.

2. Configuração da Conexão no Airflow
Certifique-se de que a configuração da conexão no Airflow esteja correta. Abaixo está um exemplo da configuração que deve ser usada:

Connection Id: postgres_astro
Connection Type: Postgres
Host: host.docker.internal (ou o IP que você obteve, se estiver no Linux)
Database: astro
Login: postgres
Password: (sua senha do PostgreSQL)
Port: 5432
Extra: (pode ser deixado vazio)
3. Verificar a Conexão no Airflow
Depois de fazer as alterações, teste a conexão no Airflow:

Vá para a seção Connections no Airflow.
Selecione a conexão postgres_astro.
Clique em Test para verificar se a conexão é bem-sucedida.
4. Verificar a Versão do Airflow e do Provider do PostgreSQL
Certifique-se de que você está utilizando a versão correta do Airflow e do provedor PostgreSQL. Se você ainda estiver usando o PostgresOperator, considere atualizar para o SQLExecuteQueryOperator, conforme indicado na mensagem de aviso sobre a depreciação.

5. Conexão Direta
Se você ainda tiver problemas, como solução temporária, você pode tentar rodar o Airflow fora do Docker, diretamente na sua máquina, para verificar se a conexão funciona normalmente. Assim, você pode confirmar se o problema está relacionado ao Docker ou à configuração do Airflow.

Resumo das Possíveis Ações
Tente usar o IP da máquina host em vez de host.docker.internal se você estiver no Linux.
Verifique se as credenciais e o nome do banco de dados estão corretos.
Teste a conexão na interface do Airflow.
Considere atualizar para o SQLExecuteQueryOperator e as dependências necessárias.
Se você continuar a ter problemas, por favor, forneça qualquer outra mensagem de erro que possa aparecer!