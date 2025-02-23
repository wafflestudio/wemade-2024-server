from django.db import models


class PersonCardColumns(models.Model):
    # 필요에 따라 다른 유형을 추가
    COLUMN_TYPE_CHOICES = (
        ('img', 'Image'),
        ('txt', 'Text'),
    )

    column_name = models.CharField(
        max_length=200,
        verbose_name="컬럼명"
    )
    column_type = models.CharField(
        max_length=10,
        choices=COLUMN_TYPE_CHOICES,
        verbose_name="자료형",  # 예: img, txt 등
        help_text="컬럼에 들어갈 자료의 유형을 지정합니다."
    )
    is_multiple = models.BooleanField(
        default=False,
        verbose_name="다중 값 허용",
        help_text="여러 개의 값이 입력될 수 있으면 True (예: 학력), 단일 값이면 False (예: 생일)"
    )
    is_supporting_material_required = models.BooleanField(
        default=False,
        verbose_name="증빙자료 필요 여부",
        help_text="해당 컬럼에 대해 증빙자료(첨부파일 등)가 필요한 경우 True"
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name="공개 정보 여부",
        help_text="모든 직원들이 검색해서 볼 수 있는 경우 True"
    )

    class Meta:
        db_table = 'person_card_columns'
        verbose_name = "Person Card Column"
        verbose_name_plural = "Person Card Columns"

    def __str__(self):
        return self.column_name
