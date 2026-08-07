from rest_framework.permissions import BasePermission


def role_required(*roles):
    """
    Factory for a DRF permission class restricting access to the given
    roles. This is the authoritative RBAC check — the Next.js frontend also
    hides nav items per role, but that's UX only; this is what actually
    protects the data.
    """

    class RoleRequired(BasePermission):
        def has_permission(self, request, view):
            user = request.user
            return bool(
                user
                and user.is_authenticated
                and user.is_active
                and user.role in roles
            )

    RoleRequired.__name__ = f"RoleRequired[{','.join(roles)}]"
    return RoleRequired


IsAdmin = role_required("ADMIN")
IsAdminOrDoctor = role_required("ADMIN", "DOCTOR")
IsSchedulingRole = role_required("ADMIN", "DOCTOR", "NURSE", "RECORDS_OFFICER")
IsLabRole = role_required("ADMIN", "DOCTOR", "NURSE")
IsPharmacyRole = role_required("ADMIN", "PHARMACIST")
IsRecordsOrAdmin = role_required("RECORDS_OFFICER", "ADMIN")
