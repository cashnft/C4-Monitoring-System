.PHONY: test

test:
	docker-compose run --rm test

test-cov:
	docker-compose run --rm test pytest --cov=api tests/

test-watch:
	docker-compose run --rm test pytest-watch