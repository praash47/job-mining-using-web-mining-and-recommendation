logsdir=/home/aasis/Documents/GitHub/job-mining-using-web-mining-and-recommendation/jobminersserver/

for entry in $(find "$logsdir" -maxdepth 5 -iname "*.log") 
do
  echo "" > $entry
done
