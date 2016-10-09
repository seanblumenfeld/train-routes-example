#train-routes-example

##Requirements
Docker and Docker Compose are required to run this application. Installation guides can be found here:
* https://docs.docker.com/engine/installation/
* https://docs.docker.com/compose/install/

##Usage
This application uses make as its interface.
* To run the application do `make start`
* To run all tests do `make tests`
* To tear down the application do `make clean`
* To run the linter do `make lint`
* To run build a graph from a file input do:
    * Move input file to data directory of the project `./data/{filename}`
    * Then do `make run file={filename}`
    * There is an example file in the repository which will work out of the box. To try it do:
    ```
        make run file=graph_file_input_example.txt
    ```
