#!/bin/sh
# chmod +x ci_cid.sh
# sudo crontab -e & paste:
# Put this in sudo crontab -e ->
# * * * * * cd /home/ubuntu/dailyWord-bot/ && . ./ci_cd.sh > ./ci_cd.log 2>&1
#  0,10,15,20,30,40,50 * * * * cd /home/ubuntu/dailyWord-bot/ && . ./ci_cd.sh$
echo "Running pipeline on "$(date "+%d/%m/%y %H:%M:%S")""


CURRENT_TAG=$(git describe --tags)

# fetch the remote tags available
git fetch --tags
# retrieve the latest tag available by using the “git describe” command
LATEST_TAG=$(git describe --tags `git rev-list --tags --max-count=1`)
echo Current tag: $CURRENT_TAG, Latest tag: $LATEST_TAG

if [ $CURRENT_TAG = $LATEST_TAG ]
then
    echo "Not updating"
else
    echo "updating"
    export VERSION=$LATEST_TAG
    echo "Checking out to '$VERSION'"
    git checkout $VERSION

    echo "Deploying version: '$VERSION'"
    sudo docker-compose build
    sudo docker-compose down
    sudo -E docker-compose up -d
    echo "Deployed version: '$VERSION' on "$(date "+%d/%m/%y %H:%M:%S")""
fi
