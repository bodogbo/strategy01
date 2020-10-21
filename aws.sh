#!/bin/bash

GOOS=linux GOARCH=amd64 go build 

#ssh -i ~/dev/aws/walkaws.pem ubuntu@ec2-34-222-69-66.us-west-2.compute.amazonaws.com
scp -i ~/dev/aws/walkaws.pem strategy01 ubuntu@ec2-34-222-69-66.us-west-2.compute.amazonaws.com:/home/ubuntu/uniperpgrid
scp -i ~/dev/aws/walkaws.pem config.json ubuntu@ec2-34-222-69-66.us-west-2.compute.amazonaws.com:/home/ubuntu/uniperpgrid
scp -i ~/dev/aws/walkaws.pem  uniperp-grid.csv ubuntu@ec2-34-222-69-66.us-west-2.compute.amazonaws.com:/home/ubuntu/uniperpgrid


