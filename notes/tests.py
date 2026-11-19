from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Note


class NoteApiTests(APITestCase):
    def setUp(self):
        self.note = Note.objects.create(title="Shopping", content="Milk and bread")
        self.list_url = reverse("note-list")
        self.detail_url = reverse("note-detail", args=[self.note.id])

    def test_create_note(self):
        payload = {
            "title": "New note",
            "content": "Some text",
            "marked": False,
            "trash": False,
        }

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Note.objects.count(), 2)
        created = Note.objects.get(id=response.data["id"])
        self.assertEqual(created.title, "New note")
        self.assertEqual(created.content, "Some text")

    def test_create_note_with_empty_content(self):
        payload = {"title": "Only a title", "content": "", "marked": False, "trash": False}

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["content"], "")

    def test_create_note_ignores_client_supplied_id(self):
        payload = {"id": 999, "title": "Title", "content": "Text"}

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data["id"], 999)

    def test_list_notes(self):
        Note.objects.create(title="Second", content="Another note")

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual([note["title"] for note in response.data], ["Shopping", "Second"])

    def test_list_response_is_plain_json_array_of_notes(self):
        response = self.client.get(self.list_url)

        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(
            data[0],
            {
                "id": self.note.id,
                "title": "Shopping",
                "content": "Milk and bread",
                "marked": False,
                "trash": False,
            },
        )

    def test_retrieve_note(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.note.id)
        self.assertEqual(response.data["title"], "Shopping")

    def test_retrieve_nonexistent_note_returns_404(self):
        response = self.client.get(reverse("note-detail", args=[9999]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_note_with_put(self):
        # Angular sends the complete note object, including its id.
        payload = {
            "id": self.note.id,
            "title": "Updated title",
            "content": "Updated content",
            "marked": True,
            "trash": False,
        }

        response = self.client.put(self.detail_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, "Updated title")
        self.assertEqual(self.note.content, "Updated content")
        self.assertTrue(self.note.marked)

    def test_update_note_with_patch(self):
        response = self.client.patch(self.detail_url, {"title": "Patched"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, "Patched")
        self.assertEqual(self.note.content, "Milk and bread")

    def test_mark_note(self):
        response = self.client.patch(self.detail_url, {"marked": True}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIs(response.data["marked"], True)
        self.note.refresh_from_db()
        self.assertTrue(self.note.marked)

    def test_unmark_note(self):
        self.note.marked = True
        self.note.save()

        response = self.client.patch(self.detail_url, {"marked": False}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIs(response.data["marked"], False)
        self.note.refresh_from_db()
        self.assertFalse(self.note.marked)

    def test_move_note_to_trash_keeps_it_in_database(self):
        response = self.client.patch(self.detail_url, {"trash": True}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.note.refresh_from_db()
        self.assertTrue(self.note.trash)
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())

    def test_restore_note_from_trash(self):
        self.note.trash = True
        self.note.save()

        response = self.client.patch(self.detail_url, {"trash": False}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.note.refresh_from_db()
        self.assertFalse(self.note.trash)

    def test_delete_note_removes_it_permanently(self):
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())

    def test_delete_nonexistent_note_returns_404(self):
        response = self.client.delete(reverse("note-detail", args=[9999]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_create_note_without_title_is_rejected(self):
        response = self.client.post(self.list_url, {"content": "No title"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)
        self.assertEqual(Note.objects.count(), 1)

    def test_create_note_with_blank_title_is_rejected(self):
        response = self.client.post(self.list_url, {"title": "", "content": "Text"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

    def test_create_note_without_content_is_rejected(self):
        response = self.client.post(self.list_url, {"title": "Title"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("content", response.data)

    def test_create_note_with_too_long_title_is_rejected(self):
        payload = {"title": "x" * 256, "content": "Text"}

        response = self.client.post(self.list_url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", response.data)

    def test_invalid_boolean_value_is_rejected(self):
        response = self.client.patch(self.detail_url, {"marked": "maybe"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("marked", response.data)

    def test_cors_allows_angular_dev_server(self):
        response = self.client.get(self.list_url, HTTP_ORIGIN="http://localhost:4200")

        self.assertEqual(
            response.headers.get("Access-Control-Allow-Origin"), "http://localhost:4200"
        )

    def test_cors_rejects_unknown_origin(self):
        response = self.client.get(self.list_url, HTTP_ORIGIN="http://evil.example.com")

        self.assertNotIn("Access-Control-Allow-Origin", response.headers)
