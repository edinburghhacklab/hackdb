from django.db.models import Count
from django.http import JsonResponse

from rest_framework.views import APIView

from membership.models import Member


class MemberCount(APIView):
    # Override default permission classes, no auth token required.
    permission_classes = []

    def get(self, request, format=None):
        return JsonResponse(
            {
                "members": len([m for m in Member.objects.all() if m.is_member()]),
            }
        )


class MemberAdvancedCount(APIView):
    # Override default permission classes, no auth token required.
    permission_classes = []

    def get(self, request, format=None):
        membership_breakdown = {}
        annotated_statuses = Member.objects.values("membership_status").annotate(
            count=Count("membership_status")
        )

        for membership_status in annotated_statuses:
            status_type = membership_status["count"]
            count = membership_status["count"]

            for (
                membership_status_code,
                membership_status_name,
            ) in Member.MEMBERSHIP_STATUS_CHOICES:
                if membership_status_code == status_type:
                    status_type = membership_status_name

            membership_breakdown[status_type] = count
        return JsonResponse(membership_breakdown)
