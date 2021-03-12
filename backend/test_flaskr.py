import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format(
                            'postgres', 'admin', 'localhost:5432',
                            self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    '''
    TEST get categories success
    '''
    def test_get_categories(self):
        # get json data from endpoint
        response = self.client().get('/categories')
        data = json.loads(response.data)

        # check response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    '''
    TEST get questions success
    '''
    def test_get_paginated_questions(self):
        # get json data from endpoint
        response = self.client().get('/questions')
        data = json.loads(response.data)

        # check response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])

    '''
    TEST get questions error
    '''
    def test_404_paginated_questions_empty(self):
        # get json data from endpoint
        response = self.client().get('/questions?page=1000')
        data = json.loads(response.data)

        # check response data
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    '''
    TEST delete question success
    '''
    def test_delete_question(self):
        # get json data from endpoint
        response = self.client().delete('/questions/3')
        data = json.loads(response.data)

        question = Question.query.filter(Question.id == 3).one_or_none()

        # check response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 3)

    '''
    TEST delete question error
    '''
    def test_422_question_deleting_fail(self):
        # get json data from endpoint
        response = self.client().post('/questions', json={})
        data = json.loads(response.data)

        question = Question.query.filter(Question.id == 0).one_or_none()

        # check response data
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable error')

    '''
    TEST post new question success
    '''
    def test_create_question(self):

        # test data for post request
        new_question = {
            'question': 'question text test',
            'answer': 'answer text test',
            'difficulty': 1,
            'category': 1,
        }

        # get json data from endpoint
        response = self.client().post('/questions', json=new_question)
        data = json.loads(response.data)

        question = Question.query.filter(Question.id == 1).one_or_none()

        # check response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(data['question_created'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    '''
    TEST post new questions error
    '''
    def test_422_question_creation_fail(self):
        # get json data from endpoint
        response = self.client().post('/questions', json={})
        data = json.loads(response.data)

        question = Question.query.filter(Question.id == 1).one_or_none()

        # check response data
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable error')

    '''
    TEST search questions success
    '''
    def test_questions_search(self):
        # get json data from endpoint
        response = self.client().post('/questions', json={
                                        'searchTerm': 'Hematology'})
        data = json.loads(response.data)

        # check response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))

    '''
    TEST search questions error
    '''
    def test_404_questions_search_empty(self):
        # get json data from endpoint
        response = self.client().post('/questions', json={
                                        'searchTerm': 'QuestionNotFound'})
        data = json.loads(response.data)

        # check response data
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    '''
    TEST questions by category success
    '''
    def test_get_questions_by_category(self):
        # get json data from endpoint
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

        # check response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertEqual(data['current_category'], 'Science')

    '''
    TEST questions by category error
    '''
    def test_422_questions_by_category_fail(self):
        # get json data from endpoint
        response = self.client().get('/categories/1000/questions')
        data = json.loads(response.data)

        # check response data
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable error')

    '''
    TEST get quiz questions success
    '''
    def test_get_quiz_questions(self):
        # get json data from endpoint
        response = self.client().post('/quizzes', json={
                                        'previous_questions': [],
                                        'quiz_category': {
                                            'type': 'Science', 'id': '1'}})
        data = json.loads(response.data)

        # check response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['category'], 1)

    '''
    TEST get quiz questions error
    '''
    def test_422_quiz_questions_fail(self):
        # get json data from endpoint
        response = self.client().post('/quizzes', json={})
        data = json.loads(response.data)

        # check response data
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable error')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
