#!/bin/bash -l

source `dirname $0`/setup.sh

yum update -y

yum install -y emacs wget zsh tcsh vim

cd /root


