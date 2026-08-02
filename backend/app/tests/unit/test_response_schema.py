from app.schemas.response import ApiResponse, ErrorDetail


def test_ok_builds_success_envelope() -> None:
    response = ApiResponse[str].ok("hello", request_id="req-1")

    assert response.success is True
    assert response.data == "hello"
    assert response.error is None
    assert response.meta.request_id == "req-1"


def test_fail_builds_error_envelope() -> None:
    error = ErrorDetail(code="NOT_FOUND", message="missing")
    response = ApiResponse[None].fail(error, request_id="req-2")

    assert response.success is False
    assert response.data is None
    assert response.error is not None
    assert response.error.code == "NOT_FOUND"
    assert response.meta.request_id == "req-2"
