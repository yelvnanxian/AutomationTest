# 作用：提供start locust slave相关的Shell启动命令。

for((i=0;i<8;i++))
do
   locust -f $1 --slave --master-host=$2 &
done
