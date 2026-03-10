from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.decorators import display
from django.utils.html import format_html
from .models import Route, Stop, RouteStop, Vehicle, VehicleLocation, FavoriteRoute, FavoriteStop


class RouteStopInline(TabularInline):
    model = RouteStop
    extra = 0
    fields = ('stop', 'order', 'distance_from_previous', 'travel_time_from_previous')
    ordering = ['order']


class VehicleInline(TabularInline):
    model = Vehicle
    extra = 0
    fields = ('plate_number', 'vehicle_type', 'status', 'is_active')
    show_change_link = True


@admin.register(Route)
class RouteAdmin(ModelAdmin):
    list_display = ('number', 'name', 'route_type', 'show_color', 'frequency_minutes', 'operating_hours', 'is_active')
    list_filter = ('route_type', 'is_active')
    search_fields = ('number', 'name')
    list_editable = ('is_active',)
    inlines = [RouteStopInline, VehicleInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('number', 'name', 'route_type', 'description', 'is_active'),
        }),
        ('Display', {
            'fields': ('color',),
        }),
        ('Schedule', {
            'fields': ('frequency_minutes', 'operating_hours'),
        }),
    )

    @display(description='Color', ordering='color')
    def show_color(self, obj):
        return format_html(
            '<span style="display:inline-block;width:20px;height:20px;background:{};border-radius:3px;"></span> {}',
            obj.color, obj.color
        )


@admin.register(Stop)
class StopAdmin(ModelAdmin):
    list_display = ('name', 'code', 'address', 'latitude', 'longitude', 'has_shelter', 'is_active')
    list_filter = ('is_active', 'has_shelter')
    search_fields = ('name', 'name_az', 'code', 'address')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'name_az', 'code', 'address', 'is_active', 'has_shelter'),
        }),
        ('Location', {
            'fields': ('latitude', 'longitude'),
        }),
    )


class VehicleLocationInline(StackedInline):
    model = VehicleLocation
    extra = 0
    fields = ('latitude', 'longitude', 'speed', 'heading', 'timestamp')
    readonly_fields = ('timestamp',)


@admin.register(Vehicle)
class VehicleAdmin(ModelAdmin):
    list_display = ('plate_number', 'route', 'vehicle_type', 'capacity', 'status', 'is_active')
    list_filter = ('status', 'is_active', 'vehicle_type', 'route')
    search_fields = ('plate_number', 'route__number')
    list_editable = ('status', 'is_active')
    inlines = [VehicleLocationInline]
    fieldsets = (
        ('Vehicle Info', {
            'fields': ('plate_number', 'vehicle_type', 'capacity'),
        }),
        ('Assignment', {
            'fields': ('route', 'status', 'is_active'),
        }),
    )


@admin.register(VehicleLocation)
class VehicleLocationAdmin(ModelAdmin):
    list_display = ('vehicle', 'get_route', 'latitude', 'longitude', 'speed', 'timestamp')
    list_filter = ('vehicle__route',)
    search_fields = ('vehicle__plate_number', 'vehicle__route__number')
    readonly_fields = ('timestamp',)

    @display(description='Route')
    def get_route(self, obj):
        if obj.vehicle.route:
            return f"Route {obj.vehicle.route.number}"
        return "—"


@admin.register(RouteStop)
class RouteStopAdmin(ModelAdmin):
    list_display = ('route', 'stop', 'order', 'distance_from_previous', 'travel_time_from_previous')
    list_filter = ('route',)
    search_fields = ('route__number', 'stop__name')
    ordering = ['route', 'order']


@admin.register(FavoriteRoute)
class FavoriteRouteAdmin(ModelAdmin):
    list_display = ('user', 'route', 'created_at')
    list_filter = ('route',)
    search_fields = ('user__username', 'route__number')


@admin.register(FavoriteStop)
class FavoriteStopAdmin(ModelAdmin):
    list_display = ('user', 'stop', 'created_at')
    search_fields = ('user__username', 'stop__name')
