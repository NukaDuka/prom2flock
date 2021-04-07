# TODO: move to CI/CD tool like Jenkins
set -e 

if [[ "$( echo $PWD | rev | cut -f1 -d/ | rev)" != 'test' ]];
then
    cd ./test || exit 0
fi;

cd ..;
docker build -t prom2flock:test .;

cd ./test;

docker stack rm prom2flock-test;

docker stack deploy -c docker-stack.yaml prom2flock-test;

set +e