from django.urls import path
from .views import *

urlpatterns = [
    # ----- 조직도 관련 -----
    # Edit mode
    path("edit/", EditListAPIView.as_view(), name="edit-list"),
    # Subteam들 정보 불러오기
    path("edit/team/<int:t_id>/", TeamEditListAPIView.as_view(), name="team-edit-list"),
    # Corporation 정보 업데이트 - 조직 이동/비활성화 (Master)
    path(
        "edit/corp/<int:c_id>/update/", CorpUpdateAPIView.as_view(), name="corp-update"
    ),
    # Team 정보 업데이트(1) - 조직 이동/비활성화 (Master/HR Team)
    path(
        "edit/team/<int:t_id>/update/",
        TeamUpdateAPIView.as_view(),
        name="team-update",
    ),
    # 조직도 임시저장
    path("edit/draft/", EditDraftAPIView.as_view(), name="edit-draft"),
    # 조직도 임시저장 삭제
    path(
        "edit/draft/delete/<int:d_id>",
        EditDraftDeleteAPIView.as_view(),
        name="edit-draft-delete",
    ),
    # Commit Restore
    path(
        "restore/corp/<int:commit_id>/<int:c_id>/",
        CorpRestoreView.as_view(),
        name="corp-restore",
    ),
    path(
        "restore/team/<int:commit_id>/<int:t_id>/",
        TeamRestoreView.as_view(),
        name="team-restore",
    ),
    path("commit/list/", CompanyCommitListView.as_view(), name="commit-list"),
    path("commit/latest/", CurrentCommitView.as_view(), name="commit-latest"),
    path(
        "commit/<int:commit_id>/",
        CompanyCommitUpdateView.as_view(),
        name="commit-update",
    ),
    path(
        "commit/compare/",
        CompanyCommitCompareListView.as_view(),
        name="commit-compare",
    ),
    # ----- 인사이동 관련 -----
    # Role
    # 특정한 사람의 role 조회 (supervisor 변경 포함)
    path("roles/<int:p_id>/", RoleListDetailAPIView.as_view(), name="role-get"),
    # 특정한 사람의 role 생성 (부서 이동/발령)
    path("roles/<int:p_id>/create/", RoleCreateAPIView.as_view(), name="role-create"),
    # 특정한 사람의 role 변경 (직급 변경)
    path(
        "roles/<int:p_id>/update/<int:r_id>/",
        RoleUpdateAPIView.as_view(),
        name="role-update",
    ),
    # ----- 추가 기능 (MasterHR) -----
    # Corporation
    # 새로운 Corporation 생성
    path("corp/create/", CorpCreateAPIView.as_view(), name="corp-create"),
    # 모든 Corporation List
    path("corp/list/", CorpListAPIView.as_view(), name="corp-list"),
    # 특정 Corporation의 정보 조회
    path("corp/<int:c_id>/", CorpDetailAPIView.as_view(), name="corp-detail"),
    # Corporation 삭제
    path("corp/<int:c_id>/delete/", CorpDeleteAPIView.as_view(), name="corp-delete"),
    # Team
    # 새로운 Team 생성
    path("team/create/", TeamCreateAPIView.as_view(), name="team-create"),
    # 모든 Team List
    path("team/list/", TeamListAPIView.as_view(), name="team-list"),
    # 특정 Team의 정보 조회
    path("team/<int:t_id>/", TeamDetailAPIView.as_view(), name="team-detail"),
    # Team 삭제
    path("team/<int:t_id>/delete/", TeamDeleteAPIView.as_view(), name="team-delete"),
    # Role
    # Role 삭제
    path(
        "roles/<int:p_id>/delete/<int:r_id>/",
        RoleDeleteAPIView.as_view(),
        name="role-delete",
    ),
    # 미분류 그룹
    path(
        "unclassified/list/",
        UnclassifiedListAPIView.as_view(),
        name="unclassified-list",
    ),
]
