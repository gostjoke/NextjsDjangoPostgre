"""
測試用 API: 發送訊息到 RabbitMQ
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .producer import publish


@api_view(['POST'])
def publish_message(request):
    """
    POST body 範例:
    {
        "queue": "send_email",
        "payload": {"to": "a@b.com", "subject": "hi"}
    }
    """
    queue = request.data.get('queue')
    payload = request.data.get('payload', {})

    if not queue:
        return Response(
            {'error': 'queue is required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        publish(queue, payload)
        return Response({'ok': True, 'queue': queue, 'payload': payload})
    except Exception as e:
        return Response(
            {'ok': False, 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
