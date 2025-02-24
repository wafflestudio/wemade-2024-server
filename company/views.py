from django.db.models import Subquery, OuterRef
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from .serializers import *
from .paginations import *
from rest_framework import status
import logging

logger = logging.getLogger(__name__)

# Corporation
class CorpListAPIView(ListAPIView):
    serializer_class = CorpListSerializer
    pagination_class = CorpListPagination

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if not name:
            return Corporation.objects.all()
        return Corporation.objects.filter(name__icontains=name)


class CorpDetailAPIView(RetrieveAPIView):
    serializer_class = CorpDetailSerializer
    queryset = Corporation.objects.all()
    lookup_field = 'c_id'

    def retrieve(self, request, *args, **kwargs):
        corporation = get_object_or_404(Corporation, c_id=kwargs.get('c_id'))
        return Response(self.get_serializer(corporation).data, status=200)


class CorpCreateAPIView(CreateAPIView):
    serializer_class = CorpCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CorpUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = CorpUpdateDeleteSerializer
    queryset = Corporation.objects.all()
    lookup_field = 'c_id'

    def retrieve(self, request, *args, **kwargs):
        corporation = get_object_or_404(Corporation, c_id=kwargs.get('c_id'))
        return Response(self.get_serializer(corporation).data, status=200)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=200)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=204)


# Team
class TeamListAPIView(ListAPIView):
    serializer_class = TeamListSerializer
    pagination_class = TeamListPagination

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if not name:
            return Team.objects.filter(is_active=True)
        return Team.objects.filter(name__icontains=name)


class TeamDetailAPIView(RetrieveAPIView):
    serializer_class = TeamDetailSerializer
    queryset = Team.objects.all()
    lookup_field = 't_id'

    def retrieve(self, request, *args, **kwargs):
        team = get_object_or_404(Team, t_id=kwargs.get('t_id'))
        return Response(self.get_serializer(team).data, status=200)


class TeamCreateAPIView(CreateAPIView):
    serializer_class = TeamCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TeamUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = TeamUpdateDeleteSerializer
    queryset = Team.objects.all()
    lookup_field = 't_id'

    def retrieve(self, request, *args, **kwargs):
        team = get_object_or_404(Team, t_id=kwargs.get('t_id'))
        return Response(self.get_serializer(team).data, status=200)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=200)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=204)

@receiver(post_save, sender=Corporation)
@receiver(post_save, sender=Team)
def update_name_history_on_save(sender, instance, **kwargs):
    if getattr(instance, '_disable_signal', False):
        return

    if instance.name_history is None:
        instance.name_history = []

    updated_name_history = instance.name_history + [{
        'name': instance.name,
        'commit_id': instance.last_commit.commit_id,
    }]
    instance.name_history = updated_name_history

    instance._disable_signal = True
    try:
        instance.save(update_fields=["name_history"])
    finally:
        instance._disable_signal = False

@receiver(m2m_changed, sender=Team.parent_teams.through)
def update_parent_team_history_on_m2m_change(sender, instance, action, **kwargs):
    if action != "post_add":
        return

    logger.critical(f"Parent team change detected for Team {instance.t_id}: {action}")

    parent_team_id = instance.parent_teams.first().t_id if instance.parent_teams.exists() else ""

    if instance.parent_team_history is None:
        instance.parent_team_history = []

    updated_parent_history = instance.parent_team_history + [{
        'parent_id': parent_team_id,
        'commit_id': instance.last_commit.commit_id,
    }]
    instance.parent_team_history = updated_parent_history

    logger.critical(f"Parent team history updated: {updated_parent_history}")

    instance._disable_signal = True
    try:
        instance.save(update_fields=["parent_team_history"])
    finally:
        instance._disable_signal = False



class TeamBatchProcessView(APIView):
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        if request.data.get('add_commit', True):
            new_commit = Commit.objects.create(
                commit_message=request.data.get('commit_message'),
                commit_author=request.user.person
            )
        else:
            new_commit = Commit.objects.last()
        new_commit.commit_content.extend(request.data.get('updates', []))
        new_commit.save()

        results = {"created": [], "updated": [], "deleted": []}
        errors = []

        for item in request.data.get('updates', []):
            t_id = item.get('t_id')
            request_type = item.get('request_type')

            try:
                if request_type == 'delete':
                    instance = Team.objects.get(t_id=t_id)
                    instance.is_active = False
                    instance.last_commit = new_commit
                    instance.save()
                    results["deleted"].append({"t_id": t_id})

                elif request_type == 'update':
                    instance = Team.objects.get(t_id=t_id)
                    serializer = TeamUpdateDeleteSerializer(
                        instance, data=item, partial=True
                    )
                    serializer.is_valid(raise_exception=True)
                    serializer.save(last_commit=new_commit)
                    results["updated"].append(serializer.data)

                elif request_type == 'create':
                    serializer = TeamCreateSerializer(data=item)
                    serializer.is_valid(raise_exception=True)
                    serializer.save(last_commit=new_commit)
                    results["created"].append(serializer.data)

                else:
                    raise ValidationError(f"Invalid request type: {request_type}")

            except Exception as e:
                errors.append({"item": item, "error": str(e)})

        return Response({"results": results, "errors": errors}, status=200)


class CorpBatchProcessView(APIView):
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        if request.data.get('add_commit', True):
            new_commit = Commit.objects.create(
                commit_message=request.data.get('commit_message'),
                commit_author=request.user.person
            )
        else:
            new_commit = Commit.objects.last()
        new_commit.commit_content.extend(request.data.get('updates', []))
        new_commit.save()

        results = {"created": [], "updated": [], "deleted": []}
        errors = []

        for item in request.data.get('updates', []):
            c_id = item.get('c_id')
            request_type = item.get('request_type')

            try:
                if request_type == 'delete':
                    instance = Corporation.objects.get(c_id=c_id)
                    instance.is_active = False
                    instance.last_commit = new_commit
                    instance.save()
                    results["deleted"].append({"c_id": c_id})

                elif request_type == 'update':
                    instance = Corporation.objects.get(c_id=c_id)
                    serializer = CorpUpdateDeleteSerializer(
                        instance, data=item, partial=True
                    )
                    serializer.is_valid(raise_exception=True)
                    serializer.save(last_commit=new_commit)
                    results["updated"].append(serializer.data)

                elif request_type == 'create':
                    serializer = CorpCreateSerializer(data=item)
                    serializer.is_valid(raise_exception=True)
                    serializer.save(last_commit=new_commit)
                    results["created"].append(serializer.data)

                else:
                    raise ValidationError(f"Invalid request type: {request_type}")

            except Exception as e:
                errors.append({"item": item, "error": str(e)})

        return Response({"results": results, "errors": errors, "commit_id": new_commit.commit_id}, status=200)

class GetCorpOfCommitView(APIView):
    def get(self, request, *args, **kwargs):
        target_corp_id = kwargs.get('c_id')
        target_commit_id = request.query_params.get('commit')
        teams = Team.objects.filter(corporation__c_id=target_corp_id)
        children = []

        for sub_team_candidate in teams:
            for d in sub_team_candidate.parent_team_history[::-1]:
                if d.get('commit_id') <= int(target_commit_id):
                    if  d.get('parent_id') == '':
                        children.append(sub_team_candidate.t_id)
                    break

        corporation = Corporation.objects.get(c_id=target_corp_id)
        serializer = CorpDetailSerializer(corporation)
        response_data = serializer.data.copy()

        for n in corporation.name_history:
            if n.get('commit_id') <= int(target_commit_id):
                response_data.update({"name": n.get('name')})
        response_data.update({"sub_teams": children})
        return Response(response_data, status=200)

class GetTeamOfCommitView(APIView):
    def get(self, request, *args, **kwargs):
        target_team_id = int(kwargs.get('t_id'))
        target_commit_id = int(request.query_params.get('commit'))

        teams = Team.objects.all()
        children = []

        for sub_team_candidate in teams:
            relevant_parent = next(
                (entry for entry in reversed(sub_team_candidate.parent_team_history)
                 if entry['commit_id'] <= target_commit_id),
                None
            )
            if relevant_parent and relevant_parent['parent_id'] == target_team_id:
                children.append(sub_team_candidate.t_id)

        team = Team.objects.get(t_id=target_team_id)
        serializer = TeamDetailSerializer(team)
        response_data = serializer.data.copy()

        latest_name = next(
            (entry for entry in reversed(team.name_history) if entry['commit_id'] <= target_commit_id),
            None
        )
        if latest_name:
            response_data['name'] = latest_name['name']

        response_data['sub_teams'] = children

        def fetch_parents(target_team, commit_id=target_commit_id):
            parent_teams = []
            current_team = target_team
            while True:
                parent_id = next(
                    (entry for entry in reversed(current_team.parent_team_history)
                     if entry['commit_id'] <= commit_id),
                    None
                )
                if parent_id == "" or parent_id is None: break

                parent_team = Team.objects.get(t_id=parent_id['parent_id'])
                parent_teams.append({
                    't_id': parent_team.t_id,
                    'name': next(
                        (entry for entry in reversed(parent_team.name_history) if entry['commit_id'] <= commit_id),
                        None
                    )['name'] if parent_team.name_history else parent_team.name,
                    'order': len(parent_teams),
                })
                current_team = parent_team

            return parent_teams

        response_data['parent_teams'] = fetch_parents(team, target_commit_id)

        return Response(response_data, status=200)




class CommitListAPIView(ListAPIView):
    serializer_class = CommitListSerializer
    pagination_class = CommitListPagination
    queryset = Commit.objects.all()