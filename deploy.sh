killall SCREEN

# Default number of workers is 4
nb=${1:-4}

echo Terminating Containers..
# kubectl delete statefulset systems --grace-period=0 --force
kubectl delete -f stateful_set.yaml

echo Launching with $nb workers
kubectl create -f stateful_set.yaml
json={'"spec"':{'"replicas"':$nb}}
kubectl patch statefulset systems -p "$json"

echo Creating Containers..
while [ ${#ADDR[@]} != $nb ]; do
PODS=$(kubectl get pods --field-selector=status.phase==Running -o=jsonpath='{range .items[*]}{.metadata.name}{","}')
IFS=',' read -ra ADDR <<< "$PODS"
done
# sleep 30

# Getting all pods
PODS=$(kubectl get pods --field-selector=status.phase==Running -o=jsonpath='{range .items[*]}{.metadata.name}{","}')
IFS=',' read -ra ADDR <<< "$PODS"

function join_by { local IFS="$1"; shift; echo "$*"; }

# For all pods
for pod in "${ADDR[@]}"; do

  # Get the hostname of all other pods
  other_hosts=()
  for other_pod in "${ADDR[@]}"; do
    if [ "$pod" != "$other_pod" ]; then
      other_hosts+=("$other_pod.nginx.cs449g3.svc.k8s.iccluster.epfl.ch")
    fi
  done

  # Running the worker
  other_hosts=$(join_by , "${other_hosts[@]}")
  screen -dmS $pod bash -c "kubectl exec -it $pod python async_client.py ${other_hosts} 100; exec sh"

done

echo
echo Pour afficher les workers run:
echo bash show.sh
