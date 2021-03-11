import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import random
import sys

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(questions_rows, page_index = 1):
    start = (page_index-1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in questions_rows]
    current_questions = questions[start:end]
    return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  # Set up CORS. Allow '*' for origins
  CORS(app, resources={'/' : {'origins': '*'}})
  
  # The after_request decorator to set Access-Control-Allow
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods','GET, POST, DELETE')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

  '''
  Default route
  '''
  @app.route('/')
  def index(): 
    return jsonify({'Project': 'Trivia API'})  

  '''
  Endpoint to handle GET requests for all available categories. 
  ''' 
  @app.route('/categories')
  @cross_origin()
  def get_categories():
    try:
      categories_rows = Category.query.order_by(Category.id).all()
      # convert data to dictionary
      categories_dict = {} 
      for category in categories_rows:
        categories_dict[category.id] = category.type

      # return data
      return jsonify({
        'success': True,
        'categories': categories_dict
      })

    except:
      # exception details
      print('\n * Error:\n',sys.exc_info(),'\n')
      # Server error
      abort(500)

  '''
  Endpoint to handle GET requests for questions
  '''
  @app.route('/questions')
  @cross_origin()
  def get_paginated_questions():
    try:
      categories_rows = Category.query.order_by(Category.id).all()
      # convert data to dictionary
      categories_dict = {}
      for category in categories_rows:
        categories_dict[category.id] = category.type

      questions_rows = Question.query.order_by(Question.id).all()
      page_index = request.args.get('page', 1, type=int)
      questions_paginated = paginate_questions(questions_rows,page_index)
      
      if len(questions_paginated) == 0:
        # Empty result
        abort(404)

      # return data  
      return jsonify({
        'success': True,            
        'questions' : questions_paginated,            
        'total_questions': len(questions_rows),
        'categories' : categories_dict,
        'current_category' : None
      })

    except:
      # exception details
      print('\n * Error:\n',sys.exc_info(),'\n')
      # Server error
      abort(500)

  '''
  Endpoint to DELETE question using a question ID
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  @cross_origin()
  def delete_question(question_id):
    try:
      question = Question.query.filter_by(id=question_id).one_or_none()

      if question is None:
        # Unprocessable error
        abort(422)

      question.delete()

      return jsonify({
        'success': True,
        'deleted': question_id
      })

    except:
      # exception details
      print('\n * Error :\n',sys.exc_info(),'\n')
      # Server error
      abort(500)

  '''
  Endpoint to get questions based on a search term.
  and to POST a new question
  '''
  @app.route('/questions', methods=['POST'])
  @cross_origin()
  def post_search_or_post_new_question():
    request_json = request.get_json()

    try:
      search_term = request_json.get('searchTerm')
      if search_term is not None:

        '''
        search for question
        '''
        questions_search = Question.query.filter(Question.question.ilike('%' + search_term + '%')).all()

        if len(questions_search) == 0:
          # Empty result
          abort(404)

        questions_paginated = paginate_questions(questions_search)

        # return data
        return jsonify({
          'success': True,
          'questions': questions_paginated,
          'total_questions': len(questions_search)
        })

      else:

        '''
        create new question
        '''
        new_question_question = request_json.get('question')
        new_question_answer = request_json.get('answer')
        new_question_difficulty = request_json.get('difficulty')
        new_question_category = request_json.get('category')

        # check the values are present
        if new_question_question is None or new_question_answer is None or new_question_difficulty is None or new_question_category is None:
          # Unprocessable error
          abort(422)

        new_question = Question(
          question=new_question_question, 
          answer=new_question_answer,
          difficulty=new_question_difficulty, 
          category=new_question_category
        )
        new_question.insert()

        questions_rows = Question.query.order_by(Question.id).all()
        total_questions_num = len(questions_rows)
        last_page_index = (total_questions_num // QUESTIONS_PER_PAGE) + 1
        questions_paginated = paginate_questions(questions_rows,last_page_index)

        # return data
        return jsonify({
          'success': True,
          'created': new_question.id,
          'question_created': new_question.question,
          'questions': questions_paginated,
          'total_questions': total_questions_num
        })

    except:
      # exception details
      print('\n * Error:\n',sys.exc_info(),'\n')
      # Server error
      abort(500)
        
 
  '''
  Endpoint to get questions based on category
  '''
  @app.route('/categories/<int:category_id>/questions')
  @cross_origin()
  def get_questions_by_category(category_id):

    try:

      # Get questions of category id
      current_category = Category.query.filter_by(id=category_id).one_or_none()

      # check the values are present
      if current_category is None:
        # Unprocessable error
        abort(422)

      questions_by_category = Question.query.filter_by(category=current_category.id).all()

      if len(questions_by_category) == 0:
        # Empty result
        abort(404)

      questions_paginated = paginate_questions(questions_by_category)

      # return data
      return jsonify({
        'success': True,
        'questions': questions_paginated,
        'total_questions': len(questions_by_category),
        'current_category': current_category.type
      })

    except:
      # exception details
      print('\n * Error:\n',sys.exc_info(),'\n')
      # Server error
      abort(500)  

  '''
  Endpoint to get questions to play the quiz
  '''
  @app.route('/quizzes', methods=['POST'])
  @cross_origin()
  def get_quiz_questions():

    # get list of previous questions id and quiz question category
    request_json = request.get_json()
    previous_questions = request_json.get('previous_questions')
    quiz_category = request_json.get('quiz_category')

    # check the values are present
    if quiz_category is None or previous_questions is None:
      # Unprocessable error
      abort(422)

    # if category id equal zero that means get all questions
    if (quiz_category['id'] == 0):
      quiz_questions = Question.query.all()
    else:
      quiz_questions = Question.query.filter_by(category=quiz_category['id']).all()

    # no new questions for showing, end quiz
    if (len(quiz_questions) == len(previous_questions)):
      return jsonify({
          'success': True
        })

    def generate_random_question():
      random_index = random.randrange(0, len(quiz_questions), 1)
      return quiz_questions[random_index]

    # get new random question
    current_question = generate_random_question()
    while (current_question.id in previous_questions):
      current_question = generate_random_question()

    # return data
    return jsonify({
      'success': True,
      'question': current_question.format()
    })

  '''
  Error handlers for expected errors 
  '''
  # catch bad request 400
  @app.errorhandler(400)
  def catch_bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': 'Bad request error'
    }), 400

  # catch not found error 404
  @app.errorhandler(404)
  def catch_not_found(error):
    print('### error ', error)
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Resource not found'
    }), 404

  # catch Method not allowed 405
  @app.errorhandler(405)
  def catch_method_not_allowed(error):
    return jsonify({
      "success": False, 
      "error": 405,
      "message": "Method not allowed"
    }), 405

  # catch unprocessable error 422
  @app.errorhandler(422)
  def catch_unprocessable(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'Unprocessable error'
    }), 422
  
  # catch server error 500
  @app.errorhandler(500)
  def catch_server_error(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': 'Internal server error has been occured'
    }), 500

  return app

    