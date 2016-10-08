.PHONY: usage clean build start unit_tests lint

usage:
	@echo "Available commands:"
	@echo "\tclean - stop the running containers and remove the volumes and network"
	@echo "\tbuild - build the docker image"
	@echo "\tstart - start program"
	@echo "\tunit_tests - run unit tests"
	@echo "\tlint - run flake8"

clean:
	find -type f -name '*.pyc' -exec rm -f {} ';'
	docker-compose down

build: clean
	docker-compose build

start: build
	docker-compose up -d train_routes_example

unit_tests: build
	docker-compose run train_routes_example bash -c "python -m pytest /train-routes-example/tests/test*.py"

lint:
	docker-compose run train_routes_example bash -c "flake8 /train-routes-example"
