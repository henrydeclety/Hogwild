killall SCREEN

# Default number of workers is 4
nb=${1:-4}

echo Terminating Containers..
kubectl delete statefulset systems --grace-period=0 --force

echo Launching with $nb workers
kubectl create -f stateful_set.yaml
json={'"spec"':{'"replicas"':$nb}}
kubectl patch statefulset systems -p "$json"

echo Creating Containers..
while [ ${#ADDR[@]} != $nb ]; do
PODS=$(kubectl get pods -o=jsonpath='{range .items[*]}{.metadata.name}{","}')
IFS=',' read -ra ADDR <<< "$PODS"
done
sleep 8

# Getting all pods
PODS=$(kubectl get pods --field-selector=status.phase==Running -o=jsonpath='{range .items[*]}{.metadata.name}{","}')
IFS=',' read -ra ADDR <<< "$PODS"

echo ${#ADDR[@]} running containers found

function join_by { local IFS="$1"; shift; echo "$*"; }

# For all pods
for pod in "${ADDR[@]}"; do

  IP=$(kubectl get pod "$pod" -o yaml | grep hostIP)
  IP="${IP:10}"

  other_ips=()

  # Get the ips of all other pods
  for other_pod in "${ADDR[@]}"; do
    if [ "$pod" != "$other_pod" ]; then

      other_IP=$(kubectl get pod "$other_pod" -o yaml | grep hostIP)
      other_ips+=("${other_IP:10}")
    fi
  done

  other_ips=$(join_by , "${other_ips[@]}")

  # Running the worker
  screen -dmS ${IP} bash -c "kubectl exec -it $pod python async_client.py 50051 ${other_ips} 100; exec sh"
  echo "${IP} -> ${other_ips}"

done

echo
echo Accède au stdout des workers dans les screens suivants:
screen -list
