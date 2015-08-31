#!/bin/bash
ROOT=/home/stackone/stackone_backup
DATE=$(date +%Y-%m-%d:%H:%M)
LOG="/home/stackone/stackone/stackone_back.log"
USER=root
PWD=stackonesam

#

#传入的第一个参数是0的话，进行备份
if [ $1 -eq 0 ];then

BACKUP_PATH=$ROOT/$2
MYSQLNAME=$BACKUP_PATH/stackone_cloud.sql
IMAGENAME=$BACKUP_PATH/image_store.tar
BACKUP_PATHFILE=$ROOT/$2.tar
#创建备份目录
if [ ! -e $ROOT ];then
 mkdir -p $ROOT
 ln -s $ROOT /home/stackone/stackone/stackone/public/stackone_backup
 if [ -e $ROOT ];then
 echo "$(date +%c):======create $ROOT direct">>$LOG
 fi
fi

#创建备份目录
if [ ! -e $BACKUP_PATH ];then
 mkdir -p $BACKUP_PATH
 if [ -e $BACKUP_PATH ];then
 echo "$(date +%c):======create $BACKUP_PATH direct">>$LOG
 fi
fi

#执行mysql数据库的备份
mysqldump --single-transaction --ignore-table=stackone_cloud.metrics --ignore-table=stackone_cloud.metrics_arch --ignore-table=stackone_cloud.metrics_curr -u$USER   -p$PWD stackone_cloud>${MYSQLNAME}
mysqlresult=$?
echo "mysql ---->$mysqlresult"

if [ -e $MYSQLNAME ]
 then
 echo "$(date +%c):======mysql backup result:success and $MYSQLNAME is created!">>$LOG
else
  echo "$(date +%c):======mysql bcakup result:false!">>$LOG
fi

#执行image_store的备份
echo "$(date +%c):======excuse image_storate backup">>$LOG
tar zcvf $IMAGENAME -C /home/stackone/stackone image_store >>$LOG
imageresult=$?
echo "image ---->$imageresult"

if [ -e $IMAGENAME ]
 then
 echo "$(date +%c):======image_storate backup result:success and $IMAGENAME is created!">>$LOG
else
  echo "$(date +%c):======image_storate bcakup result:false!">>$LOG
fi

if [ $mysqlresult -eq 0 -a  $imageresult -eq 0 ]
then
tar zcvf $BACKUP_PATHFILE -C $ROOT $2 >>$LOG
rm -fr $BACKUP_PATH
md5sum $BACKUP_PATHFILE>$ROOT/md5
echo "path@$BACKUP_PATHFILE"
else
echo "path@failed"
fi


#传入的第一个参数为1，进行还原
elif [ $1 -eq 1 ]
then

BACKUP_PATH=$3
if [ ! -e $2 ];then
  echo "$2 is not exist!"
  echo "$(date +%c)======file $2 dose not exist!">>$LOG
else
#先解压tar文件
tar xvf $2 -C $ROOT>>$LOG 
#还原mysql数据库
 
#先备份platform_backup表
  mysqldump  -u$USER   -p$PWD stackone_cloud platform_backup>$BACKUP_PATH/platform_backup.sql
#还原备份表
  mysql  -u$USER   -p$PWD stackone_cloud<$BACKUP_PATH/stackone_cloud.sql
  mysql  -u$USER   -p$PWD stackone_cloud<$BACKUP_PATH/platform_backup.sql
  mysql_result=$?

#还原image_store，此处在生产环境中需修改
  tar zxvf $BACKUP_PATH/image_store.tar -C /home/stackone/stackone/>>$LOG
  image_result=$?
fi



if [ $mysql_result -eq 0 -a  $image_result -eq 0 ]
then
rm -fr $BACKUP_PATH
echo "$(date +%c)======file $2 restore successed!">>$LOG
echo "restore_result@successfully"
else
echo "$(date +%c)======file $2 restore failed!">>$LOG
echo "restore_result@failed"
fi

fi
