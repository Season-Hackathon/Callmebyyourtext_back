from .models import Question, Comment
from login.serializers import PointSerializer
from .serializers import QuestionSerializer, QuestionDetailSerializer, CommentSerializer, CommentCreateSerializer, CommentLikeSerializer
from login.serializers import LoginSerializer
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status

from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from .permissions import IsOwnerOrReadOnly

#질문 CRUD
class QuestionViewSet(ModelViewSet):
    queryset = Question.objects.all().order_by('-created_at')
    serializer_class = QuestionSerializer
    #authentication_classes = [BasicAuthentication, SessionAuthentication]
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == "create":
            return QuestionSerializer
        if self.action == "list":
            return QuestionDetailSerializer
        if self.action == "retrieve":
            return QuestionDetailSerializer
        
        return QuestionSerializer

    def perform_create(self, serializer, **kwargs):
        if self.request.user.id == None:
            serializer.save(writer=self.request.user.id)
        else:
            serializer.save(writer = self.request.user)


#UserId별 질문 리스트
class QuestionListSet(ModelViewSet):
    queryset = Question.objects.all().order_by('-created_at')
    serializer_class = QuestionSerializer
    def get_queryset(self, **kwargs): # Override
        writer = self.kwargs['writer']
        return self.queryset.filter(writer=writer)
    def get_serializer_class(self):
        if self.action == "create":
            return CommentCreateSerializer
        

#답변 CRUD. create는 CommentCreateSerializer, 나머지는 CommentSerializer
class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    permission_classes = [IsOwnerOrReadOnly]
    
    def get_serializer_class(self): 
        writer = self.request.user
        if self.action == 'list':
            return CommentSerializer
        if self.action == 'retrieve':
            return CommentSerializer
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentCreateSerializer

    #답변 생성하면 포인트 +50                       -> 내 질문에 내가 답변하는거 막아야하나?
    def perform_create(self, serializer):
        if self.request.user.id == None:            # 로그인 안해도 답변 남길 수 있음
            serializer.save(writer=self.request.user.id)
        else:                                       # 로그인 유저는 답변 남기면 포인트 +50
            loginUser = self.request.user
            serializer.save(writer=self.request.user)
            loginUser.point += 50
            update_serial=PointSerializer(loginUser, data=self.request.data, partial=True)
            if update_serial.is_valid():
                update_serial.save()
        
    #답변 누르면 포인트 차감되는 로직
    def retrieve(self, request, pk=None, **kwargs):
        question_id = self.kwargs['question_id']
        question = get_object_or_404(Question, id=question_id)  # questionId로 해당 질문 받아옴
        print(question.writer.id)                               # 질문 작성자 ID
        if self.request.user.id != None:                        # 로그인 했을때
            comment = Comment.objects.all()
            comment = get_object_or_404(Comment, pk=pk)
            if comment.open_user.filter(id=request.user.id).exists():
                print('이미 열어본 답변')
                serializer=CommentSerializer(comment)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                print('처음 열어보는 답변')
                comment.open_user.add(request.user)
                loginUser = request.user
                if loginUser.id == question.writer.id:          # 질문 작성자와 로그인 유저가 같음 -> 내 질문 내가 보는거
                    loginUser.point -= 50
                else:                                           # 질문 작성자와 로그인 유저가 다름 -> 남 질문 내가 보기
                    print('-100')   
                    loginUser.point -= 100
                update_serial=PointSerializer(loginUser, data=request.data, partial=True)

                if update_serial.is_valid():
                    update_serial.save()
                    serializer=CommentSerializer(comment)

                return Response(serializer.data, status=status.HTTP_200_OK)
        #로그인 안했을때 어떻게 해야할지?!?!
        else:                                                    # 로그인 안했을때
            print('로그인후 이용해주세요')
            serializer=LoginSerializer()
        return Response(serializer.data, status=status.HTTP_401_UNAUTHORIZED)
        
    def get_queryset(self, **kwargs): # Override
        question_id = self.kwargs['question_id']
        return self.queryset.filter(questionId=question_id)


#답변 추천 로직
class CommentLikeViewSet(ModelViewSet):
    authentication_classes = [TokenAuthentication]          # 로그인 한 사람만 누를 수 있음
    queryset = Comment.objects.all()    
    serializer_class = CommentLikeSerializer

    def get_serializer_class(self): 
        if self.action == 'list':
            return CommentLikeSerializer
        
    def list(self, request, **kwargs):
        comment_id = self.kwargs['comment_id']
        comment = get_object_or_404(Comment, id=comment_id)
        serializer = CommentLikeSerializer(comment)

        if self.request.user.id != None:                        # 로그인 했을때
            comment = get_object_or_404(Comment, pk=comment_id)
            loginUser = self.request.user
            if comment.like_user.filter(id=self.request.user.id).exists():          # 이미 추천 누른 경우
                comment.like_user.remove(self.request.user)
                comment.like_count -= 1

            else:                                              # 추천 처음 누름
                if loginUser.id == comment.writer.id:          # 답변 작성자와 로그인 유저가 같음 -> 내 답변 내가 추천X
                    print('자기 답변 추천 금지')                
                else:                                          # 답변 작성자와 로그인 유저가 다름 -> 남 답변 내가 추천
                    comment.like_user.add(self.request.user)
                    comment.like_count += 1
                    
            update_serial=CommentLikeSerializer(comment, data=request.data, partial=True)
            if update_serial.is_valid():
                update_serial.save()
                serializer=CommentLikeSerializer(comment)

            return Response(serializer.data, status=status.HTTP_200_OK)
        
    def get_queryset(self, **kwargs): # Override
        comment_id = self.kwargs['comment_id']
        return self.queryset.filter(id=comment_id)