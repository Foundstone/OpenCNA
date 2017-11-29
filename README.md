# OpenCNA

OpenCNA (Collection, Normalization and Analysis) tool, to collect data from endpoints (actually, we use [rastrea2r](https://github.com/aboutsecurity/rastrea2r) to do that), normalize (parse) that data and analyze it.


## Requirements

In order to make it easy to deploy, we rely on docker:
* Install and start Docker CE (https://www.docker.com/community-edition)


## Deployment

Currently, the docker images are NOT in the docker hub. You have to deploy them first:

```bash
sh build.sh
```

That will create the opencna command line tool and a set of docker images. You can see them, by running:

```bash
docker images
```


## Running

Currently, there are two commands for opencna:

* normalize: parses the data in the snapshots and create csv files as output.
    Example:
    ```bash
    opencna normalize -i data/collector/ -o data/normalizer/
    ```
    The snapshots in data/collector/ will be parsed and the result stored in data/normalizer/. **The folders in -i and -o will be loaded as volumes in docker. Make sure these folders can be volumes.**


* analyze: in this case, the functions work with piping. They read from stdin and write to stdout.
    Examples:
    * web-history:
        ```bash
        cat data/normalizer/webhistory-WIN81/20171126083616/20171126083616-WIN81-webhist-demouser1.csv | opencna analyze web-history -c URL -o naked_IP
        ```
    * random-process-name:
        ```bash
        cat data/normalizer/triage-WIN81/20171126084231-WIN81-process-list.csv | opencna analyze random-process-name -c Name -o is_random_name
        ```
    * process-uncommon-nsrl:
        ```bash
        cat data/normalizer/triage-WIN81/20171126084231-WIN81-process-list.csv | opencna analyze process-uncommon-nsrl -c Name -o is_uncommon
        ```

    In general, for analyzers, the following arguments must be passed:
    * -c: csv column name(s) to process
    * -o: csv column name(s) generated
