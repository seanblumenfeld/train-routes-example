.PHONY: usage clean build run unit_tests lint

usage:
	@echo "Available commands:"
	@echo "\tclean - stop the running containers and remove the volumes and network"
	@echo "\tbuild - build the docker image"
	@echo "\trun - run program"
	@echo "\tunit_tests - run unit tests"
	@echo "\tlint - run flake8"

clean:
	find . -type f -name '*.pyc' -exec rm -f {} ';'
	find . -type d -name '__pycache__' -exec rm -f {} ';'
	docker-compose down

build: clean
	docker-compose build

unit_tests: build
	docker-compose run train_routes_example bash -c "python -m pytest /train-routes-example/tests/test*.py"

lint:
	docker-compose run train_routes_example bash -c "flake8 /train-routes-example"

run: build
	docker-compose run train_routes_example bash -c "python /train-routes-example/bin/route.py --graph_file '$(file)'"
