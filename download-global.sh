


#specify branch
if [[ $# -lt 1 ]]
then
	BRANCH='main'
else
	BRANCH=$1
fi

cd /home/pi

#download latest version
wget --tries=2 https://github.com/The-Redstar/mine-zebro/archive/$BRANCH.zip
unzip $BRANCH.zip
rm $BRANCH.zip

rm -r global
mv mine-zebro-$BRANCH global


#create local if it doesn't exist
mkdir local