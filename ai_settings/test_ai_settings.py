import unittest
from datetime import datetime, time
from ai_settings import app, db, AIService, AITemplate, TrainingData, FallbackRule, OfficeHours

class TestAISettings(unittest.TestCase):
    def setUp(self):
        # Create a test database
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_ai_settings.db'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
            self.service = AIService()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_template_creation(self):
        with app.app_context():
            # Create template
            template = AITemplate(
                template_type='confirmation',
                subject='Shift Confirmation',
                content='Your shift has been confirmed for {{date}}'
            )
            db.session.add(template)
            db.session.commit()
            
            # Test retrieval
            retrieved = self.service.get_template('confirmation')
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved.template_type, 'confirmation')

    def test_training_data(self):
        with app.app_context():
            # Create training data
            training = TrainingData(
                question='What are the rates?',
                response='Our rates start at $20/hour',
                category='rates'
            )
            db.session.add(training)
            db.session.commit()
            
            # Test retrieval
            response = self.service.get_training_response('rates')
            self.assertIsNotNone(response)
            self.assertEqual(response, 'Our rates start at $20/hour')

    def test_fallback_rules(self):
        with app.app_context():
            # Create fallback rule
            rule = FallbackRule(
                condition='confidence_score < 0.7',
                action='escalate_to_human',
                priority=10
            )
            db.session.add(rule)
            db.session.commit()
            
            # Test fallback
            action = self.service.should_fallback(0.6)
            self.assertEqual(action, 'escalate_to_human')
            
            action = self.service.should_fallback(0.8)
            self.assertIsNone(action)

    def test_office_hours(self):
        with app.app_context():
            # Create office hours
            hours = OfficeHours(
                day_of_week=0,  # Monday
                start_time=time(9, 0),
                end_time=time(17, 0),
                timezone='UTC'
            )
            db.session.add(hours)
            db.session.commit()
            
            # Test office hours
            self.assertFalse(self.service.is_within_office_hours())  # Current time is not considered

if __name__ == '__main__':
    unittest.main()
