import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
        response.headers.add('Access-Control-Allow-Headers','Content-Type')
        response.headers.add('Access-Control-Allow-Methods','GET,POST,PATCH,DELETE')
        response.headers.add('Access-Control-Allow-Origin','*')
        return response
  
  def paginate_questions(request, selection):
      page = request.args.get('page', 1, type=int)
      start =  (page - 1) * QUESTIONS_PER_PAGE
      end = start + QUESTIONS_PER_PAGE
      questions = [question.format() for question in selection]
      current_questions = questions[start:end]
      return current_questions 
    
  def psql_obj_as_list_dict(selections):
      selection_list_of_dict = [selection.format() for selection in selections]
      print(selection_list_of_dict)
      return selection_list_of_dict
    
  def get_categories_object():
      categories = Category.query.all()
      categories_dict = [category.format() for category in categories]
      categories_formatted = {category['id']:category['type'] for category in categories_dict}
      
      return categories_formatted

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_all_categories():
        try:
          categories_formatted = get_categories_object()
          return jsonify({
            'success': True,
            'categories': categories_formatted 
          })
        except:
            abort(405)
          
  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods = ['GET']) #with page arguement
  def get_questions_paginated():
        all_questions = Question.query.order_by(Question.id).all()
        show_questions = paginate_questions(request,all_questions)
        categories_formatted = get_categories_object()
        
        if len(show_questions) == 0:
          abort(404)
          
        return jsonify({
          'success': True,
          'questions': show_questions,
          'total_questions': len(all_questions),
          'categories': categories_formatted,
          'current_category': 'History'
        })

      
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>', methods=['DELETE'])
  def delete_questions(id):
      try:
        question = Question.query.filter(Question.id == id).one_or_none()
        if question is None:
              abort(404)
        question.delete()
        return jsonify({
           'success': True,
           'removed_id': id
        })
      except:
        abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions',methods=['POST'])
  def add_new_questions():        
      try:
        body = request.get_json()
        search = body.get('searchTerm', None)
        #depending on the body of the request:
        if search != None:
            #a) search for term
            print(search)
            questions = Question.query.order_by(Question.id).filter(Question.question.ilike('% {} %'.format(search)))
            questions_pagenated = paginate_questions(request,questions)
            return jsonify({
              'success': True,
              'questions': questions_pagenated,
              'total_questions': len(questions_pagenated),
              'current_category': 'History'        
            })
              
        else:
            # b) add new question
            question = Question(
              body.get('question', None), 
              body.get('answer', None),
              body.get('category', None),
              body.get('difficulty', None)
            )
            #FERFI: wie none abfragen?
            question.insert()
            print(question.format())

            return jsonify({
              'success': True         
            })
      except:
        abort(422)
      


  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
   
  @app.route('/categories/<int:id>/questions', methods = ['GET'])
  def get_questions_for_specific_category(id):
        #print(id)
           current_category = Category.query.filter(Category.id==id).one_or_none()
           if current_category is None:
              abort(404)
           questions=Question.query.order_by(Question.id).filter(Question.category == id).all()
           if len(questions) == 0:
              abort(404)

           return jsonify({
             'success' : True,
             'questions': psql_obj_as_list_dict(questions),
             'total_questions': len(questions),
             'current_category': current_category.id
             })

        

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_next_question():
      try:
        body = request.get_json()
        print(body)
        quizCategory= body.get('quiz_category', None)
        id_used_questions= body.get('previous_questions', None)
        if quizCategory['id'] != 0:
           # get only questions of the choosen quiz_category
           ids_all_questions = [q.id for q in Question.query.filter(Question.category==quizCategory['id']).all()]
        else:
           # get all ids
           ids_all_questions = [q.id for q in Question.query.all()] 
        # find all ids, which are not in id_used_questions
        id_not_yet_used_questions = [id for id in ids_all_questions if id not in id_used_questions] 
        question = Question.query.filter(Question.id == random.choice(id_not_yet_used_questions)).all() 
        return jsonify({
          'success': True,
          'question': psql_obj_as_list_dict(question)[0]
          
        })
      except:
        abort(400)
  
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''



  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400
    
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False, 
      'error': 404,
      'message': 'resource not found'
      }), 404 
    
  @app.errorhandler(405)
  def bad_request(error):
    return jsonify({
      'success': False, 
      'error': 405,
      'message': 'method not allowed'
      }), 405
    
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False, 
      'error': 422,
      'message': 'unprocessable entity'
      }), 422
    
  @app.errorhandler(500)
  def unprocessable(error):
    return jsonify({
      'success': False, 
      'error': 500,
      'message': 'internal sever error'
      }), 500
  return app

    