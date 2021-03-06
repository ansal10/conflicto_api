import logging
import os

from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('conflicto')


class LoggerMiddleWare(MiddlewareMixin):

    def process_request(self, request):
        logger.info("URL : {}\nBODY : {}\nHTTP AUTHORIZATION : {}".format(request.path, request.body, request.META.get('HTTP_AUTHORIZATION', None)))
        return None

    def process_response(self, request, response):
        logger.info("\nResponse : {}\n\n".format(response.content))
        return response