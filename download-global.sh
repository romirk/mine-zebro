#!/bin/bash


#specify branch
if [[ $# -lt 1 ]]
then
	BRANCH='global'
else
	BRANCH=$1
fi

cd /home/pi

#download latest version
wget --tries=2 https://github.com/The-Redstar/mine-zebro/archive/$BRANCH.zip
if [[ -f "$BRANCH.zip"]]
then
	unzip "$BRANCH.zip"
	rm "$BRANCH.zip"

	rm -r global
	mv "mine-zebro-$BRANCH" global
fi

#create local if it doesn't exist
mkdir local