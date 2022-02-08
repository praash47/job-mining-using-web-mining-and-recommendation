logsdir=$PWD

for entry in $(find "$logsdir" -maxdepth 5 -iname "*.log") 
do
  echo "" > $entry
done
