from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Route(models.Model):
    """A bus route operating in Baku."""
    ROUTE_TYPE_CHOICES = [
        ('bus', 'Bus'),
        ('minibus', 'Minibus'),
        ('express', 'Express'),
        ('night', 'Night Bus'),
    ]

    number = models.CharField(max_length=20, unique=True, verbose_name=_('Route Number'))
    name = models.CharField(max_length=200, verbose_name=_('Route Name'))
    route_type = models.CharField(max_length=20, choices=ROUTE_TYPE_CHOICES, default='bus', verbose_name=_('Type'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    color = models.CharField(max_length=7, default='#0ea5e9', verbose_name=_('Color (hex)'))
    frequency_minutes = models.PositiveIntegerField(default=15, verbose_name=_('Frequency (min)'))
    operating_hours = models.CharField(max_length=50, default='06:00 - 23:00', verbose_name=_('Operating Hours'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['number']
        verbose_name = _('Route')
        verbose_name_plural = _('Routes')

    def __str__(self):
        return f"Route {self.number} – {self.name}"

    @property
    def stop_count(self):
        return self.route_stops.count()

    @property
    def vehicle_count(self):
        return self.vehicles.filter(is_active=True).count()


class Stop(models.Model):
    """A bus stop in Baku."""
    name = models.CharField(max_length=200, verbose_name=_('Stop Name'))
    name_az = models.CharField(max_length=200, blank=True, verbose_name=_('Name (Azerbaijani)'))
    code = models.CharField(max_length=20, blank=True, unique=True, null=True, verbose_name=_('Stop Code'))
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name=_('Latitude'))
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name=_('Longitude'))
    address = models.CharField(max_length=300, blank=True, verbose_name=_('Address'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    has_shelter = models.BooleanField(default=False, verbose_name=_('Has Shelter'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = _('Stop')
        verbose_name_plural = _('Stops')

    def __str__(self):
        return self.name

    @property
    def routes(self):
        return Route.objects.filter(route_stops__stop=self, is_active=True).distinct()


class RouteStop(models.Model):
    """Ordered relationship between a route and its stops."""
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='route_stops', verbose_name=_('Route'))
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='route_stops', verbose_name=_('Stop'))
    order = models.PositiveIntegerField(verbose_name=_('Order'))
    distance_from_previous = models.PositiveIntegerField(default=0, verbose_name=_('Distance from prev. (m)'))
    travel_time_from_previous = models.PositiveIntegerField(default=0, verbose_name=_('Travel time from prev. (min)'))

    class Meta:
        ordering = ['route', 'order']
        unique_together = [('route', 'stop'), ('route', 'order')]
        verbose_name = _('Route Stop')
        verbose_name_plural = _('Route Stops')

    def __str__(self):
        return f"{self.route.number} → {self.stop.name} (#{self.order})"


class Vehicle(models.Model):
    """A bus/vehicle assigned to a route."""
    VEHICLE_STATUS_CHOICES = [
        ('active', 'Active'),
        ('idle', 'Idle'),
        ('maintenance', 'Maintenance'),
        ('offline', 'Offline'),
    ]

    plate_number = models.CharField(max_length=20, unique=True, verbose_name=_('Plate Number'))
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicles', verbose_name=_('Route'))
    vehicle_type = models.CharField(max_length=50, default='bus', verbose_name=_('Vehicle Type'))
    capacity = models.PositiveIntegerField(default=80, verbose_name=_('Capacity'))
    status = models.CharField(max_length=20, choices=VEHICLE_STATUS_CHOICES, default='active', verbose_name=_('Status'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['plate_number']
        verbose_name = _('Vehicle')
        verbose_name_plural = _('Vehicles')

    def __str__(self):
        route_info = f" ({self.route.number})" if self.route else ""
        return f"{self.plate_number}{route_info}"


class VehicleLocation(models.Model):
    """Current or recent location of a vehicle."""
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name='location', verbose_name=_('Vehicle'))
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name=_('Latitude'))
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name=_('Longitude'))
    speed = models.FloatField(default=0.0, verbose_name=_('Speed (km/h)'))
    heading = models.FloatField(default=0.0, verbose_name=_('Heading (degrees)'))
    timestamp = models.DateTimeField(auto_now=True, verbose_name=_('Last Updated'))

    class Meta:
        verbose_name = _('Vehicle Location')
        verbose_name_plural = _('Vehicle Locations')

    def __str__(self):
        return f"{self.vehicle.plate_number} @ ({self.latitude}, {self.longitude})"


class FavoriteRoute(models.Model):
    """A route saved by a user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_routes')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('user', 'route')]
        verbose_name = _('Favorite Route')
        verbose_name_plural = _('Favorite Routes')

    def __str__(self):
        return f"{self.user.username} → Route {self.route.number}"


class FavoriteStop(models.Model):
    """A stop saved by a user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_stops')
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('user', 'stop')]
        verbose_name = _('Favorite Stop')
        verbose_name_plural = _('Favorite Stops')

    def __str__(self):
        return f"{self.user.username} → {self.stop.name}"
