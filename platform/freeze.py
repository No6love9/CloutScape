from flask_frozen import Freezer
from app import create_app
import os

app = create_app()
# Output to a 'build' directory outside the platform folder
app.config['FREEZER_DESTINATION'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '../build'))
# Ensure relative URLs for static hosting
app.config['FREEZER_RELATIVE_URLS'] = True

freezer = Freezer(app)

if __name__ == '__main__':
    print(f"Freezing app to: {app.config['FREEZER_DESTINATION']}")
    freezer.freeze()
    print("Freeze complete!")
