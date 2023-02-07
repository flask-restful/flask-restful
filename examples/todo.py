from flask import Flask
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__)
api = Api(app)

TODOS = {
    'todo1': {'task': 'build an API'},
    'todo2': {'task': '?????'},
    'todo3': {'task': 'profit!'},
}


def abort_if_todo_doesnt_exist(todo_id):
    """
    Function to raise a 404 error if the requested todo item doesn't exist.
    """
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist".format(todo_id))


parser = reqparse.RequestParser()
parser.add_argument('task', help='The task details')


class Todo(Resource):
    """
    Todo Resource.
    Allows for operations on a single todo item.
    """

    def get(self, todo_id):
        """
        Get a single todo item by its id.
        """
        abort_if_todo_doesnt_exist(todo_id)
        return TODOS[todo_id]

    def delete(self, todo_id):
        """
        Delete a single todo item by its id.
        """
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return '', 204

    def put(self, todo_id):
        """
        Update a single todo item by its id.
        """
        args = parser.parse_args()
        task = {'task': args['task']}
        TODOS[todo_id] = task
        return task, 201


class TodoList(Resource):
    """
    TodoList Resource.
    Allows for operations on the whole list of todo items.
    """

    def get(self):
        """
        Get the whole list of todo items.
        """
        return TODOS

    def post(self):
        """
        Add a new todo item to the list.
        """
        args = parser.parse_args()
        todo_id = 'todo%d' % (len(TODOS) + 1)
        TODOS[todo_id] = {'task': args['task']}
        return TODOS[todo_id], 201


# Actually setup the Api resources routing here - An API resource and its endpoint
# Notice we determine the parameter type of todo_id to a string
api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<string:todo_id>')


if __name__ == '__main__':
    app.run(debug=True)
