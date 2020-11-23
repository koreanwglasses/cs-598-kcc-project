#/bin/bash
set -e

remote_url=`git config --get remote.origin.url`
read -p "Git Username: " username
read -sp "Password: " password
auth_remote_url=${remote_url/:\/\//:\/\/$username:$password@}

git fetch $auth_remote_url

function stagger() {
	i=0
	for inFile in data/*.csv; do
		if [ $(( $i % $1 )) == $2 ]; then
			python3 process.py $inFile
			base=$(basename -- "$inFile")
			git add out/$base
			git commit -m "processed $inFile"
			git push $auth_remote_url
			rm out/$base
	        fi
		let i=i+1
	done
}

trap 'kill $(jobs -p)' SIGINT

stagger 2 0 &
stagger 2 1 &
wait < <(jobs -p)
