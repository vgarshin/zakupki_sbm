#!/bin/bash

cd `dirname "$0"`

VOLUMES="-v /home/user/extradata:/home/user/extradata"
PROC_DATE=`date +%Y%m%d`
CACHE_DIR="cache_zakupki_companies_rng"
DATA_DIR="_data"
EMAIL="vgarshin@yandex.ru"
CONT_NAME="parcesites_zakupki_rng"
RNUM_START=19000000
RNUM_END=19200000
RNUM_STEP=20000

for ((RNUM=RNUM_START; RNUM<RNUM_END; RNUM+=RNUM_STEP))
	do
		RNUM_END_STEP=$(($RNUM+$RNUM_STEP))
		echo "collecting reestr numbers from $RNUM to $RNUM_END_STEP"
		
		sudo mkdir "../$CACHE_DIR"

		sudo docker run -i --name $CONT_NAME $VOLUMES extradata python zakupki/zakupki_companies_bs_range.py $DATA_DIR $PROC_DATE $CACHE_DIR $EMAIL $RNUM $RNUM_END_STEP
		sudo docker rm -f $CONT_NAME

		sudo rm -r "../$CACHE_DIR"
		sudo cp /home/user/extradata/_data/* /home/smbuser/chroot/

		sleep 10s
	done
