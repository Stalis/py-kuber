from os import path
from kubernetes import client, config
from kubernetes.client.api.apps_v1_api import AppsV1Api
from kubernetes.client.api.core_v1_api import CoreV1Api
import yaml


class KubeHelper:
    def __init__(self, 
            config_file=None, 
            context=None, 
            client_configuration=None,
            persist_config=None):
        config.load_kube_config(
            config_file=config_file, 
            context=context,
            client_configuration=client_configuration,
            persist_config=persist_config)
        self.__apps_v1 = None
        self.__core_v1 = None
        pass

    @property
    def apps_v1(self) -> AppsV1Api:
        if self.__apps_v1 is None:
            self.__apps_v1 = client.AppsV1Api()
        return self.__apps_v1
    
    @property
    def core_v1(self) -> CoreV1Api:
        if self.__core_v1 is None:
            self.__core_v1 = client.CoreV1Api()
        return self.__core_v1


class AppDeployer(KubeHelper):
    def __init__(self, config_path):
        super().__init__()
        self.config_path = config_path
    
    def read_config(self, file_name):
        with open(path.join(self.config_path, file_name)) as f:
            return yaml.safe_load(f)

    def print_pods(self):
        pods = self.core_v1.list_pod_for_all_namespaces(watch=False)
        for item in pods.items:
            print("%s\t%s\t%s\n" % (item.status.pod_ip, item.metadata.namespace, item.metadata.name))

    def create_deployment(self, config_body):
        self.apps_v1.create_namespaced_deployment(
            namespace='default', body=config_body)

    def delete_deployment(self, dep_name: str):
        self.apps_v1.delete_namespaced_deployment(dep_name, 'default')

    def create_service(self, config_body):
        self.core_v1.create_namespaced_service(
            namespace='default', body=config_body)

    def deploy_app(self):
        deployment = self.read_config('deployment.yml')
        service = self.read_config('service.yml')

        self.create_deployment(deployment)

        try:
            self.create_service(service)
        except:
            self.delete_deployment(deployment['metadata']['name'])
            raise

def main():
    deployer = AppDeployer(path.join(path.dirname(__file__), 'hello-minikube'))
    deployer.print_pods()
    deployer.deploy_app()

if __name__ == '__main__':
    main()