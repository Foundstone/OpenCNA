echo "Creating the docker images..."

echo "Creating the normalizer"
docker build -t opencna/normalizer normalizer/

echo "Creating the analyzers"
docker build -t opencna/analyzer/process-uncommon-nsrl analyzer/process-uncommon-nsrl/
docker build -t opencna/analyzer/random-process-name analyzer/random-process-name/
docker build -t opencna/analyzer/web-history analyzer/web-history/

pip install .

