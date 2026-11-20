from app.db.database import connection


class MemoryRepository:
    def list(self) -> list[dict]:
        with connection() as db:
            return [dict(row) for row in db.execute("SELECT * FROM memories ORDER BY updated_at DESC")]

    def get(self, identifier: str) -> dict | None:
        with connection() as db:
            row = db.execute("SELECT * FROM memories WHERE id = ?", (identifier,)).fetchone()
        return dict(row) if row else None

    def create(self, item: dict) -> dict:
        with connection() as db:
            db.execute("INSERT INTO memories(id,content,category,created_at,updated_at) VALUES(:id,:content,:category,:created_at,:updated_at)", item)
        return item

    def delete(self, identifier: str) -> bool:
        with connection() as db:
            cursor = db.execute("DELETE FROM memories WHERE id = ?", (identifier,))
        return cursor.rowcount > 0


memory_repository = MemoryRepository()
