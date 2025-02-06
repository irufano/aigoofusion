# Develop as Contributor
## Build the container
```sh
docker-compose build
```

## Run the container
```sh
docker-compose up -d aigoo-fusion
```

## Stop the container
```sh
docker-compose stop aigoo-fusion
```

## Access the container shell
```sh
docker exec -it aigoo_fusion bash
```

## Run test
```sh
python aigoo_fusion/test/test_chat.py 
python aigoo_fusion/test/test_flow.py 
```
or
```sh
python aigoo_fusion.test.test_chat.py 
python aigoo_fusion.test.test_flow.py 
```