# k8s-statefulsetscheduler
Schedules Statefulsets to fixed nodes matching a specific name. The scheduling task is defined with a Custom Resource.
It is a very basic tool. Feel free to extend it and open pull requests.

Currently, the tool only supports checking if the pod should not be scheduled on a worker node (e.g. if drained or cordoned).

# License
This code is licensed under the GNU Affero General Public License version 3.

# Install
With helm
```
helm repo add codeflixde-statefulsetscheduler https://codeflixde.github.io/k8s-statefulsetscheduler/

helm upgrade --install -n <namespace> --create-namespace <name> cf-statefulsetscheduler/statefulsetscheduler
```
# Usage

The Custom Resource requires to define the statefulset pod prefix. The scheduler name is optional, falling back to the default name if not set.
The "nodeNames" array must be ordered. The pod instances are scheduled with respect to the order of the array.

An example is provided in the examples directory. Just try it out.