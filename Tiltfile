docker_build(
    'backend-api',
    context='.',
    build_args={'UV_NO_DEV': '1'},
    live_update=[
        sync('.', '/app'),
        run('uv sync',
            trigger=['pyproject.toml', 'uv.lock']),
    ]
)
k8s_yaml('app.yaml')
k8s_resource('backend-api', port_forwards='8000')