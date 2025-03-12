#!/bin/bash
# Check for updates

cd ota_updates
git fetch
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse @{u})

if [ $LOCAL != $REMOTE ]; then

  echo “Repository is outdated. Updating…”

  # git pull

  # Download updates

  git checkout master

  # Replace the current application with the updated version

  rsync -a ./..

  # Restart the application

  sudo service your_application restart

else

  echo “Repository is up to date.”

fi
