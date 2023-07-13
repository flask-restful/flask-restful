from flask import Flask
from flask_restful import Resource, Api, reqparse, abort

app = Flask(__name__)
api = Api(app)

todos = {
   1: {"task":"Daily Standup with Team", "Meetings Agenda": "Catch up with team"},
   2: {"task":"One-on-One meeting with Manager", "Meeting Agenda": "Layout the business plan for next PI."},
   3: {"task":"Team lunch with Team", "Meeting Agenda": "Daily get togethor and fun interactions"}
}

todo_post_args = reqparse.RequestParser()
todo_post_args.add_argument("task", type=str, help="Task is required", required=True)
todo_post_args.add_argument("Meetings Agenda", type=str, help="Agenda is required", required=True)

todo_put_args = reqparse.RequestParser()
todo_put_args.add_argument("task", type=str)
todo_put_args.add_argument("Meetings Agenda", type=str)

class TodoList(Resource):
   def get(Self):
      return todos


class ToDo(Resource):
   def get(self, todo_id):
      return todos[todo_id]
   
   def post(self, todo_id):
      args = todo_post_args.parse_args()
      if todo_id in todos:
         abort(409, "Task Id already taken")
      todos[todo_id] = {"task": args["task"], "Meetings Agenda": args["Meetings Agenda"]}
      return todos[todo_id]
   
   def put(self, todo_id):
      args = todo_put_args.parse_args()
      if todo_id not in todos:
         abort(404, message ="Todo not found. Cannot update")
      if args['task']:
         todos[todo_id]['task'] = args["task"]
      if args['Meetings Agenda']:
         todos[todo_id]['Meetings Agenda'] = args["Meetings Agenda"]
      return todos[todo_id]
   
   
   def delete(self, todo_id):
      del todos[todo_id]
      return todos
   
api.add_resource(ToDo, '/todos/<int:todo_id>')
api.add_resource(TodoList, '/todos')

if __name__ == '__main__':
   app.run(debug=True)