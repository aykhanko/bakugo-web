from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Prefetch
from .models import Route, Stop, RouteStop, Vehicle, VehicleLocation
from .forms import RoutePlannerForm


def home(request):
    """Public landing page."""
    stats = {
        'routes': Route.objects.filter(is_active=True).count(),
        'stops': Stop.objects.filter(is_active=True).count(),
        'vehicles': Vehicle.objects.filter(is_active=True).count(),
    }
    featured_routes = Route.objects.filter(is_active=True).order_by('number')[:6]
    benefits = [
        'Mobile-first design for on-the-go use',
        'Real-time vehicle tracking on maps',
        'Simple route planner between any two points',
        'Clean stop information with route coverage',
        'Free to use, no account required for browsing',
    ]
    return render(request, 'transport/home.html', {
        'stats': stats,
        'featured_routes': featured_routes,
        'benefits': benefits,
    })


def route_list(request):
    """Browse all active routes."""
    query = request.GET.get('q', '').strip()
    route_type = request.GET.get('type', '')

    routes = Route.objects.filter(is_active=True)

    if query:
        routes = routes.filter(Q(number__icontains=query) | Q(name__icontains=query))
    if route_type:
        routes = routes.filter(route_type=route_type)

    routes = routes.order_by('number')

    return render(request, 'transport/route_list.html', {
        'routes': routes,
        'query': query,
        'route_type': route_type,
        'route_type_choices': Route.ROUTE_TYPE_CHOICES,
    })


def route_detail(request, pk):
    """Detail page for a single route."""
    route = get_object_or_404(Route, pk=pk, is_active=True)
    route_stops = RouteStop.objects.filter(route=route).select_related('stop').order_by('order')
    vehicles = Vehicle.objects.filter(route=route, is_active=True).select_related('location')

    # Build vehicle location data for map
    vehicle_locations = []
    for v in vehicles:
        if hasattr(v, 'location'):
            vehicle_locations.append({
                'plate': v.plate_number,
                'lat': float(v.location.latitude),
                'lng': float(v.location.longitude),
                'speed': v.location.speed,
                'status': v.status,
            })

    stop_coords = []
    for rs in route_stops:
        stop_coords.append({
            'name': rs.stop.name,
            'lat': float(rs.stop.latitude),
            'lng': float(rs.stop.longitude),
            'order': rs.order,
        })

    return render(request, 'transport/route_detail.html', {
        'route': route,
        'route_stops': route_stops,
        'vehicles': vehicles,
        'vehicle_locations': vehicle_locations,
        'stop_coords': stop_coords,
    })


def stop_list(request):
    """Browse all active stops."""
    query = request.GET.get('q', '').strip()
    stops = Stop.objects.filter(is_active=True)

    if query:
        stops = stops.filter(Q(name__icontains=query) | Q(address__icontains=query) | Q(code__icontains=query))

    stops = stops.order_by('name')

    return render(request, 'transport/stop_list.html', {
        'stops': stops,
        'query': query,
    })


def stop_detail(request, pk):
    """Detail page for a single stop."""
    stop = get_object_or_404(Stop, pk=pk, is_active=True)
    route_stops = RouteStop.objects.filter(stop=stop).select_related('route').order_by('route__number')

    # Nearby vehicles – vehicles currently on routes serving this stop
    route_ids = route_stops.values_list('route_id', flat=True)
    nearby_vehicles = Vehicle.objects.filter(
        route_id__in=route_ids, is_active=True, status='active'
    ).select_related('location', 'route')

    return render(request, 'transport/stop_detail.html', {
        'stop': stop,
        'route_stops': route_stops,
        'nearby_vehicles': nearby_vehicles,
    })


def route_planner(request):
    """Simple route suggestion between two stops."""
    form = RoutePlannerForm(request.GET or None)
    results = None
    origin_stop = None
    destination_stop = None

    if form.is_valid():
        origin_query = form.cleaned_data['origin']
        dest_query = form.cleaned_data['destination']

        # Find best matching stops
        origin_stops = Stop.objects.filter(
            Q(name__icontains=origin_query) | Q(address__icontains=origin_query),
            is_active=True
        )[:5]
        dest_stops = Stop.objects.filter(
            Q(name__icontains=dest_query) | Q(address__icontains=dest_query),
            is_active=True
        )[:5]

        if origin_stops and dest_stops:
            origin_stop = origin_stops[0]
            destination_stop = dest_stops[0]
            results = _find_routes(origin_stop, destination_stop)

    return render(request, 'transport/route_planner.html', {
        'form': form,
        'results': results,
        'origin_stop': origin_stop,
        'destination_stop': destination_stop,
    })


def _find_routes(origin_stop, destination_stop):
    """
    Simple route suggestion logic.
    1. Find direct routes serving both stops.
    2. If none, find transfer options (routes from origin + routes to destination with a common stop).
    """
    # Get routes serving origin
    origin_route_ids = set(
        RouteStop.objects.filter(stop=origin_stop).values_list('route_id', flat=True)
    )
    # Get routes serving destination
    dest_route_ids = set(
        RouteStop.objects.filter(stop=destination_stop).values_list('route_id', flat=True)
    )

    direct_route_ids = origin_route_ids & dest_route_ids
    suggestions = []

    # Direct routes
    for route_id in direct_route_ids:
        route = Route.objects.get(pk=route_id)
        origin_rs = RouteStop.objects.get(route=route, stop=origin_stop)
        dest_rs = RouteStop.objects.get(route=route, stop=destination_stop)
        if origin_rs.order <= dest_rs.order:
            # Count stops between
            stops_between = dest_rs.order - origin_rs.order
            suggestions.append({
                'type': 'direct',
                'route': route,
                'from_stop': origin_stop,
                'to_stop': destination_stop,
                'stops_count': stops_between,
                'estimated_minutes': stops_between * route.frequency_minutes // 3 + 5,
                'transfers': [],
            })

    # Transfer options (one transfer) – only if no direct found or to offer alternatives
    if len(suggestions) < 3:
        for origin_route_id in origin_route_ids - direct_route_ids:
            origin_route = Route.objects.get(pk=origin_route_id)
            # Find stops on this origin route
            origin_route_stop_ids = set(
                RouteStop.objects.filter(route=origin_route).values_list('stop_id', flat=True)
            )
            for dest_route_id in dest_route_ids - direct_route_ids:
                if origin_route_id == dest_route_id:
                    continue
                dest_route = Route.objects.get(pk=dest_route_id)
                dest_route_stop_ids = set(
                    RouteStop.objects.filter(route=dest_route).values_list('stop_id', flat=True)
                )
                # Transfer stops
                transfer_stop_ids = origin_route_stop_ids & dest_route_stop_ids
                for transfer_stop_id in list(transfer_stop_ids)[:1]:
                    transfer_stop = Stop.objects.get(pk=transfer_stop_id)
                    leg1_rs = RouteStop.objects.get(route=origin_route, stop=origin_stop)
                    transfer_rs1 = RouteStop.objects.get(route=origin_route, stop=transfer_stop)
                    transfer_rs2 = RouteStop.objects.get(route=dest_route, stop=transfer_stop)
                    dest_rs = RouteStop.objects.get(route=dest_route, stop=destination_stop)

                    if leg1_rs.order <= transfer_rs1.order and transfer_rs2.order <= dest_rs.order:
                        stops1 = transfer_rs1.order - leg1_rs.order
                        stops2 = dest_rs.order - transfer_rs2.order
                        suggestions.append({
                            'type': 'transfer',
                            'route': origin_route,
                            'from_stop': origin_stop,
                            'to_stop': destination_stop,
                            'stops_count': stops1 + stops2,
                            'estimated_minutes': (stops1 + stops2) * 3 + 10,
                            'transfers': [{'stop': transfer_stop, 'route': dest_route}],
                        })
                        if len(suggestions) >= 3:
                            break
                if len(suggestions) >= 3:
                    break

    # Sort: direct first, then by estimated time
    suggestions.sort(key=lambda x: (0 if x['type'] == 'direct' else 1, x['estimated_minutes']))
    return suggestions[:3]


def map_view(request):
    """Live map showing stops and vehicles."""
    stops = Stop.objects.filter(is_active=True).values('id', 'name', 'latitude', 'longitude')
    vehicles = VehicleLocation.objects.select_related('vehicle', 'vehicle__route').all()

    stop_data = [
        {'id': s['id'], 'name': s['name'], 'lat': float(s['latitude']), 'lng': float(s['longitude'])}
        for s in stops
    ]
    vehicle_data = [
        {
            'plate': v.vehicle.plate_number,
            'lat': float(v.latitude),
            'lng': float(v.longitude),
            'route': v.vehicle.route.number if v.vehicle.route else '?',
            'speed': v.speed,
        }
        for v in vehicles
    ]

    return render(request, 'transport/map_view.html', {
        'stop_data': stop_data,
        'vehicle_data': vehicle_data,
    })
