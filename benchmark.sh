lambdas=(0.001 0.005 0.01)
nb_workers=(4 10 30)

echo Async..
for lambda in "${lambdas[@]}"; do
  for nb_worker in "${nb_workers[@]}"; do
    bash deploy.sh Async $nb_worker $lambda
    sleep 30
  done
done

echo Sync..
for lambda in "${lambdas[@]}"; do
  for nb_worker in "${nb_workers[@]}"; do
    bash deploy.sh Sync $nb_worker $lambda
    sleep 30
  done
done
