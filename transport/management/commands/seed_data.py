"""
Management command to seed BakuGo with realistic demo data.
Usage: python manage.py seed_data
"""
import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from transport.models import Route, Stop, RouteStop, Vehicle, VehicleLocation


# Realistic Baku bus stops with actual coordinates
STOPS_DATA = [
    # Central Baku
    {"name": "28 May Metro", "name_az": "28 May Metro", "code": "BKU001", "lat": 40.3794, "lng": 49.8511, "address": "28 May Street, Central Baku", "shelter": True},
    {"name": "Sahil Metro", "name_az": "Sahil Metro", "code": "BKU002", "lat": 40.3752, "lng": 49.8453, "address": "Neftchilar Avenue, Baku", "shelter": True},
    {"name": "İçərişəhər Metro", "name_az": "İçərişəhər Metro", "code": "BKU003", "lat": 40.3681, "lng": 49.8372, "address": "Old City area, Baku", "shelter": True},
    {"name": "Nizami Street", "name_az": "Nizami küçəsi", "code": "BKU004", "lat": 40.3775, "lng": 49.8495, "address": "Nizami Street, Central Baku", "shelter": False},
    {"name": "Fountains Square", "name_az": "Fəvvarələr meydanı", "code": "BKU005", "lat": 40.3765, "lng": 49.8478, "address": "Fountains Square, Baku", "shelter": False},
    # Narimanov District
    {"name": "Narimanov Metro", "name_az": "Nəriman Nərimanov Metro", "code": "BKU006", "lat": 40.4032, "lng": 49.8684, "address": "Narimanov District", "shelter": True},
    {"name": "Koroglu Metro", "name_az": "Koroğlu Metro", "code": "BKU007", "lat": 40.4112, "lng": 49.8672, "address": "Koroglu, Narimanov District", "shelter": True},
    {"name": "Ganjlik Metro", "name_az": "Gənclik Metro", "code": "BKU008", "lat": 40.4073, "lng": 49.8619, "address": "Ganjlik Mall Area", "shelter": True},
    # Surakhani / East Baku
    {"name": "Hazi Aslanov Metro", "name_az": "Həzi Aslanov Metro", "code": "BKU009", "lat": 40.3984, "lng": 49.9438, "address": "Hazi Aslanov, Surakhani", "shelter": True},
    {"name": "Ahmadli Metro", "name_az": "Əhmədli Metro", "code": "BKU010", "lat": 40.4053, "lng": 49.9185, "address": "Ahmadli District", "shelter": True},
    {"name": "Khalglar Dostlugu Metro", "name_az": "Xalqlar Dostluğu Metro", "code": "BKU011", "lat": 40.3972, "lng": 49.9078, "address": "Khalglar Dostlugu", "shelter": True},
    # Yasamal District
    {"name": "8 November Station", "name_az": "8 Noyabr", "code": "BKU012", "lat": 40.3841, "lng": 49.8413, "address": "8 November Avenue, Yasamal", "shelter": False},
    {"name": "Stadium Stop", "name_az": "Stadion", "code": "BKU013", "lat": 40.3853, "lng": 49.8579, "address": "Tofig Bahramov Stadium, Baku", "shelter": True},
    {"name": "Memar Ajami Metro", "name_az": "Memar Əcəmi Metro", "code": "BKU014", "lat": 40.4072, "lng": 49.8344, "address": "Memar Ajami, Binagadi", "shelter": True},
    {"name": "Avtovagzal (Bus Terminal)", "name_az": "Avtovağzal", "code": "BKU015", "lat": 40.4097, "lng": 49.8308, "address": "Binagadi Highway, Bus Terminal", "shelter": True},
    # Sabunchu / Airport area
    {"name": "Bina Stop", "name_az": "Binə", "code": "BKU016", "lat": 40.4549, "lng": 50.0168, "address": "Bina, Sabunchu District", "shelter": True},
    {"name": "Airport Terminal", "name_az": "Hava limanı", "code": "BKU017", "lat": 40.4675, "lng": 50.0467, "address": "Heydar Aliyev International Airport", "shelter": True},
    # Biləcəri
    {"name": "Bilajeari Depot", "name_az": "Bilaşəri Depo", "code": "BKU018", "lat": 40.4218, "lng": 49.8195, "address": "Bilajeari, Binagadi", "shelter": False},
    # White City / Khazar
    {"name": "Aga Neymatulla Stop", "name_az": "Ağa Neymatulla", "code": "BKU019", "lat": 40.3616, "lng": 49.8853, "address": "Khazar District, White City", "shelter": False},
    {"name": "Bayil Stop", "name_az": "Bayıl", "code": "BKU020", "lat": 40.3445, "lng": 49.8222, "address": "Bayil, Baku", "shelter": False},
    # Binagadi
    {"name": "Binagadi Stop", "name_az": "Binəqədi", "code": "BKU021", "lat": 40.4531, "lng": 49.8061, "address": "Binagadi District", "shelter": True},
    # Lökbatan
    {"name": "Lokbatan Stop", "name_az": "Lökbatan", "code": "BKU022", "lat": 40.3827, "lng": 49.6953, "address": "Lokbatan, Garadagh", "shelter": False},
]

# Route definitions
ROUTES_DATA = [
    {
        "number": "1", "name": "28 May – Sahil – İçərişəhər",
        "type": "bus", "color": "#0ea5e9", "freq": 10, "hours": "06:00 - 23:00",
        "stops": ["BKU001", "BKU004", "BKU005", "BKU002", "BKU003"],
        "description": "Central Baku circular route connecting major metro stations."
    },
    {
        "number": "5", "name": "Ganjlik – Narimanov – Sahil",
        "type": "bus", "color": "#8b5cf6", "freq": 12, "hours": "06:00 - 23:30",
        "stops": ["BKU008", "BKU007", "BKU006", "BKU013", "BKU002"],
        "description": "Route connecting Ganjlik and Narimanov district to Central Baku."
    },
    {
        "number": "14", "name": "28 May – Hazi Aslanov",
        "type": "bus", "color": "#10b981", "freq": 15, "hours": "06:30 - 22:30",
        "stops": ["BKU001", "BKU011", "BKU010", "BKU009"],
        "description": "East Baku connector linking 28 May to Hazi Aslanov metro."
    },
    {
        "number": "21", "name": "Memar Ajami – 28 May – Stadium",
        "type": "bus", "color": "#f59e0b", "freq": 20, "hours": "07:00 - 22:00",
        "stops": ["BKU014", "BKU015", "BKU001", "BKU004", "BKU013"],
        "description": "West Baku to Central coverage via main thoroughfare."
    },
    {
        "number": "65", "name": "Bina – Airport Express",
        "type": "express", "color": "#ef4444", "freq": 30, "hours": "05:00 - 23:59",
        "stops": ["BKU016", "BKU017"],
        "description": "Express service connecting Bina area to Heydar Aliyev International Airport."
    },
    {
        "number": "108", "name": "Bayil – 28 May – Koroglu",
        "type": "bus", "color": "#06b6d4", "freq": 18, "hours": "06:00 - 23:00",
        "stops": ["BKU020", "BKU003", "BKU002", "BKU001", "BKU006", "BKU007"],
        "description": "Long cross-city route from Bayil peninsula to Narimanov."
    },
    {
        "number": "45", "name": "Avtovagzal – Ganjlik – Koroglu",
        "type": "minibus", "color": "#84cc16", "freq": 8, "hours": "07:00 - 21:00",
        "stops": ["BKU015", "BKU014", "BKU008", "BKU007"],
        "description": "Minibus route serving Binagadi and Narimanov district."
    },
    {
        "number": "125N", "name": "Night: Sahil – Narimanov – Memar Ajami",
        "type": "night", "color": "#1e3a5f", "freq": 40, "hours": "23:00 - 06:00",
        "stops": ["BKU002", "BKU006", "BKU014"],
        "description": "Night bus providing late service to key areas."
    },
    {
        "number": "71", "name": "Binagadi – Avtovagzal – 28 May",
        "type": "bus", "color": "#d946ef", "freq": 15, "hours": "06:00 - 22:00",
        "stops": ["BKU021", "BKU015", "BKU014", "BKU012", "BKU001"],
        "description": "Binagadi district to central Baku service."
    },
]

VEHICLE_PLATES = [
    "10 AB 001", "10 AB 002", "10 AZ 143", "10 AZ 144", "10 BY 209",
    "77 AB 320", "77 AB 321", "77 AZ 012", "99 AX 500", "99 AX 501",
    "10 NH 100", "10 NH 101", "77 BK 304", "77 BK 305", "99 BA 210",
    "10 BR 410", "10 BR 411", "77 BY 620", "99 XA 801", "99 XA 802",
]


class Command(BaseCommand):
    help = 'Seed the database with realistic Baku transport demo data'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing data before seeding')

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing transport data...')
            VehicleLocation.objects.all().delete()
            Vehicle.objects.all().delete()
            RouteStop.objects.all().delete()
            Route.objects.all().delete()
            Stop.objects.all().delete()

        self.stdout.write('Creating stops...')
        stops_map = {}
        for s in STOPS_DATA:
            stop, created = Stop.objects.update_or_create(
                code=s['code'],
                defaults={
                    'name': s['name'],
                    'name_az': s['name_az'],
                    'latitude': s['lat'],
                    'longitude': s['lng'],
                    'address': s['address'],
                    'has_shelter': s['shelter'],
                    'is_active': True,
                }
            )
            stops_map[s['code']] = stop
            if created:
                self.stdout.write(f'  Created stop: {stop.name}')

        self.stdout.write('Creating routes and assigning stops...')
        routes_map = {}
        plate_idx = 0

        for r in ROUTES_DATA:
            route, created = Route.objects.update_or_create(
                number=r['number'],
                defaults={
                    'name': r['name'],
                    'route_type': r['type'],
                    'color': r['color'],
                    'frequency_minutes': r['freq'],
                    'operating_hours': r['hours'],
                    'description': r['description'],
                    'is_active': True,
                }
            )
            routes_map[r['number']] = route

            if created:
                self.stdout.write(f'  Created route: {route.number} - {route.name}')

            # Create route stops
            RouteStop.objects.filter(route=route).delete()
            for order, code in enumerate(r['stops'], start=1):
                stop = stops_map.get(code)
                if stop:
                    RouteStop.objects.create(
                        route=route,
                        stop=stop,
                        order=order,
                        distance_from_previous=random.randint(300, 1200),
                        travel_time_from_previous=random.randint(2, 6) if order > 1 else 0,
                    )

            # Assign vehicles to each route
            num_vehicles = random.randint(2, 4)
            for _ in range(num_vehicles):
                if plate_idx < len(VEHICLE_PLATES):
                    plate = VEHICLE_PLATES[plate_idx]
                    plate_idx += 1
                    vehicle, v_created = Vehicle.objects.update_or_create(
                        plate_number=plate,
                        defaults={
                            'route': route,
                            'vehicle_type': 'minibus' if r['type'] == 'minibus' else 'bus',
                            'capacity': 25 if r['type'] == 'minibus' else 80,
                            'status': random.choice(['active', 'active', 'active', 'idle']),
                            'is_active': True,
                        }
                    )
                    if v_created:
                        self.stdout.write(f'    Vehicle: {plate}')

                    # Create vehicle location near a stop on its route
                    route_stops = RouteStop.objects.filter(route=route).select_related('stop')
                    if route_stops.exists():
                        random_stop = random.choice(list(route_stops)).stop
                        VehicleLocation.objects.update_or_create(
                            vehicle=vehicle,
                            defaults={
                                'latitude': float(random_stop.latitude) + random.uniform(-0.002, 0.002),
                                'longitude': float(random_stop.longitude) + random.uniform(-0.003, 0.003),
                                'speed': random.uniform(0, 45),
                                'heading': random.uniform(0, 360),
                            }
                        )

        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Seeding complete!\n'
            f'  Stops:    {Stop.objects.count()}\n'
            f'  Routes:   {Route.objects.count()}\n'
            f'  Vehicles: {Vehicle.objects.count()}\n'
            f'  Locations:{VehicleLocation.objects.count()}'
        ))
