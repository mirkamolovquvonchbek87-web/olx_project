from apps.models import Region

def regions_processor(request):
    return {
        'regions': Region.objects.all().prefetch_related('districts')
    }
