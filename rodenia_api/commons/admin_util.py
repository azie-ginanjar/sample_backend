from rodenia_api.commons.rq_utils import get_failed_jobs_by_index
from rodenia_api.commons.schemas import UserSchema
from rodenia_api.models import User


def get_user_summary(user_id):
    user = User.get(user_id)
    failed_jobs_by_seller_id = get_failed_jobs_by_index("seller_id")
    failed_jobs_by_username = get_failed_jobs_by_index("username")

    return {
        "user_dump": UserSchema().dump(user).data,
        "failed_jobs_by_seller_id": failed_jobs_by_seller_id.get(user.seller_id, []),
        "failed_jobs_by_username": failed_jobs_by_username.get(user.username, []),
    }
