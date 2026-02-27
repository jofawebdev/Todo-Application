from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Todo

class TodoSearchPaginationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        # Create sample todos
        for i in range(15):
            Todo.objects.create(
                user=self.user,
                title=f'Task {i}',
                description=f'Description {i}',
                priority=(i % 5) + 1,
                completed=(i % 2 == 0)
            )

    def test_search_by_title(self):
        response = self.client.get(reverse('todos:todo_list'), {'q': 'Task 1'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Task 1')
        self.assertNotContains(response, 'Task 2')

    def test_search_by_description(self):
        response = self.client.get(reverse('todos:todo_list'), {'q': 'Description 5'})
        self.assertContains(response, 'Description 5')

    def test_search_by_priority_number(self):
        # Search for priority 3 tasks
        response = self.client.get(reverse('todos:todo_list'), {'q': '3'})
        # Should include tasks with priority=3 OR title/description containing '3'
        # For simplicity, check that at least one priority=3 task is present
        todos_in_context = response.context['todos']
        self.assertTrue(any(t.priority == 3 for t in todos_in_context))

    def test_search_case_insensitive(self):
        response = self.client.get(reverse('todos:todo_list'), {'q': 'task 1'})
        self.assertContains(response, 'Task 1')

    def test_search_with_filters(self):
        # Search + status filter
        response = self.client.get(reverse('todos:todo_list'), {'q': 'Task', 'status': 'active'})
        todos = response.context['todos']
        self.assertTrue(all(not t.completed for t in todos))
        self.assertTrue(any('Task' in t.title for t in todos))

    def test_pagination(self):
        response = self.client.get(reverse('todos:todo_list'), {'page': 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['todos']), 10)  # paginate_by=10

        response = self.client.get(reverse('todos:todo_list'), {'page': 2})
        self.assertEqual(len(response.context['todos']), 5)   # remaining 5

    def test_pagination_preserves_query(self):
        response = self.client.get(reverse('todos:todo_list'), {'q': 'Task', 'status': 'active', 'page': 2})
        # Check that pagination links contain the query parameters
        self.assertContains(response, '?q=Task&amp;status=active&amp;page=1')
        self.assertContains(response, '?q=Task&amp;status=active&amp;page=3')