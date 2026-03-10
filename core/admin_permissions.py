def permission_dashboard(request):
    return request.user.is_active and request.user.is_staff


def permission_transport_route(request):
    return request.user.has_perm("transport.view_route")


def permission_transport_stop(request):
    return request.user.has_perm("transport.view_stop")


def permission_transport_vehicle(request):
    return request.user.has_perm("transport.view_vehicle")


def permission_transport_vehiclelocation(request):
    return request.user.has_perm("transport.view_vehiclelocation")


def permission_auth_user(request):
    return request.user.has_perm("auth.view_user")


def permission_transport_favoriteroute(request):
    return request.user.has_perm("transport.view_favoriteroute")


def permission_transport_favoritestop(request):
    return request.user.has_perm("transport.view_favoritestop")


def permission_materials_projectmaterial(request):
    return request.user.has_perm("materials.view_projectmaterial")


# Section-level: transport section visible if user has at least one transport perm
def permission_section_transport(request):
    return any([
        request.user.has_perm("transport.view_route"),
        request.user.has_perm("transport.view_stop"),
        request.user.has_perm("transport.view_vehicle"),
        request.user.has_perm("transport.view_vehiclelocation"),
    ])


# Section-level: users section visible if user has user or favorites perm
def permission_section_users(request):
    return any([
        request.user.has_perm("auth.view_user"),
        request.user.has_perm("transport.view_favoriteroute"),
        request.user.has_perm("transport.view_favoritestop"),
    ])


# Section-level: materials section visible if user has materials perm
def permission_section_materials(request):
    return request.user.has_perm("materials.view_projectmaterial")
