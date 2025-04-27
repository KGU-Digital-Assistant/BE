from app.models import Item

def create_test_item(db, name="Test Item"):
    item = Item(name=name)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item