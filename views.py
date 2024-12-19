from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import *
from .serializers import *
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .permissions import *
import requests


class NewsAPIView(APIView):

    def get(self, request):
        articles = News.objects.all()
        serializer = NewsSerializer(articles, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_staff:
            return Response({"error": "Only admins can create articles."}, status=status.HTTP_403_FORBIDDEN)
        serializer = NewsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        if not request.user.is_staff:
            return Response({"error": "Only admins can edit articles."}, status=status.HTTP_403_FORBIDDEN)

        article_id = request.data.get('id')
        if not article_id:
            return Response({"error": "Please provide 'id' of the article to edit."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            article = News.objects.get(id=article_id)
        except News.DoesNotExist:
            return Response({"error": "Article not found"}, status=status.HTTP_404_NOT_FOUND)


        serializer = NewsSerializer(article, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):

        if not request.user.is_staff:
            return Response({"error": "Only admins can delete articles."}, status=status.HTTP_403_FORBIDDEN)

        article_id = request.data.get('article_id')
        if not article_id:
            return Response({"error": "Please provide 'article_id' to delete"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            article = News.objects.get(id=article_id)
        except News.DoesNotExist:
            return Response({"error": "Article not found"}, status=status.HTTP_404_NOT_FOUND)

        article.delete()
        return Response({"message": "Article deleted successfully"}, status=status.HTTP_200_OK)


class SavedArticleList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        saved_articles = SavedArticle.objects.filter(user=request.user)
        serializer = SavedArticleSerializer(saved_articles, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SavedArticleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        news_id = request.data.get('news_id')
        if not news_id:
            return Response({"error": "Please provide 'news_id' to delete"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            saved_article = SavedArticle.objects.get(user=request.user,news_id=news_id)
        except SavedArticle.DoesNotExist:
            return Response({"error": "Saved article not found or unauthorized"}, status=status.HTTP_404_NOT_FOUND)

        saved_article.delete()
        return Response({"message": "Saved article removed successfully"}, status=status.HTTP_200_OK)


class CategoryListView(APIView):

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


    def post(self, request):
        if not request.user.is_staff:
            return Response({"error": "Only admins can create categories."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Category created successfully", "data": serializer.data},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        if not request.user.is_staff:
            return Response({"error": "Only admins can delete categories."}, status=status.HTTP_403_FORBIDDEN)
        category_id = request.data.get('id')

        if not category_id:
            return Response({"error": "Please provide 'id' to delete a category"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            category = Category.objects.get(id=category_id)  # Попытка найти категорию
            category.delete()
            return Response({"message": "Category deleted successfully"}, status=status.HTTP_200_OK)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        from django.contrib.auth import authenticate, login
        username = request.data.get('username')
        password = request.data.get('password')
        if username is None:
            return Response(data={'message': 'Field "username" is required!'}, status=status.HTTP_400_BAD_REQUEST)
        password = request.data.get('password')
        if password is None:
            return Response(data={'message': 'Field "password" is required!'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user is None:
            return Response(data={'message': 'Invalid username or password!'}, status=status.HTTP_400_BAD_REQUEST)

        login(request, user)
        return Response(data={'message': 'Login successful!'}, status=status.HTTP_200_OK)


class LogOutApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.contrib.auth import logout
        logout(request)
        return Response(data={'message': 'Logout successful!'}, status=status.HTTP_200_OK)


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user
        user_serializer = UserSerializer(user)
        saved_articles = SavedArticle.objects.filter(user=user)
        saved_articles_serializer = SavedArticleSerializer(saved_articles, many=True)

        return Response({
            "profile": user_serializer.data,
            "saved_articles": saved_articles_serializer.data,
        })

    def put(self, request):

        user = request.user
        data = request.data
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = data.get('email', user.email)
        user.save()
        return Response({"message": "Profile updated successfully", "profile": UserSerializer(user).data})

    def delete(self, request):

        user = request.user
        user.delete()
        return Response({"message": "Profile deleted successfully"}, status=status.HTTP_200_OK)



from rest_framework.pagination import PageNumberPagination
class PaginatedNewsApiView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        news = News.objects.all()
        paginator = PageNumberPagination()
        paginator.page_size = 3

        paginated_news = paginator.paginate_queryset(news, request)
        if not paginated_news:
            return Response(
                {'detail': 'We don’t have that many news updates :('}, status=status.HTTP_400_BAD_REQUEST)

        data = NewsSerializer(instance=paginated_news, many=True).data
        return Response(data=data, status=status.HTTP_200_OK)


class QuotesApiView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        url = "https://zenquotes.io/api/random"

        try:

            response = requests.get(url)

            if response.status_code == 200:
                quote_data = response.json()
                quote = quote_data[0]['q']
                author = quote_data[0]['a']
                return Response({"quote": quote, "author": author})
            else:
                return Response({"error": "Failed to get the quote. Please try again later"}, status=500)

        except requests.exceptions.RequestException as e:
            return Response({"error": f"Error while connecting to the API: {e}"}, status=500)


class SearchNewsApiView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        word = request.GET.get('search')
        if word is None:
            return Response(data={'message': 'Parameter "search" is required!'}, status=status.HTTP_400_BAD_REQUEST)
        news = News.objects.filter(content__icontains=word)
        data = NewsSerializer(instance=news, many=True).data
        return Response(data=data, status=status.HTTP_200_OK)


class OtherFilterAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        category = request.GET.get('category')
        author = request.GET.get('author')

        news = News.objects.all()

        if category:
            news = news.filter(category__name__icontains=category)

        if author:
            news = news.filter(author__name__icontains=author)

        data = NewsSerializer(news, many=True)
        return Response(data.data, status=status.HTTP_200_OK)


class NewsSortApiView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        sorting = request.GET.get('sorting')
        if sorting is None:
            news = News.objects.all()

        else:
            if sorting == 'date-asc':
                news = News.objects.all().order_by('published_date')
            elif sorting == 'date-desc':
                news = News.objects.all().order_by('-published_date')
        data = NewsSerializer(instance=news, many=True).data
        return Response(data=data, status=status.HTTP_200_OK)


class AdvertisementAPIView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):

        ads = Advertisement.objects.all()
        serializer = AdvertisementSerializer(ads, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):

        serializer = AdvertisementSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):

        ad_id = request.data.get("id")
        if not ad_id:
            return Response({"error": "Please provide 'id' of the advertisement to delete."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            ad = Advertisement.objects.get(id=ad_id)
            ad.delete()
            return Response({"message": "Advertisement deleted successfully."}, status=status.HTTP_200_OK)
        except Advertisement.DoesNotExist:
            return Response({"error": "Advertisement not found."}, status=status.HTTP_404_NOT_FOUND)