#!/bin/bash

URL = "https://onyinyechiaguhackathon.duckdns.org/*"

if curl --output /dev/null --silent --head --fail  "$URL"
then
       echo "This URL Exist"
else
      echo "This URL Not Exist"
fi

