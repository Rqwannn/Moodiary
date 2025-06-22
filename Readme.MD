Fitur CRUD yang Tersedia:

1. Create Note

POST /notes/create - Membuat catatan baru
Validasi user exists
Auto-generate timestamps

2. Read Notes

GET /notes/get_all - Get semua notes dengan pagination
GET /notes/get_single/{note_id} - Get note by ID
GET /notes/user/{user_id} - Get notes by user
GET /notes/search - Search notes by title/content

3. Update Note

PUT /notes/update/{note_id} - Update note
Partial update (hanya field yang dikirim)
Auto-update updated_at

4. Delete Note

DELETE /notes/delete/{note_id} - Hapus note

Struktur File:

├── Controllers/
│   └── notes_controller.py     # CRUD operations

app/
├── DTOs/
│   └── notes_dto.py           # Data Transfer Objects
├── Models/
│   └── notes.py               # SQLModel definition
├── Database/
│   └── connection.py          # Database setup
└── main.py                    # Application entry point

Contoh Penggunaan:

Create Note:
bashPOST /notes/create
{
    "title": "My First Note",
    "content": "This is the content of my note",
    "id_user": 1
}

Search Notes:
bashGET /notes/search?q=first&user_id=1&limit=5

Update Note:
bashPUT /notes/update/1
{
    "title": "Updated Title"
}