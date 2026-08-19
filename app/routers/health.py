from fastapi import APIRouter, status

router = APIRouter(tags=["health check"])

@router.get("/health")
def health_check():
    return {
        "status": status.HTTP_200_OK,
        "message": "Dịch vụ đang hoạt động bình thường"
    }