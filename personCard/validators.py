from rest_framework import serializers
from personCard.models import PersonCardColumns


class PersonCardInfoValidator:
    """
    expected_public이 True이면 공개 정보, False이면 비공개 정보여야 합니다.
    각 컬럼에 대해 자료형 및 증빙자료 필요 여부를 검증합니다.
    """

    def __init__(self, expected_public):
        self.expected_public = expected_public

    def __call__(self, value):
        errors = {}
        # 모든 PersonCardColumns 정보를 가져와 사전으로 구성
        columns = PersonCardColumns.objects.all()
        column_map = {col.column_name: col for col in columns}

        for key, val in value.items():
            if key not in column_map:
                errors[key] = f"알 수 없는 컬럼입니다: {key}"
                continue
            col = column_map[key]

            # 공개/비공개 여부 검사
            if col.is_public != self.expected_public:
                errors[key] = f"이 컬럼은 {'공개' if col.is_public else '비공개'} 정보입니다. 적절한 필드에 입력하세요."

            # 자료형 검사
            if col.column_type == 'txt':
                if not isinstance(val, str) and not (isinstance(val, dict) and 'value' in val):
                    errors[key] = "텍스트 형식은 문자열 또는 'value' 키를 포함하는 객체여야 합니다."
            elif col.column_type in ['img', 'pdf']:
                if not isinstance(val, str) and not (isinstance(val, dict) and 'value' in val):
                    errors[key] = f"{col.get_column_type_display()} 형식은 문자열 또는 'value' 키를 포함하는 객체여야 합니다."

            # 증빙자료 필요 여부 검사: 해당 컬럼이 증빙자료가 필요한 경우, val은 dict여야 하며 'supporting_material' 키가 있어야 함.
            if col.is_supporting_material_required:
                if isinstance(val, dict):
                    if 'supporting_material' not in val or not val['supporting_material']:
                        errors[key] = "증빙자료가 필요한 컬럼입니다. 'supporting_material' 값을 제공하세요."
                else:
                    errors[key] = "증빙자료가 필요한 컬럼은 객체 형태로 입력되어야 합니다."

        if errors:
            raise serializers.ValidationError(errors)
        return value
