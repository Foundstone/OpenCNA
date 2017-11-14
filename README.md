# OPENCNA

This is a VERY FIRST trial to make the OPENCNA (Collection, Normalization and Analysis) happen. It contains just an example of a way how we can run an analytic with a csv files interface, and 'really easy' to deploy.


## Requeriments

In order to make it easy to deploy, we rely on docker:
* Install and start Docker CE (https://www.docker.com/community-edition)


## TODOs (next steps)

These are the inputs we would like to process in a near future:
* Random paths -> autorun
* Webhistory
* MFT

We would like to have a way of visualizing the results with:
* Temporal lines?
* How to represent entropy, uncommon things?

We must perform Collection + Normalization. In that sense, we need to convert rastrea2r output to csv


## Deployment

The deployment is done through docker images. To create the first one, run:

```bash
build -t random-folder random-folder/
```

That will create a docker image called "random-folder". You can see it listed, by running:

```bash
docker images
```


## Running

The docker instances created are expecting a csv file being passed through stdin and the output is stdout. Therefore, we can use pipes '|' to process files. For example, you may add a column of 'random path' to a csv file listing processes:

```bash
cat random-folder/resources/example.csv | docker run --rm -i random-paths -c fpath -o "is random path" | cat
```

For that example, we are running the image random-paths 'interactively' (-i argument). After running it, we remove it (--rm argument). And we pass the following arguments to the analytic in the docker:
* -c: csv column name to process
* -o: csv column name generated

You can run the docker with the -h option to get usage help:

```bash
docker run --rm -i random-paths -h
```