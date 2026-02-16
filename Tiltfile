k8s_yaml('app.yaml')

docker_build('backend-api', context='.', dockerfile='Dockerfile',)

k8s_resource('backend-api', port_forwards='8000')