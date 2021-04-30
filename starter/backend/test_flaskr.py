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
        self.database_path = "postgres://postgres:hallo@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
            
        #create dummy question:
        self.new_question = {
            'question': 'Which stupid bird creates havoc on our balcony?',
            'answer': 'Meisi',
            'category': 1,
            'difficulty': 2
        }
        
    def tearDown(self):
        """Executed after each test"""
        pass

    def test_GET_categories_success(self):
        ''' Test Get categories '''
        res= self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']),6)
    
    def test_GET_categories_fail(self):
        res= self.client().post('/categories')
        data = json.loads(res.data)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],405)
        self.assertEqual(data['message'],'method not allowed') 
    
    ###### Test endpoint:get('/questions?page=1')
    def test_GET_questions_paginated_success(self):
        ''' Test Get questions, paginated, success '''
        res= self.client().get('/questions?page=1')
        data = json.loads(res.data)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']), 10)
        self.assertEqual(data['total_questions'],19)
        self.assertTrue(data['categories'])
        self.assertTrue(data['current_category'])   
    
    def test_GET_questions_paginated_fail_404(self):
        ''' Test Get questions, paginated, fail 404 '''
        res= self.client().get('/questions?page=100')
        data = json.loads(res.data)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],404)
        self.assertTrue(data['message'],'resource not found')
      
    ###### Test endpoint:get('/categories/${id}/questions')  
    def test_GET_questions_by_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data) 
        self.assertEqual(data['success'], True)
        # assert that there a 3 questions in category 1:
        self.assertEqual(len(data['questions']), 3)
        self.assertEqual(data['total_questions'], 3)
        self.assertEqual(data['current_category'], 1)  
    
    def test_get_questions_by_category_fail_404(self):
        ''' hit an nonexistant category index'''
        res = self.client().get('/categories/7/questions')
        data = json.loads(res.data) 
        self.assertEqual(data['success'], False) 
        self.assertEqual(res.status_code, 404)
        self.assertTrue(data['message'],'resource not found') 
        
    ###### Test endpoint:post('/questions)
    def test_add_question(self): 
        nr_questions_previous = len(Question.query.all())   
        res = self.client().post('/questions', json=self.new_question)
        nr_questions_new = len(Question.query.all())
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertEqual(nr_questions_previous + 1,nr_questions_new) 
    
    def test_add_question_fail(self): 
        res = self.client().post('/questions')
        self.assertEqual(res.status_code, 422)
    
    def test_search_questions(self): 
        print('now search:')
        res = self.client().post('/questions', json={'searchTerm':'is'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['total_questions'],8)
        self.assertTrue(data['questions'])
    
    def test_search_questions_searchTerm_nonexistent(self): 
        res = self.client().post('/questions', json={'searchTerm':'bullshit'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['total_questions'],0)
        self.assertEqual(len(data['questions']),0)
        
   ###### Test endpoint:post('/quizzes)
    def test_get_next_question(self):
       res = self.client().post('/quizzes', json={'previous_questions': [5,9], 'quiz_category': {'type': 'Art', 'id': '2'}})
       data = json.loads(res.data)
       print(data)
       self.assertEqual(res.status_code, 200)
       self.assertEqual(data['success'],True)
       self.assertEqual(data['question']['category'],2)       
    
    def test_get_next_question_case_all_categories(self):
       res = self.client().post('/quizzes', json= {'previous_questions': [], 'quiz_category': {'type': 'click', 'id': 0}})
       data = json.loads(res.data)
       self.assertEqual(res.status_code, 200)
       self.assertEqual(data['success'],True)
    
    def test_get_next_question_fail_404(self):
       res = self.client().post('/quizzes', json= {'previous_questions': [], 'quiz_category': {'type': 'click', 'id': 9}})
       data = json.loads(res.data)
       self.assertEqual(res.status_code, 400)
       self.assertEqual(data['success'],False)

    ###### Test endpoint:get('/categories/${id}')
    def test_delete_question(self):
         res = self.client().delete('/questions/20')
         data = json.loads(res.data)
         question = Question.query.filter(Question.id == 20).one_or_none()
         self.assertEqual(res.status_code, 200)
         self.assertEqual(data['success'],True)
         self.assertEqual(data['removed_id'],20)
         self.assertEqual(question, None) 
    
    def test_delete_question_fail(self):
         res = self.client().delete('/questions/200')     
         data = json.loads(res.data)
         self.assertEqual(res.status_code, 422)
         self.assertEqual(data['success'],False)
         
                   
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()