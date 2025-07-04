import React, { useState, useEffect } from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';

const PracticeSessionScreen = ({ route, navigation }) => {
  const { subject, difficulty, numQuestions } = route.params;
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [score, setScore] = useState(0);
  const [questions, setQuestions] = useState([]);

  useEffect(() => {
    // TODO: Fetch questions based on subject, difficulty, numQuestions
    setQuestions([
      { id: 1, question: 'What is 2 + 2?', answer: '4' },
      { id: 2, question: 'What is 5 * 5?', answer: '25' },
    ]);
  }, []);

  const handleAnswer = (isCorrect) => {
    if (isCorrect) {
      setScore(score + 1);
    }
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      navigation.navigate('SessionSummary', { score, totalQuestions: questions.length });
    }
  };

  if (questions.length === 0) {
    return (
      <View style={styles.container}>
        <Text>Loading questions...</Text>
      </View>
    );
  }

  const currentQuestion = questions[currentQuestionIndex];

  return (
    <View style={styles.container}>
      <Text style={styles.questionText}>{currentQuestion.question}</Text>
      <Button title="Correct" onPress={() => handleAnswer(true)} />
      <Button title="Incorrect" onPress={() => handleAnswer(false)} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  questionText: {
    fontSize: 20,
    marginBottom: 20,
    textAlign: 'center',
  },
});

export default PracticeSessionScreen;
