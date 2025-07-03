from app import db
from app.models import Paper
from datetime import datetime
from app import create_app

# Initialize the app
app = create_app()

def test_reviewer_submission_status():
    with app.app_context():
        # Fetch all papers to check how many there are
        papers = Paper.query.all()
        
        print(f"Total papers found: {len(papers)}")
        
        if papers:
            # Fetch the first paper
            paper = papers[0]
            print(f"Original Status: {paper.status}")
            
            # Set the status to 'Accepted' and commit changes
            paper.status = 'Accepted'
            paper.final_copy_submitted_date = datetime.now()  # Optional: Set the final submission date
            db.session.commit()
            print(f"Updated Status: {paper.status}")
            print(f"Paper with title '{paper.title}' is now Accepted!")
            
            # Simulate the rejected case
            paper.status = 'Rejected'
            paper.rejection_reasons = "The thesis did not meet the quality standards."
            db.session.commit()
            print(f"Updated Status: {paper.status}")
            print(f"Paper with title '{paper.title}' is now Rejected!")
            
        else:
            print("No papers found for review.")

test_reviewer_submission_status()
