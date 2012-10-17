from flask import Flask
from flask.ext.restful import reqparse, abort, Api, Resource

app = Flask(__name__)
api = Api(app)

TODOS = [
    { 'task': 'build an API' },
    { 'task': '?????'},
    { 'task': 'profit!'},
]

# Todo
#   show a single todo item and lets you delete them
class Todo(Resource):
    def get(self, todo_id):
        if not(len(TODOS) > todo_id > 0) or TODOS[todo_id] is None:
            abort(404, message="Todo {} doesn't exist".format(todo_id))
        return TODOS[todo_id]

    def delete(self, todo_id):
        if not(len(TODOS) > todo_id > 0):
            abort(404, message="Todo {} doesn't exist".format(todo_id))
        TODOS[todo_id] = None
        return "", 204

# TodoList
#   shows a list of all todos, and lets you POST to add new tasks
parser = reqparse.RequestParser()
parser.add_argument('task', type=str)

class TodoList(Resource):
    def get(self):
        return TODOS

    def post(self):
        args = parser.parse_args()
        task = {'task': args['task']}
        TODOS.append(task)
        return task, 201

##
## Actually setup the Api resource routing here
##
api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<int:todo_id>')


if __name__ == '__main__':
    app.run(debug=True)