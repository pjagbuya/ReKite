"""
Script to add example deck and card for user 'asd'
"""
from database import SessionLocal
from models import User, Deck, Card, UserCardProgress
from datetime import datetime

db = SessionLocal()

try:
    # Find the user
    user = db.query(User).filter(User.username == "asd").first()
    
    if not user:
        print("User 'asd' not found. Creating user...")
        from auth_utils import get_password_hash
        
        user = User(
            username="asd",
            hashed_password=get_password_hash("123456")
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✓ Created user 'asd' with ID {user.id}")
    else:
        print(f"✓ Found user 'asd' with ID {user.id}")
    
    # Create a deck for examples
    deck = db.query(Deck).filter(
        Deck.user_id == user.id,
        Deck.name == "Art Terminology"
    ).first()
    
    if not deck:
        deck = Deck(
            user_id=user.id,
            name="Art Terminology",
            description="Key terms and definitions in art and design"
        )
        db.add(deck)
        db.commit()
        db.refresh(deck)
        print(f"✓ Created deck 'Art Terminology' with ID {deck.id}")
    else:
        print(f"✓ Using existing deck 'Art Terminology' with ID {deck.id}")
    
    # Add the card
    card = db.query(Card).filter(
        Card.deck_id == deck.id,
        Card.concept == "Practical Art"
    ).first()
    
    if not card:
        card = Card(
            deck_id=deck.id,
            concept="Practical Art",
            definition="concerned with the design and decoration of objects in practical use"
        )
        db.add(card)
        db.commit()
        db.refresh(card)
        print(f"✓ Created card 'Practical Art' with ID {card.id}")
    else:
        print(f"✓ Card 'Practical Art' already exists with ID {card.id}")
    
    # Initialize user card progress
    progress = db.query(UserCardProgress).filter(
        UserCardProgress.user_id == user.id,
        UserCardProgress.card_id == card.id
    ).first()
    
    if not progress:
        progress = UserCardProgress(
            user_id=user.id,
            card_id=card.id,
            ease_factor=2.5,
            interval=0,
            repetitions=0,
            next_review=datetime.utcnow()  # Available for review immediately
        )
        db.add(progress)
        db.commit()
        print(f"✓ Initialized progress tracking for card")
    else:
        print(f"✓ Progress tracking already exists")
    
    print("\n✅ All done! You can now:")
    print(f"   1. Login with username: asd, password: 123456")
    print(f"   2. View the 'Art Terminology' deck")
    print(f"   3. Study the 'Practical Art' card")
    
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
