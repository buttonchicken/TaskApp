from Accounts.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from rest_framework import status
from .serializers import *
from .models import Task
from django.core.exceptions import ObjectDoesNotExist
import json
from django.db.models import Case, When, Value, IntegerField
from .config import *
from datetime import datetime


class CreateTask(APIView):
    '''
    Api to create a task with the given parameters
    Payload:
    Required params - name, description
    Optional params - task_type, task_status
    Constraint - The user must be registered and have a valid JWT to create a task
    '''
    authentication_classes = [JWTAuthentication]
    def post(self,request):
        try:
            task_obj = Task()
            task_obj.created_by = request.user
            assigned_to = request.data.get('assigned_to','[]')
            username_list = json.loads(assigned_to)
            name = request.data['name']
            description = request.data['description']
            task_type = request.data.get('task_type', 'RED')
            task_status = request.data.get('task_status', 'TODO')
            task_obj = Task.objects.create(created_by = request.user, name = name,description = description,
                                           task_type = task_type, task_status = task_status)
            if assigned_to!='[]':
                users_to_assign = User.objects.filter(username__in=username_list)
                task_obj.assigned_to.add(users_to_assign)
                task_obj.save()
            serializer = TaskSerializer(task_obj)
            return Response({"Success":True, "message":"Task created successfully","task":serializer.data},status = status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"Success": False, "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"Success": False, "message": f"Error updating task: {e}"}, status=status.HTTP_400_BAD_REQUEST)

class EditTask(APIView):
    '''
    Api to edit a task with the given parameters
    Payload:
    Optional params - task_type, task_status, name, description (if the user is editing a task created by him/her)
    Constraint - The user must be registered and have a valid JWT to edit a task. Also to edit the status and type the
    user first must be assigned the task
    Returns - The updated task data
    '''
    authentication_classes = [JWTAuthentication]
    def put(self, request):
        try:
            task_id = request.data.get('task_id',None)
            task_obj = Task.objects.get(task_id=task_id)
            task_created_by_user = (task_obj.created_by==request.user)
            name = request.data.get('name',None)
            description = request.data.get('description',None)
            task_status = request.data.get('task_status',None)
            task_type = request.data.get('task_type',None)
            task_type_set = {item[0] for item in TASK_TYPE}
            task_status_set = {item[0] for item in TASK_STATUS}
            
            if task_created_by_user:
                if name:
                    task_obj.name = name
                if description:
                    task_obj.description = description
                task_obj.save()
            else:
                if name or description:
                    return Response({"Success": False, "message": "Task name and description can only be changed by the user who created it !!"},
                    status=status.HTTP_403_FORBIDDEN)
            
            if task_status and request.user in task_obj.assigned_to.all(): #status of a task can only be changed by the user who is assigned to it
                if task_status.upper() in task_status_set:
                    task_obj.task_status = task_status
                    if task_status.upper()=="COMPLETED":
                        completed_at_str = str(timezone.now())
                        task_obj.completed_at = datetime.fromisoformat(completed_at_str) #setting the completed at to the time when the user marks the task as completed
                else:
                    return Response({"Success": False, "message": "Task Status can only be TODO, IN PROGRESS or COMPLETED"}, status=status.HTTP_404_NOT_FOUND)
            elif task_status and request.user not in task_obj.assigned_to.all():
                return Response({"Success": False, "message": "Task needs to be assigned to the user to change the status"}, status=status.HTTP_403_FORBIDDEN)
            
            if task_type and request.user in task_obj.assigned_to.all(): #type of a task can only be changed by the user who is assigned to it
                if task_type.upper() in task_type_set:
                    task_obj.task_type = task_type
                else:
                    return Response({"Success": False, "message": "Task type can only be RED,BLUE or GREY and needs to be assigned to the user"}, status=status.HTTP_404_NOT_FOUND)
            elif task_type and request.user not in task_obj.assigned_to.all():
                return Response({"Success": False, "message": "Task needs to be assigned to the user to change the type"}, status=status.HTTP_403_FORBIDDEN)
            
            task_obj.save()
            serializer = TaskSerializer(task_obj)
            return Response({"Success": True, "message": "Task updated successfully", "task": serializer.data}, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({"Success": False, "message": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"Success": False, "message": f"Error updating task: {e}"}, status=status.HTTP_400_BAD_REQUEST)

class AssignTask(APIView):
    '''
    Api to assign a task to the user
    Required params - task_id, assign_to (A list of users like ["user1","user2"...])
    Constraint - The user must be registered and have a valid JWT to assign a task
    '''
    authentication_classes = [JWTAuthentication]
    def post(self,request):
        try:
            task_id = request.data['task_id']
            assign_to = request.data['assign_to']
            if len(assign_to)>0:
                users_to_assign = User.objects.filter(username__in=assign_to)
                task_obj = Task.objects.get(task_id=task_id)
                already_assigned_users = task_obj.assigned_to.all()
                already_assigned_usernames = [user.username for user in already_assigned_users]
                new_users_to_assign = []
                for user in users_to_assign:
                    if user.username not in already_assigned_usernames:
                        new_users_to_assign.append(user)
                if new_users_to_assign:
                    task_obj.assigned_to.add(*new_users_to_assign)
                    task_obj.save()
                elif len(new_users_to_assign) == 0:
                    return Response({"Success":False, "message":"User already assigned the task"},status=status.HTTP_400_BAD_REQUEST)
                return Response({"Success":True, "message":"Task assigned successfully"},status = status.HTTP_200_OK)
            else:
                return Response({"Success":False, "message":"Please enter usernames to assign"},status=status.HTTP_400_BAD_REQUEST)
        except Task.DoesNotExist:
            return Response({"Success": False, "message": "Task not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"Success": False, "message": f"Error updating task: {e}"}, status=status.HTTP_400_BAD_REQUEST)

class UnassignTask(APIView):
    '''
    Api to unassign a task to the user
    Required params - task_id, users_to_remove (A list of users like ["user1","user2"...])
    Constraint - The user must be registered and have a valid JWT to unassign a task
    '''
    authentication_classes = [JWTAuthentication]
    def post(self,request):
        try:
            task_id = request.data['task_id']
            task_obj = Task.objects.get(task_id=task_id)
            already_assigned_users = task_obj.assigned_to.all()
            users_to_remove = request.data['users_to_remove']
            if len(users_to_remove)>0:
                users_to_remove = User.objects.filter(username__in=users_to_remove)
                users_to_remove = [x for x in users_to_remove if x in already_assigned_users]
                print(users_to_remove)
                if len(users_to_remove)==0:
                    return Response({"Success":False, "message":"Task not assigned to the user"},status=status.HTTP_400_BAD_REQUEST)
                task_obj.assigned_to.remove(*users_to_remove)
                task_obj.save()
                return Response({"Success":True, "message":"Task unassigned from the user"},status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"Success":False, "message":"Task not found"},status=status.HTTP_400_BAD_REQUEST)

class UserTasks(APIView):
    '''
    Api to fetch all tasks assigned to a user
    Required params - task_id, assign_to (A list of users like ["user1","user2"...])
    Constraint - The user must be registered and have a valid JWT to unassign a task
    Returns - A list of tasks for the user sorted by task_type (priority) and then task_status
    '''
    authentication_classes = [JWTAuthentication]
    def get(self, request):
        try:
            username = request.data.get('username',None)
            user = User.objects.get(username=username)
            task_type_ordering = Case(
                When(task_type='RED', then=Value(1)),
                When(task_type='BLUE', then=Value(2)),
                When(task_type='GREY', then=Value(3)),
                output_field=IntegerField()
            )
            task_status_ordering = Case(
                When(task_status='TODO', then=Value(1)),
                When(task_status='IN PROGRESS', then=Value(2)),
                When(task_status='COMPLETED', then=Value(3)),
                output_field=IntegerField()
            )
            tasks = Task.objects.filter(assigned_to=user).order_by(task_type_ordering,task_status_ordering)
            serializer = TaskSerializer(tasks, many=True)
            return Response({"Success":True,  "message": serializer.data}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"Success":False, "message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"Success":False, "message":"Task not found"},status=status.HTTP_400_BAD_REQUEST)
