import json
from app.db.database import connection


class AssignmentRepository:
    def list(self) -> list[dict]:
        with connection() as db:
            rows = db.execute("SELECT * FROM assignments ORDER BY created_at DESC").fetchall()
        return [self._deserialize(row) for row in rows]

    def get(self, identifier: str) -> dict | None:
        with connection() as db:
            row = db.execute("SELECT * FROM assignments WHERE id = ?", (identifier,)).fetchone()
        return self._deserialize(row) if row else None

    def create(self, item: dict) -> dict:
        with connection() as db:
            db.execute("""INSERT INTO assignments(id,title,description,course,due_date,status,created_at,attachment_names,extracted_text)
            VALUES(:id,:title,:description,:course,:due_date,:status,:created_at,:attachment_names,:extracted_text)""",
            {**item, "attachment_names": json.dumps(item["attachment_names"], ensure_ascii=False)})
        return item

    def update_documents(self, identifier: str, names: list[str], extracted_text: str) -> bool:
        with connection() as db:
            cursor = db.execute("UPDATE assignments SET attachment_names = ?, extracted_text = ? WHERE id = ?",
                (json.dumps(names, ensure_ascii=False), extracted_text, identifier))
        return cursor.rowcount > 0

    @staticmethod
    def _deserialize(row) -> dict:
        item = dict(row)
        item["attachment_names"] = json.loads(item["attachment_names"])
        return item


assignment_repository = AssignmentRepository()
