# generates result for each csv file in /etc/data

for file in etc/data/*
do
  if [[ -f $file && $file == *.csv ]]; then
    echo "processing " $file
    (time python src/main.py -f $file)  > "etc/out1/$(basename $file .csv).out" 2>&1
  fi
done
