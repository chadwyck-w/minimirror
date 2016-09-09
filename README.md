README.md

copy over to pi:
	rsync -avz ~/2016_experiments/minimirror pi@minimirror.local:

run:
	ssh pi@minimirror.local 'cd minimirror; sudo python minimirror.py'