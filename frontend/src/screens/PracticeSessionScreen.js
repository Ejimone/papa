import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  TouchableOpacity, 
  StyleSheet, 
  ScrollView, 
  ActivityIndicator, 
  Alert 
} from 'react-native';
import { useSelector } from 'react-redux';
import apiClient from '../api/client';

const PracticeSessionScreen = ({ route, navigation }) => {
  const { subject, difficulty, numQuestions } = route.params || {};
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [showAnswer, setShowAnswer] = useState(false);
  const [timeStarted, setTimeStarted] = useState(Date.now());
  const user = useSelector((state) => state.auth.user);

  const fetchQuestions = async () => {
    try {
      setLoading(true);
      
      // Fetch random questions with filters
      const params = new URLSearchParams({
        count: numQuestions || 10,
      });
      
      if (subject?.id) {
        params.append('subject_ids', subject.id);
      }
      if (difficulty) {
        params.append('difficulty_levels', difficulty);
      }

      let questionsData = [];
      
      try {
        const response = await apiClient.get(`/questions/random?${params}`);
        if (response.data && response.data.length > 0) {
          questionsData = response.data;
        }
      } catch (error) {
        console.log('Random questions API failed, trying basic questions endpoint');
        try {
          // Fallback: get any available questions
          const fallbackResponse = await apiClient.get('/questions?limit=10');
          if (fallbackResponse.data && fallbackResponse.data.length > 0) {
            questionsData = fallbackResponse.data;
          }
        } catch (fallbackError) {
          console.log('Basic questions API also failed');
        }
      }
      
      if (questionsData.length > 0) {
        setQuestions(questionsData);
      } else {
        // Use sample questions for demonstration
        setQuestions([
          {
            id: 1,
            title: 'Sample Math Question',
            content: 'What is 2 + 2?',
            answer: '4',
            options: { 'A': '3', 'B': '4', 'C': '5', 'D': '6' },
            points: 1,
            question_type: 'multiple_choice',
            difficulty_level: 'easy'
          },
          {
            id: 2,
            title: 'Sample Science Question',
            content: 'What is the chemical symbol for water?',
            answer: 'H2O',
            points: 1,
            question_type: 'short_answer',
            difficulty_level: 'easy'
          }
        ]);
      }
    } catch (error) {
      console.error('Error fetching questions:', error);
      // Still provide sample questions even if there's an error
      setQuestions([
        {
          id: 1,
          title: 'Demo Question',
          content: 'This is a demo question. Upload your own questions to practice with real content!',
          answer: 'Demo Answer',
          points: 1,
          question_type: 'short_answer',
          difficulty_level: 'easy'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuestions();
  }, []);

  const handleAnswer = (userAnswer) => {
    setSelectedAnswer(userAnswer);
    setShowAnswer(true);
    
    const currentQuestion = questions[currentQuestionIndex];
    const isCorrect = userAnswer === currentQuestion.answer;
    
    if (isCorrect) {
      setScore(score + 1);
    }

    // Auto advance after 2 seconds
    setTimeout(() => {
      if (currentQuestionIndex < questions.length - 1) {
        setCurrentQuestionIndex(currentQuestionIndex + 1);
        setSelectedAnswer(null);
        setShowAnswer(false);
      } else {
        const timeSpent = Math.round((Date.now() - timeStarted) / 1000);
        navigation.navigate('SessionSummary', { 
          score, 
          totalQuestions: questions.length,
          timeSpent,
          subject: subject?.name || 'Mixed Topics'
        });
      }
    }, 2000);
  };

  const renderEmptyState = () => (
    <View style={styles.emptyContainer}>
      <Text style={styles.emptyIcon}>📝</Text>
      <Text style={styles.emptyTitle}>No Questions Available</Text>
      <Text style={styles.emptySubtitle}>
        Upload some past questions to start practicing
      </Text>
      <TouchableOpacity 
        style={styles.uploadButton} 
        onPress={() => navigation.navigate('Learn', { screen: 'Upload' })}
      >
        <Text style={styles.uploadButtonText}>Upload Questions</Text>
      </TouchableOpacity>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#3498DB" />
        <Text style={styles.loadingText}>Loading practice questions...</Text>
      </View>
    );
  }

  if (questions.length === 0) {
    return renderEmptyState();
  }

  const currentQuestion = questions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / questions.length) * 100;

  return (
    <ScrollView style={styles.container}>
      {/* Progress Header */}
      <View style={styles.progressContainer}>
        <View style={styles.progressInfo}>
          <Text style={styles.progressText}>
            Question {currentQuestionIndex + 1} of {questions.length}
          </Text>
          <Text style={styles.scoreText}>Score: {score}/{questions.length}</Text>
        </View>
        <View style={styles.progressBar}>
          <View style={[styles.progressFill, { width: `${progress}%` }]} />
        </View>
      </View>

      {/* Question Content */}
      <View style={styles.questionContainer}>
        <Text style={styles.questionTitle}>{currentQuestion.title}</Text>
        <Text style={styles.questionText}>{currentQuestion.content}</Text>
        
        {currentQuestion.points && (
          <Text style={styles.pointsText}>Points: {currentQuestion.points}</Text>
        )}
      </View>

      {/* Answer Options or Input */}
      <View style={styles.answerContainer}>
        {currentQuestion.options && typeof currentQuestion.options === 'object' ? (
          // Multiple choice question
          Object.entries(currentQuestion.options).map(([key, value]) => (
            <TouchableOpacity
              key={key}
              style={[
                styles.optionButton,
                selectedAnswer === key && styles.selectedOption,
                showAnswer && key === currentQuestion.answer && styles.correctOption,
                showAnswer && selectedAnswer === key && key !== currentQuestion.answer && styles.incorrectOption
              ]}
              onPress={() => !showAnswer && handleAnswer(key)}
              disabled={showAnswer}
            >
              <Text style={styles.optionText}>{key}. {value}</Text>
            </TouchableOpacity>
          ))
        ) : (
          // Short answer or text input
          <View style={styles.textAnswerContainer}>
            <Text style={styles.instructionText}>Think about your answer, then check:</Text>
            <TouchableOpacity
              style={[styles.revealButton, showAnswer && styles.revealButtonPressed]}
              onPress={() => setShowAnswer(true)}
              disabled={showAnswer}
            >
              <Text style={styles.revealButtonText}>
                {showAnswer ? 'Answer Revealed' : 'Reveal Answer'}
              </Text>
            </TouchableOpacity>
            
            {showAnswer && (
              <View style={styles.answerReveal}>
                <Text style={styles.answerLabel}>Correct Answer:</Text>
                <Text style={styles.answerValue}>{currentQuestion.answer}</Text>
                
                <View style={styles.selfAssessment}>
                  <Text style={styles.assessmentText}>Did you get it right?</Text>
                  <View style={styles.assessmentButtons}>
                    <TouchableOpacity
                      style={[styles.assessmentButton, styles.correctButton]}
                      onPress={() => handleAnswer(currentQuestion.answer)}
                    >
                      <Text style={styles.assessmentButtonText}>✓ Correct</Text>
                    </TouchableOpacity>
                    <TouchableOpacity
                      style={[styles.assessmentButton, styles.incorrectButton]}
                      onPress={() => handleAnswer('incorrect')}
                    >
                      <Text style={styles.assessmentButtonText}>✗ Incorrect</Text>
                    </TouchableOpacity>
                  </View>
                </View>
              </View>
            )}
          </View>
        )}
      </View>

      {/* Feedback */}
      {showAnswer && (
        <View style={styles.feedbackContainer}>
          <Text style={styles.feedbackText}>
            {selectedAnswer === currentQuestion.answer ? 
              '🎉 Correct! Well done!' : 
              '💡 Not quite right, but keep practicing!'
            }
          </Text>
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8F9FA',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F8F9FA',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#7F8C8D',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 40,
  },
  emptyIcon: {
    fontSize: 64,
    marginBottom: 20,
  },
  emptyTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 12,
    textAlign: 'center',
  },
  emptySubtitle: {
    fontSize: 16,
    color: '#7F8C8D',
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 30,
  },
  uploadButton: {
    backgroundColor: '#3498DB',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  uploadButtonText: {
    color: '#FFFFFF',
    fontWeight: '600',
    fontSize: 16,
  },
  progressContainer: {
    backgroundColor: '#FFFFFF',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#E1E8ED',
  },
  progressInfo: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  progressText: {
    fontSize: 16,
    color: '#2C3E50',
    fontWeight: '500',
  },
  scoreText: {
    fontSize: 16,
    color: '#3498DB',
    fontWeight: '600',
  },
  progressBar: {
    height: 8,
    backgroundColor: '#E1E8ED',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#3498DB',
    borderRadius: 4,
  },
  questionContainer: {
    backgroundColor: '#FFFFFF',
    margin: 16,
    padding: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  questionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 12,
  },
  questionText: {
    fontSize: 16,
    color: '#2C3E50',
    lineHeight: 24,
    marginBottom: 12,
  },
  pointsText: {
    fontSize: 14,
    color: '#3498DB',
    fontWeight: '500',
  },
  answerContainer: {
    margin: 16,
    marginTop: 0,
  },
  optionButton: {
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 8,
    borderWidth: 2,
    borderColor: '#E1E8ED',
    marginBottom: 12,
  },
  selectedOption: {
    borderColor: '#3498DB',
    backgroundColor: '#E3F2FD',
  },
  correctOption: {
    borderColor: '#27AE60',
    backgroundColor: '#D5EDDA',
  },
  incorrectOption: {
    borderColor: '#E74C3C',
    backgroundColor: '#F8D7DA',
  },
  optionText: {
    fontSize: 16,
    color: '#2C3E50',
  },
  textAnswerContainer: {
    backgroundColor: '#FFFFFF',
    padding: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  instructionText: {
    fontSize: 16,
    color: '#7F8C8D',
    textAlign: 'center',
    marginBottom: 20,
  },
  revealButton: {
    backgroundColor: '#3498DB',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 20,
  },
  revealButtonPressed: {
    backgroundColor: '#BDC3C7',
  },
  revealButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  answerReveal: {
    borderTopWidth: 1,
    borderTopColor: '#E1E8ED',
    paddingTop: 20,
  },
  answerLabel: {
    fontSize: 14,
    color: '#7F8C8D',
    marginBottom: 8,
  },
  answerValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2C3E50',
    marginBottom: 20,
    padding: 12,
    backgroundColor: '#F8F9FA',
    borderRadius: 8,
  },
  selfAssessment: {
    alignItems: 'center',
  },
  assessmentText: {
    fontSize: 16,
    color: '#2C3E50',
    marginBottom: 16,
  },
  assessmentButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  assessmentButton: {
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
    minWidth: 100,
    alignItems: 'center',
  },
  correctButton: {
    backgroundColor: '#27AE60',
  },
  incorrectButton: {
    backgroundColor: '#E74C3C',
  },
  assessmentButtonText: {
    color: '#FFFFFF',
    fontWeight: '600',
    fontSize: 14,
  },
  feedbackContainer: {
    margin: 16,
    padding: 16,
    backgroundColor: '#E8F4FD',
    borderRadius: 8,
    alignItems: 'center',
  },
  feedbackText: {
    fontSize: 16,
    color: '#2C3E50',
    textAlign: 'center',
    fontWeight: '500',
  },
});

export default PracticeSessionScreen;
