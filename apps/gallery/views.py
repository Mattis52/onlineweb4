# -*- coding: utf-8 -*-

import logging
import os

from django.db.models import Q
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse, HttpResponse

from guardian.decorators import permission_required
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny
from taggit.utils import parse_tags

from apps.gallery.util import UploadImageHandler, ResponsiveImageHandler
from apps.gallery.models import UnhandledImage, ResponsiveImage
from apps.gallery.forms import DocumentForm
from apps.gallery.serializers import ResponsiveImageSerializer


def _create_request_dictionary():

    dictionary = {
        'unhandled_images': UnhandledImage.objects.all(),
        'responsive_images': ResponsiveImage.objects.all(),
    }

    return dictionary


@login_required
@permission_required('gallery.view_responsiveimage')
def all_images(request):
    """
    Returns a rendered view that displays all images
    uploaded through the gallery app
    """

    template = 'gallery/list.html'
    images = ResponsiveImage.objects.all()

    return render(request, template, {'images': images})


@login_required
@permission_required('gallery.add_responsiveimage')
def upload(request):

    log = logging.getLogger(__name__)

    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            log.info('%s uploaded image "%s"' % (request.user, os.path.abspath(str(request.FILES['file']))))

            # Check if we successfully generate an UnhandledImage object
            result = UploadImageHandler(request.FILES['file']).status
            if not result:
                return JsonResponse({'success': False, 'message': result.message}, status=500)

            # Return OK if all good
            return JsonResponse({'success': True, 'message': 'OK'}, status=200)

    return JsonResponse({'success': False, 'message': 'Bad request or invalid type.'}, status=400)


@login_required
@permission_required('gallery.add_responsiveimage')
def number_of_untreated(request):
    if request.is_ajax():
        if request.method == 'GET':
            return JsonResponse(data={'untreated': UnhandledImage.objects.all().count()}, status=200)
    return JsonResponse({}, status=405)


@login_required
@permission_required('gallery.add_responsiveimage')
def get_all_untreated(request):
    if request.is_ajax():
        if request.method == 'GET':

            images = []

            for image in UnhandledImage.objects.all():
                images.append({
                    'id': image.id,
                    'thumbnail': image.thumbnail.url,
                    'image': image.image.url
                })

            return JsonResponse({'untreated': images}, status=200)
    return JsonResponse({}, status=405)


# Same here, delete all files if something goes wrong, not yet handled
@login_required
@permission_required('gallery.add_responsiveimage')
def crop_image(request):

    log = logging.getLogger(__name__)

    if request.is_ajax():
        if request.method == 'POST':
            crop_data = request.POST

            # Check that the image ID exists
            image = get_object_or_404(UnhandledImage, pk=crop_data['id'])

            # Fetch values from Django's immutable MultiValueDict
            config = {key: crop_data.get(key) for key in crop_data.keys()}
            config['preset'] = 'article'

            # Construct a responsive image handler and configure it using the provided request data
            handler = ResponsiveImageHandler(image)
            status = handler.configure(config)
            if not status:
                return HttpResponse(status.message, status=400)

            # Generate the responsive versions based on the provided request data
            status = handler.generate()
            if not status:
                return HttpResponse(status.message, status=500)

            # Add Taggit tags if provided
            resp_image = status.data
            tags = crop_data.get('tags')
            if tags:
                resp_image.tags.add(*parse_tags(tags))

            # Log who performed the crop operation
            log.info(
                '%s cropped and saved ResponsiveImage %d (%s)' % (
                    request.user,
                    resp_image.id,
                    config.get('name')
                )
            )

            return JsonResponse(data={'name': config['name'], 'id': resp_image.id})

    return HttpResponse(status=405)


@login_required
@permission_required('gallery.view_responsiveimage')
def search(request):
    """
    Performs a search request and returns a JSON response
    :param request: Django Request object
    :return: JsonResponse
    """

    if request.method != 'GET' or 'query' not in request.GET:
        return JsonResponse(status=400, data={'error': 'Bad Request', 'status': 400})

    query = request.GET['query']

    # Field filters are normally AND'ed together. Q objects circumvent this, treating each field result like a set.
    # This allows us to use set operators like | (union), & (intersect) and ~ (negation)
    matches = ResponsiveImage.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(tags__name__in=query.split(' '))
    ).distinct()[:15]

    results = {
        'total': len(matches),
        'images': [{
            'name': image.name,
            'description': image.description,
            'id': image.id,
            'photographer': image.photographer,
            'original': settings.MEDIA_URL + str(image.image_original),
            'thumbnail': settings.MEDIA_URL + str(image.thumbnail),
            'wide': settings.MEDIA_URL + str(image.image_wide),
            'xs': settings.MEDIA_URL + str(image.image_xs),
            'sm': settings.MEDIA_URL + str(image.image_sm),
            'md': settings.MEDIA_URL + str(image.image_md),
            'lg': settings.MEDIA_URL + str(image.image_lg),
            'timestamp': image.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'tags': [str(tag) for tag in image.tags.all()]
        } for image in matches]
    }

    return JsonResponse(data=results, status=200, safe=False)


# REST Framework

class ResponsiveImageViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin, mixins.ListModelMixin):
    """
    Image viewset. Can be filtered on 'year', 'month', and free text search using 'query'.

    The 'query' filter performs a case-insensitive OR match on either image name or description.
    """

    queryset = ResponsiveImage.objects.filter().order_by('-timestamp')
    serializer_class = ResponsiveImageSerializer
    permission_classes = (AllowAny,)
    filter_fields = ('id', 'name', 'timestamp')

    def get_queryset(self):
        queryset = self.queryset
        month = self.request.query_params.get('month', None)
        year = self.request.query_params.get('year', None)
        query = self.request.query_params.get('query', None)

        if year:
            if month:
                # Filtering on year and month
                queryset = queryset.filter(
                    timestamp__year=year,
                    timestamp__month=month,
                ).order_by('-timestamp')
            else:
                # Filtering only on year
                queryset = queryset.filter(
                    timestamp__year=year,
                ).order_by('-timestamp')

        if query:
            # Restrict results based off of search
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(tags__name__in=query.split())
            ).distinct()

        return queryset
