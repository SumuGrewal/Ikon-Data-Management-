from IkonConveyancing.app import createApp, db
from IkonConveyancing.app.models import User

app = createApp()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

if __name__ == '__main__':
    app.run(debug=True)