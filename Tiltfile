docker_build(
    'backend-api',
    context='.',
    live_update=[
        sync('.', '/app'),
    ]
)
k8s_yaml('app.yaml')
k8s_resource('backend-api', port_forwards='8000')