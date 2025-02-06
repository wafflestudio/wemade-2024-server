from django.db import models


# 본인 수정 가능한 Field: 업무성과, 자격증, 학력
class PersonCardInfo(models.Model):
    p_card_info = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'personCard_info'

#p_info: 공개정보(자격증 등), p_card_info(비공개/인사카드 정보)
class PersonalInfo(models.Model):
    main_phone_number = models.TextField(max_length=13, null=True)  # '010-0000-0000' 형태, 여러 개일 수 있음
    name = models.CharField(max_length=100, null=True)
    emails = models.JSONField()
    birthday = models.TextField(max_length=10, null=True) #2000-01-01 형태
    p_info = models.JSONField(null=True, blank=True)  # JSON 데이터를 저장할 필드
    p_card_info = models.OneToOneField(PersonCardInfo, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'personal_info'

class Person(models.Model):
    p_id = models.BigAutoField(primary_key=True) # p_id를 고유값으로 설정
    name = models.CharField(max_length=100)
    personal_info = models.OneToOneField(PersonalInfo, on_delete=models.SET_NULL, null=True)
    roles = models.JSONField(null=True)


    class Meta:
        db_table = 'person'
        app_label = 'person'
