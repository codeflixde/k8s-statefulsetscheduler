from kubernetes import client, config
from time import sleep

config.load_config()
v1 = client.CoreV1Api()


def get_crds():
    crds = client.CustomObjectsApi().list_cluster_custom_object(group="k8s.codeflix.com", version="v1",
                                                                plural="statefulsetschedulers")
    for crd in crds['items']:
        namespace = crd['metadata']['namespace']
        pod_prefix = crd['spec']['podName']
        node_names = crd['spec']['nodeNames']
        scheduler_name = crd['spec']['schedulerName']

        schedule_pods(namespace, pod_prefix, scheduler_name, node_names)
        # v1.list_namespaced_pod(namespace,
        #                        watch=False,
        #                        field_selector='spec.schedulerName==statefulset-scheduler,status.phase==Pending')


def remove_prefix(text, prefix):
    if text.startswith(prefix):
        return text[len(prefix):]
    return text  # or whatever


def schedule_pods(namespace, prefix, scheduler_name, target_node_names):
    pods = v1.list_namespaced_pod(namespace,
                                  watch=False,
                                  field_selector=f'spec.schedulerName=={scheduler_name},status.phase==Pending')

    nodes = v1.list_node()
    for i in pods.items:
        try:
            pod_name = i.metadata.labels['statefulset.kubernetes.io/pod-name']
            index = int(remove_prefix(pod_name, f"{prefix}-"))
            designated_node = target_node_names[index]

            node = list(filter(lambda x: x.metadata.name == designated_node, nodes.items))[0]
            if node.spec.taints is not None:
                taint_no_schedule = list(filter(lambda x: x.effect == 'NoSchedule', node.spec.taints))
                if len(taint_no_schedule) > 0:
                    continue

            pod_binding = {
                "apiVersion": "v1",
                "kind": "Binding",
                "metadata": {
                    "name": i.metadata.name
                },
                "target": {
                    "apiVersion": "v1",
                    "kind": "Node",
                    "name": node.metadata.name
                }
            }
            v1.api_client.call_api(f"/api/v1/namespaces/{i.metadata.namespace}/pods/{i.metadata.name}/binding/",
                                   'POST',
                                   body=pod_binding,
                                   response_type='V1Status',
                                   auth_settings=['BearerToken'])
        except Exception as err:
            print(err)
            pass


while True:
    get_crds()
    sleep(5)
