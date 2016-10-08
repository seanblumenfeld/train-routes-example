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
	docker-compose up -d thoughtworks_example

unit_tests: build
	docker-compose run thoughtworks_example bash -c "python -m pytest /thoughtworks-example/tests/unit_tests/test*.py"

lint:
	docker-compose run thoughtworks_example bash -c "flake8 /thoughtworks-example"
