import os
import grpc
import restaurant_pb2
import restaurant_pb2_grpc


def _get_restaurant_url():
    try:
        url = getattr(config, 'RESTAURANT_GRPC_URL', None)
        if url:
            return url
    except Exception:
        pass

    return os.environ.get('RESTAURANT_GRPC_URL', 'restaurant_service:50051')


def get_restaurant_client():
    url = _get_restaurant_url()
    channel = grpc.insecure_channel(url)
    return restaurant_pb2_grpc.RestaurantServiceStub(channel)

def createQueryRequest(query: str):
    return restaurant_pb2.SearchRequest(query=query)
