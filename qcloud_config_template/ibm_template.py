from qpandalite import create_ibm_online_config

if __name__ == '__main__':
    # The IBM account token
    token = 'c3d3da0c74dc1a77d194557c2a0fa969b5f1b2fc000b2f75f7181dc05e3816aa5a85ad05f48ba1606a9ca8a17f61e7c2d8c5b8182910be719f29252e66b1045c'
    
    create_ibm_online_config(default_token = token)