# -*- coding: utf-8 -*-
################################################################################
# Copyright (c) 2017 McAfee Inc. - All Rights Reserved.
################################################################################

__author__ = "Matias Marenchino"

import os
import sys
import argparse
import subprocess

import docker


_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


def _parse_arguments():
    parser = argparse.ArgumentParser(description=("openCNA tool to Collect "
                                                  "endpoints data, Normalize "
                                                  "and Analyze it, based on "
                                                  "txt and csv files"),
                                     add_help=False)
    options = parser.add_argument_group("Optional arguments")
    options.add_argument("--help", "-h",
                         help="Show this help message and exit",
                         action="help")
    options.add_argument("--version",
                         help="Display seekersdk version",
                         action="version")
    actions = parser.add_subparsers(help="Available actions",
                                    dest="action")
    normalize_parser = actions.add_parser("normalize", help=("Parse the "
                                                             "rastrea2r endpoint snapshot "
                                                             "to csv format"))
    normalize_parser.add_argument("-i", "--input_folder", required=True,
                                  help=("Directory containing the rastrea2r"
                                        "zip files. Will be loaded as a "
                                        "docker volume."))
    normalize_parser.add_argument("-o", "--output_folder", required=True,
                                  help=("Directory to store parsed data."
                                        "Will be loaded as a docker volume."))
    analyzer_parser = actions.add_parser("analyze",
                                         help="Process a normalized file")
    sub_actions = analyzer_parser.add_subparsers(help="Available actions",
                                                 dest="subaction")
    for analyzer in _get_dockers_analyzer():
        analyzer_parser = sub_actions.add_parser(analyzer,
                                                 help=("Compute analytics for " +
                                                       analyzer))
    return parser


def _get_dockers_analyzer(prefix="opencna/analyzer/"):
    res = []
    docker_client = docker.from_env()
    for image in docker_client.images.list():
        for tag in image.tags:
            if tag.startswith(prefix):
                res.append(tag[len(prefix):].split(":")[0])
    return res


def _find_docker_image(docker_client, docker_image_tag):
    for image in docker_client.images.list():
        for tag in image.tags:
            if tag.startswith(docker_image_tag):
                return image
    print "There is no docker image tagged as", docker_image_tag
    return None


def _run_docker_image(docker_client, image, subcommand_args, input_dir=None,
                      output_dir=None):
    volumes = {}
    if input_dir:
        volumes[input_dir] = {'bind': '/shared/input', 'mode': 'rw'}
    if output_dir:
        volumes[output_dir] = {'bind': '/shared/output', 'mode': 'rw'}
    print docker_client.containers.run(image, command=subcommand_args,
                                       remove=True, volumes=volumes,
                                       stderr=True, stdout=True)


def normalize(args, subcommand_args):
    """Run the docker that normalizes the snapshot(s)"""
    docker_client = docker.from_env()
    image = _find_docker_image(docker_client, "opencna/normalizer")
    if not os.path.isdir(args.input_folder):
        print args.input_folder, "should be a valid directory"
        sys.exit(1)
    if not os.path.isdir(args.output_folder):
        print args.output_folder, "should be a valid directory"
        sys.exit(1)
    input_dir = os.path.abspath(args.input_folder)
    output_dir = os.path.abspath(args.output_folder)
    if image:
        _run_docker_image(docker_client, image,
                          subcommand_args, input_dir, output_dir)



def analyze_command(subaction, subcommand_args):
    """Run the specific docker that analyzes the data"""
    docker_client = docker.from_env()
    image = _find_docker_image(docker_client, "opencna/analyzer/" + subaction)
    if image:
        #docker-py does not implement a mechanism to pass the stdin message
        # _run_docker_image(docker_client, image, subcommand_args)
        bash_command = "docker run --rm -i opencna/analyzer/" + subaction + \
                      " " + subcommand_args
        process = subprocess.Popen(bash_command.split(), stdin=sys.stdin)
        # stdout=subprocess.PIPE)
        process.communicate()


def main():
    """Entrypoint"""
    parser = _parse_arguments()
    args, subcommand_args = parser.parse_known_args()
    subcommand_args = " ".join(subcommand_args)
    action = args.action

    if action == "normalize":
        return normalize(args, subcommand_args)
    elif action == "analyze":
        subaction = args.subaction
        return analyze_command(subaction, subcommand_args)
    else:
        print "Action '{}' is not implemented. Aborting.".format(action)


if __name__ == "__main__":
    main()
