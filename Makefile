CURRENTDIR := ${CURDIR}
LAMBDA_DOCKER_IMAGE := 21buttons/lambda-progres-cloudwatch:$(or $(BRANCH_NAME), latest)

# ############
# Global tasks
# ############

init: symlinks-pre-commit-hooks build-docker-image

symlinks-pre-commit-hooks:
	rm -f .git/hooks/pre-commit
	mkdir -p config/git/hooks
	curl -o config/git/hooks/pre-commit.sh https://raw.githubusercontent.com/21Buttons/backend-pre-commit/master/pre-commit.sh
	chmod +x config/git/hooks/pre-commit.sh
	ln -s ../../config/git/hooks/pre-commit.sh .git/hooks/pre-commit

clean:
	rm -rf build function.zip app/__pycache__

build: clean
	mkdir -p build
	cp -r /tmp/app/build/. build
	cp -r app/. build

artifact: build
	cd build; zip -r9 ../function.zip .; rm -rf ../build

# ############
# Flake 8
# ############

flake8:
	docker run --rm --volume $(CURRENTDIR):/app 21buttons/flake8 $(or $(files), /app)

# ############
# Docker
# ############

clean-docker-image:
	-docker rmi $(LAMBDA_DOCKER_IMAGE)

build-docker-image: clean-docker-image
	docker build --force-rm --no-cache -t $(LAMBDA_DOCKER_IMAGE) .

run-docker-image:
	docker run --rm -v $(CURRENTDIR):/var/task $(LAMBDA_DOCKER_IMAGE) make build

build-artifact: build-docker-image
	docker run --rm -v $(CURRENTDIR):/var/task $(LAMBDA_DOCKER_IMAGE)

# ############
# CI
# ############

ci-build: build-artifact

ci-static-code-analysis: flake8

ci-tests:
	echo 'No tests for lambda-postgres-cloudwatch :('
